#!/usr/bin/env python
import os
from pathlib import Path

import markdown


def convert_md_to_html(md_content: str, title_fallback: str) -> str:
    """
    Converte markdown in HTML e lo wrappa in un semplice template HTML.
    Cerca il primo heading come titolo, altrimenti usa il fallback.
    """
    lines = md_content.splitlines()
    title = title_fallback
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            break

    html_body = markdown.markdown(
        md_content,
        extensions=["extra", "tables", "toc"],
        output_format="html5",
    )

    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      max-width: 900px;
      margin: 2rem auto;
      padding: 0 1rem;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 1rem 0;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 0.5rem;
      vertical-align: top;
    }}
    th {{
      background: #f5f5f5;
    }}
    code {{
      background: #f4f4f4;
      padding: 0.1rem 0.2rem;
      border-radius: 3px;
      font-size: 0.95em;
    }}
    a {{
      color: #0366d6;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
{html_body}
</body>
</html>
"""
    return template


def rewrite_links(md_content: str) -> str:
    """
    Riscrive i link che puntano a .md in link a .html.
    Esempio: (./season1.md) -> (season1.html)
    Esempio: (season1.md) -> (season1.html)
    Esempio: (./README.md) -> (index.html)
    """
    content = md_content

    # README.md -> index.html
    content = content.replace("(./README.md)", "(index.html)")
    content = content.replace("(README.md)", "(index.html)")

    # seasonX.md -> seasonX.html (gestione semplice)
    # Se in futuro avrai altri file .md qui, puoi raffinare con regex.
    content = content.replace(".md)", ".html)")

    return content


def main():
    repo_root = Path(".").resolve()
    seasons_dir = repo_root / "seasons"
    output_dir = repo_root / "site"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not seasons_dir.is_dir():
        raise SystemExit("Expected 'seasons/' directory at repo root.")

    for md_file in seasons_dir.glob("*.md"):
        name = md_file.name

        # Leggi contenuto markdown
        md_text = md_file.read_text(encoding="utf-8")

        # Riscrivi i link .md -> .html
        md_text = rewrite_links(md_text)

        # Determina output filename
        if name.lower() == "readme.md":
            out_name = "index.html"
        else:
            out_name = f"{md_file.stem}.html"

        out_path = output_dir / out_name

        html = convert_md_to_html(md_text, title_fallback=md_file.stem)
        out_path.write_text(html, encoding="utf-8")
        print(f"Generated {out_path.relative_to(repo_root)}")

    print("All pages generated into 'site/' directory.")


if __name__ == "__main__":
    main()
