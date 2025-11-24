# Contributing Guidelines

Thank you for your interest in contributing to the **Buffy the Vampire Slayer Episode Importance Guide** (and its future companion project for *Angel*).  
This project aims to provide a clear, structured, and community-driven reference for new viewers and rewatchers to understand which episodes matter most in terms of continuity — without making value judgments about their artistic quality.

Below are the guidelines and expectations for contributors.

---

## 📚 Philosophy of the Project

This guide classifies episodes based on their **relevance to the main storyline** using four categories:

- **FONDAMENTAL**
- **IMPORTANT**
- **DISPENSABLE**
- **FILLER**

> **Important:** These categories **do not represent a judgment of quality**.  
> Some non-FONDAMENTAL episodes (e.g. *S04E10 – “Hush”*) are among the best of the entire series.

The goal is clarity and consistency — not ranking the show.

---

## 🧭 How to Contribute

We welcome contributions of all types:

- Adding new season files  
- Improving descriptions  
- Fixing typos or formatting  
- Updating documentation  
- Improving workflows and automation  
- Discussing or refining episode importance levels  

All contributions must go through a **Pull Request (PR)**.  
Direct commits to the `main` branch are disabled.

---

## 🌿 PR Workflow

1. Fork the repository (if you are not a maintainer).
2. Create a new branch for your changes.
3. Make your edits following the formatting rules.
4. Open a Pull Request using the supplied PR template.
5. Ensure all automated checks pass (formatting, lint, etc.).
6. Engage in any discussion or requested revisions.
7. Once approved, your PR will be merged by a maintainer.

---

## 🌱 Branch Naming Convention

Branches should follow this pattern:


### Example types:
- `content/` — changes to episode tables, descriptions, season files  
- `docs/` — changes to README, CONTRIBUTING, etc.  
- `ci/` — updates to GitHub Actions, validation workflows  
- `meta/` — templates, governance, repo structure changes  
- `chore/` — small cleanups, refactors, renames  

### Example names:
- `content/buffy-s03-update-descriptions`
- `content/buffy-s05-importance-adjustments`
- `docs/readme-improvements`
- `ci/validate-pr-formatting`

This naming scheme helps maintain clarity and avoids repository chaos.

---

## 🔥 Changing an Episode’s Importance Level

Changes to an episode’s classification (FONDAMENTAL, IMPORTANT, etc.) are **sensitive**, since they can be subjective.

To prevent conflicts or arbitrary changes:

### Requirements:
- Include a **clear justification** in the PR body.
- The PR must be tagged with the `importance-change` label.
- The PR cannot be merged without **at least two approvals**.
- Reviewers may request discussion via comments or separate Issues.

This ensures classification changes remain collaborative and community-driven.

---

## 🧩 Formatting Rules

### Season Files

Each season file should contain:

- A brief overview of the main arcs (1–3 short paragraphs).
- A Markdown table with the following columns:

  | Code | Title | Importance | Description | Key Story Notes |

  - **Code** – Episode code (e.g., `S03E14`)  
  - **Title** – Episode title  
  - **Importance** – One of:
    - `FONDAMENTAL`
    - `IMPORTANT`
    - `DISPENSABLE`
    - `FILLER`
  - **Description** – A short (1–2 lines), neutral summary of the episode.  
  - **Key Story Notes** – A richer field used to capture anything that matters for long-term continuity, such as:
    - introduction of recurring or important characters  
    - lore, world-building, and prophecies that return later  
    - relationship developments and emotional turning points  
    - events that are referenced again in future seasons  

This column can be **longer than the description** and may mention connections to later episodes (e.g. *“This becomes relevant again in S02E17”*).


Table columns must remain consistent across seasons.

### Descriptions

- Keep them concise and neutral (1–2 lines).  
- Focus on what happens in the episode, not whether it is “good” or “bad”.  
- Avoid spoilers that go far beyond the episode itself.  
- No personal commentary (e.g., “this episode is boring/great”).

### Key Story Notes

The **Key Story Notes** column is designed to help viewers who skip non-essential episodes still understand:

- who key characters are and where they came from  
- why certain relationships exist or evolve in a given way  
- how prophecies, artifacts, or lore threads were first introduced  
- which events will later be referenced as part of character development or world-building  

Guidelines:

- It’s acceptable for this field to be **more detailed (3–5 lines)** if needed.  
- You may reference future episodes explicitly (e.g., *“This detail is referenced again in S05E13”*).  
- Keep the tone factual and respectful; no subjective reviews.  
- Focus on information that matters for understanding future plot points or emotional beats.


### Metadata and Structure
- Do not rename files without good reason.  
- Keep paths consistent (e.g., `seasons/season3.md`).  

---

## 🤝 Community Behavior Guidelines

We expect contributors to:
- Be respectful and constructive  
- Avoid personal attacks or sarcasm  
- Stay on topic in PRs and Issues  
- Assume good intentions  
- Welcome differing opinions about episode importance  

This is a fandom project — let’s keep it fun and collaborative.

---

## 🧪 Automated Checks (Current & Future)

This repository may include GitHub Actions that validate:
- File formatting  
- Table structure  
- Presence of forbidden language (insults, hate speech, etc.)  
- (Future) AI-assisted content review  

Contributors should ensure all checks pass before requesting review.

---

## 🛡 Maintainers Responsibilities

Maintainers are expected to:
- Monitor PRs and Issues  
- Ensure respectful discussion  
- Enforce importance-change rules  
- Maintain project consistency  
- Merge only after sufficient review  
- Update documentation when the project evolves  

---

## 💬 Need Help?

Open an Issue for:
- Questions about contributing  
- Proposals for new features  
- Clarification about episode importance  
- Discussion about contentious episodes  

We’re happy to help!

---

Thank you for contributing — whether it’s a typo fix or a complex classification discussion,  
you’re helping build the most comprehensive Buffy + Angel continuity guide online.
