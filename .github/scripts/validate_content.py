#!/usr/bin/env python
import os
import sys
import json
import subprocess
from pathlib import Path

from openai import OpenAI

client = OpenAI()  # usa OPENAI_API_KEY dall'env


def get_changed_files():
    """
    Restituisce la lista dei file modificati nella PR
    rispetto al branch base (es: main).
    """
    base_ref = os.environ.get("GITHUB_BASE_REF") or "main"
    base = f"origin/{base_ref}"

    # Lista file cambiati tra base e HEAD
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
    - in particolare seasons/ e README/CONTRIBUTING, ecc.
    """
    repo_root = Path(".").resolve()
    relevant = {}

    for f in files:
        path = repo_root / f
        if not path.is_file():
            continue

        # Consideriamo solo markdown
        if not f.lower().endswith(".md"):
            continue

        # Siamo interessati principalmente a:
        # - seasons/*.md
        # - README.md
        # - CONTRIBUTING.md
        # - .github/pull_request_template.md
        if (
            f.startswith("seasons/")
            or f in ("README.md", "CONTRIBUTING.md")
            or f.startswith(".github/")
        ):
            text = path.read_text(encoding="utf-8", errors="ignore")
            relevant[f] = text

    return relevant


def build_prompt(files_content: dict) -> str:
    """
    Costruisce il prompt per l'AI, includendo:
    - contesto del progetto
    - linee guida di formato
    - linee guida di comportamento
    - contenuti modificati
    """
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
        # Limita dimensione per sicurezza (ma di solito i file sono piccoli)
        if len(content) > 15000:
            content_snippet = content[:15000]
            parts.append(content_snippet + "\n\n[TRUNCATED]")
        else:
            parts.append(content)

    return "\n".join(parts)


def call_openai(prompt: str):
    """
    Chiama OpenAI Responses API e si aspetta come output
    una stringa JSON valida, secondo le istruzioni nel prompt.
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
        # In caso di errore API, meglio fallire la build per sicurezza
        print("Error calling OpenAI API:", e)
        sys.exit(1)

    ok = result.get("ok", False)
    violations = result.get("violations", [])

    if not violations:
        print("✅ AI validation: no issues reported.")
    else:
        print("⚠️ AI validation reported the following issues:")
        for v in violations:
            print(
                f"- [{v.get('severity','?').upper()}] {v.get('type','?')} "
                f"in {v.get('file','?')}: {v.get('message','')}"
            )
            suggestion = v.get("suggestion")
            if suggestion:
                print(f"  Suggestion: {suggestion}")

    if not ok:
        print("\n❌ Failing CI because of one or more ERROR-level violations.")
        sys.exit(1)

    print("\n✅ CI passed: only warnings or no violations.")
    sys.exit(0)


if __name__ == "__main__":
    main()
