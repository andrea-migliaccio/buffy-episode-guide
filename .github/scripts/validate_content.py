#!/usr/bin/env python
import os
import sys
import json
import subprocess
from pathlib import Path

import requests
from openai import OpenAI

client = OpenAI()  # usa OPENAI_API_KEY dall'env


def get_changed_files():
    """
    Restituisce la lista dei file modificati nella PR
    rispetto al branch base (es: main).
    """
    base_ref = os.environ.get("GITHUB_BASE_REF") or "main"
    base = f"origin/{base_ref}"

    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    return files


def load_relevant_files(files):
    """
    Filtra e carica solo i file che ci interessano:
    - Markdown (.md)
    - in particolare seasons/ e file di doc/templating.
    """
    repo_root = Path(".").resolve()
    relevant = {}

    for f in files:
        path = repo_root / f
        if not path.is_file():
            continue

        if not f.lower().endswith(".md"):
            continue

        if (
            f.startswith("seasons/")
            or f in ("README.md", "CONTRIBUTING.md")
            or f.startswith(".github/")
        ):
            text = path.read_text(encoding="utf-8", errors="ignore")
            relevant[f] = text

    return relevant


def build_prompt(files_content: dict) -> str:
    guidelines = """
You are an automated reviewer for a public GitHub repository that contains
episode guides for "Buffy the Vampire Slayer" (and in the future, "Angel").

Your job is to validate ONLY the *proposed changes* (the current state of the files),
checking for BOTH:

1) STRUCTURE & FORMAT
   - Season files are Markdown with:
     - A short overview section.
     - An episode table with columns:
       | Code | Title | Importance | Description |
   - The "Importance" column MUST use ONLY:
     - FONDAMENTAL
     - IMPORTANT
     - DISPENSABLE
     - FILLER
   - Descriptions should be short (1–2 lines).
   - No obviously broken tables (missing pipes, header/rows mismatch, etc).

2) CONTENT & CODE OF CONDUCT
   - No insults, hate speech, personal attacks or toxicity.
   - No off-topic content (e.g. spam, self-promotion, ads, unrelated rants).
   - No explicit sexual content or slurs.
   - Tone should be neutral and descriptive, not a subjective review.
   - Descriptions should focus on plot, continuity relevance, and main themes.

You are NOT judging whether episodes are good or bad; you only enforce structure
and respectful, relevant content.

Return a JSON object with this exact structure:

{
  "ok": true or false,
  "violations": [
    {
      "file": "<filename>",
      "type": "structure" or "content",
      "severity": "warning" or "error",
      "message": "<short explanation>",
      "suggestion": "<short, concrete suggestion to fix>"
    },
    ...
  ]
}

Rules for ok:
- "ok" must be false if there is ANY violation with severity "error".
- If there are only minor issues, you may use severity "warning" and set ok=true.

Be strict about:
- Importance values being in the allowed set.
- Obvious disrespectful or off-topic content.

Now you will receive a list of files and their full updated contents.
Analyze ONLY those contents.
"""

    parts = [guidelines.strip(), "\n\nCHANGED FILES:\n"]
    for name, content in files_content.items():
        parts.append(f"\n=== FILE: {name} ===\n")
        if len(content) > 15000:
            parts.append(content[:15000] + "\n\n[TRUNCATED]")
        else:
            parts.append(content)

    return "\n".join(parts)


def call_openai(prompt: str):
    """
    Chiama OpenAI Responses API e si aspetta un JSON valido come output.
    """
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )
    text = response.output_text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("Model did not return valid JSON:")
        print(text)
        raise


def get_pr_context():
    """
    Legge il file evento di GitHub per recuperare:
    - owner
    - repo
    - numero della PR
    """
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repo_full = os.environ.get("GITHUB_REPOSITORY", "")
    if not event_path or not repo_full:
        print("Missing GITHUB_EVENT_PATH or GITHUB_REPOSITORY env vars.")
        return None, None, None

    owner, repo = repo_full.split("/", 1)

    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    pr_number = event.get("number")  # per eventi pull_request

    return owner, repo, pr_number


def post_github_comment(body: str):
    """
    Crea un commento sulla Pull Request usando il GITHUB_TOKEN.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("No GITHUB_TOKEN available; cannot post PR comment.")
        return

    owner, repo, pr_number = get_pr_context()
    if not (owner and repo and pr_number):
        print("Could not determine PR context; skipping comment.")
        return

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }
    data = {"body": body}

    resp = requests.post(url, headers=headers, json=data, timeout=10)
    if resp.status_code >= 300:
        print("Failed to post PR comment:", resp.status_code, resp.text)
    else:
        print("Posted AI validation comment to PR.")


def format_violations_markdown(violations):
    """
    Format violations as a single Markdown comment.
    """
    if not violations:
        return "✅ AI validation: no issues found."

    lines = []
    lines.append("## 🤖 AI Content & Structure Validation\n")
    lines.append(
        "The AI validator found the following issues in the modified files:\n"
    )

    for v in violations:
        file = v.get("file", "?")
        vtype = v.get("type", "?")
        severity = v.get("severity", "?").upper()
        message = v.get("message", "")
        suggestion = v.get("suggestion", "")

        lines.append(f"- **[{severity}]** `{file}` – *{vtype}*")
        if message:
            lines.append(f"  - **Issue:** {message}")
        if suggestion:
            lines.append(f"  - **Suggestion:** {suggestion}")

    lines.append("\n> This comment was generated automatically by the AI PR validator.")
    return "\n".join(lines)


def main():
    changed_files = get_changed_files()
    files_content = load_relevant_files(changed_files)

    if not files_content:
        print("No relevant markdown files changed. Skipping AI validation.")
        sys.exit(0)

    prompt = build_prompt(files_content)

    try:
        result = call_openai(prompt)
    except Exception as e:
        print("Error calling OpenAI API:", e)
        # in caso di errore API falliamo la CI per sicurezza
        sys.exit(1)

    ok = result.get("ok", False)
    violations = result.get("violations", [])

    if not violations:
        print("✅ AI validation: no issues reported.")
    else:
        print("⚠️ AI validation reported the following issues:")
        for v in violations:
            print(
                f"[{v.get('severity','?').upper()}] {v.get('type','?')} "
                f"in {v.get('file','?')}: {v.get('message','')}"
            )
            suggestion = v.get("suggestion")
            if suggestion:
                print(f"  Suggestion: {suggestion}")

        # Crea un commento sulla PR con tutte le violazioni
        comment_body = format_violations_markdown(violations)
        post_github_comment(comment_body)

    if not ok:
        print("\n❌ Failing CI because of one or more ERROR-level violations.")
        sys.exit(1)

    print("\n✅ CI passed: only warnings or no violations.")
    sys.exit(0)


if __name__ == "__main__":
    main()
