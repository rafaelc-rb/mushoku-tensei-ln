"""
Extrai o texto de um PDF (versão em inglês) agrupado por capítulo, para
servir de base à tradução manual (via LLM, um capítulo por vez).

Detecta o início de cada capítulo procurando linhas no padrão
"Chapter N:" / "Extra Chapter" no próprio corpo do texto (não usa a
Table of Contents, que pode ter títulos diferentes do cabeçalho real
da página).

Gera, para cada capítulo:
  - um arquivo .txt com o texto extraído (para colar no tradutor)
  - uma entrada em manifest.json com número, título, página inicial/final

Uso:
    /usr/bin/python extract_chapters.py "../english version/mt_v17.pdf" ../translation/v17/en
"""

import json
import re
import sys
from pathlib import Path

import pymupdf as fitz

CHAPTER_RE = re.compile(r"^(Chapter\s+\d+|Extra\s+Chapter)\s*:?\s*$")


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:60]


def extract(pdf_path, out_dir):
    doc = fitz.open(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # Encontrar página inicial + título de cada capítulo
    # -------------------------------------------------------------

    chapters = []  # list of (start_page_idx, label, title)

    for pno in range(len(doc)):
        lines = [l.strip() for l in doc[pno].get_text().split("\n")]
        lines = [l for l in lines if l]

        for i, line in enumerate(lines):
            if CHAPTER_RE.match(line):
                label = line.rstrip(":").strip()
                title = lines[i + 1] if i + 1 < len(lines) else ""
                chapters.append((pno, label, title))
                break  # só o primeiro heading por página

    if not chapters:
        print("Nenhum cabeçalho de capítulo encontrado com o padrão atual.")
        return

    # -------------------------------------------------------------
    # Determinar o intervalo de páginas de cada capítulo
    # -------------------------------------------------------------

    manifest = []

    for idx, (start, label, title) in enumerate(chapters):
        end = chapters[idx + 1][0] - 1 if idx + 1 < len(chapters) else len(doc) - 1

        text_parts = []
        for pno in range(start, end + 1):
            text_parts.append(doc[pno].get_text())

        full_text = "\n".join(text_parts).strip()

        num_prefix = f"{idx + 1:02d}"
        slug = slugify(title) or slugify(label)
        filename = f"{num_prefix}_{slug}.txt"

        (out_dir / filename).write_text(full_text, encoding="utf-8")

        manifest.append(
            {
                "order": idx + 1,
                "label": label,
                "title": title,
                "start_page": start + 1,
                "end_page": end + 1,
                "file": filename,
                "chars": len(full_text),
            }
        )

        print(f"{num_prefix} {label}: {title!r}  (p{start + 1}-{end + 1})  -> {filename}")

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n{len(manifest)} capítulos extraídos em: {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: extract_chapters.py <entrada.pdf> <dir_saida>")
        sys.exit(1)

    extract(sys.argv[1], sys.argv[2])
