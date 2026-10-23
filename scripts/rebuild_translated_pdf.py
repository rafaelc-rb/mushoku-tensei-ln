"""
Remonta um volume em PT-BR a partir da tradução já pronta
(translation/vNN/pt/*.txt), usando o PDF EM INGLÊS como referência de
layout: as páginas de ilustração (capa, spreads, cenas de ação sem
texto) são extraídas do PDF em inglês — sem marca d'água de tradução
automática — e posicionadas no ponto correto dentro do capítulo
correspondente, usando a paginação do próprio PDF em inglês como guia.

Passos:
  1. Lê translation/vNN/en/manifest.json (intervalo de página de cada
     capítulo, no PDF em inglês em volumes/english version/mt_vNN.pdf).
  2. Detecta, no PDF em inglês, as páginas com pouquíssimo texto
     (ilustrações puras): capa/material inicial fica na frente do
     volume; as demais são associadas ao capítulo em cujo intervalo
     de página caem, com uma fração (0.0-1.0) indicando a posição
     relativa dentro do capítulo.
  3. Para cada capítulo, pagina o texto traduzido (translation/vNN/pt)
     parágrafo por parágrafo e insere a(s) ilustração(ões) do PDF em
     inglês no ponto correspondente à fração calculada.
  4. Gera o PDF final com bookmarks por capítulo.

Uso:
    /usr/bin/python rebuild_translated_pdf.py 17
"""

import json
import re
import sys
from pathlib import Path

import pymupdf as fitz

ENGLISH_PDF_DIR = Path("volumes/english version")
ILLUSTRATION_TEXT_THRESHOLD = 150  # chars; abaixo disso = página só de arte

PAGE_MARGIN = 56  # pt
# Fontes TrueType embutidas (Liberation Serif = métricas da Times). As
# base-14 ("Times-Roman") só cobrem Latin-1: aspas curvas, "…" e "—"
# saíam como "·" no PDF (v17–v19).
FONT_DIR = Path("/usr/share/fonts/liberation")
BODY_FONT = "libserif"
BODY_FONT_FILE = FONT_DIR / "LiberationSerif-Regular.ttf"
BODY_FONT_SIZE = 11.5
LINE_HEIGHT = BODY_FONT_SIZE * 1.35
PARAGRAPH_GAP = BODY_FONT_SIZE * 0.55
TITLE_FONT = "libserifbold"
TITLE_FONT_FILE = FONT_DIR / "LiberationSerif-Bold.ttf"

BODY_FONT_METRICS = fitz.Font(fontfile=str(BODY_FONT_FILE))

PAGE_MARKER_RE = re.compile(r"^Page\s*\|\s*\d+\s*$")


# -------------------------------------------------------------------
# Mapeamento de ilustrações (fonte: PDF em inglês) para capítulos
# -------------------------------------------------------------------

def find_illustration_pages(doc):
    pages = []
    for pno in range(len(doc)):
        text = doc[pno].get_text().strip()
        if len(text) < ILLUSTRATION_TEXT_THRESHOLD:
            pages.append(pno)
    return pages


def classify_illustrations(illustration_pages, manifest):
    """Retorna (front_pages, {order: [(fraction, pno), ...]})."""

    first_start = manifest[0]["start_page"] - 1  # 0-indexed
    front = [p for p in illustration_pages if p < first_start]

    by_chapter = {ch["order"]: [] for ch in manifest}

    for pno in illustration_pages:
        if pno < first_start:
            continue
        page_1indexed = pno + 1
        for ch in manifest:
            start, end = ch["start_page"], ch["end_page"]
            if start <= page_1indexed <= end:
                span = max(end - start, 1)
                fraction = (page_1indexed - start) / span
                by_chapter[ch["order"]].append((fraction, pno))
                break

    return front, by_chapter


# -------------------------------------------------------------------
# Parsing dos capítulos traduzidos
# -------------------------------------------------------------------

def parse_chapter_file(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    lines = [l.rstrip() for l in lines]

    while lines and (not lines[0].strip() or lines[0].strip().startswith("Page")):
        lines.pop(0)

    heading_line = lines.pop(0).strip() if lines else ""
    title_line = ""
    if lines and lines[0].strip():
        title_line = lines.pop(0).strip()

    while lines and not lines[0].strip():
        lines.pop(0)

    lines = [l for l in lines if not PAGE_MARKER_RE.match(l.strip())]

    body = "\n".join(lines).strip()
    heading = f"{heading_line} {title_line}".strip() if title_line else heading_line

    return heading, [p.strip() for p in body.split("\n") if p.strip()]


# -------------------------------------------------------------------
# Tipografia / paginação
# -------------------------------------------------------------------

def wrap_paragraph(paragraph, max_width, font, fontsize):
    words = paragraph.split(" ")
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if font.text_length(candidate, fontsize=fontsize) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    return lines


class Paginator:
    def __init__(self, out_doc, en_doc, page_size):
        self.out = out_doc
        self.en = en_doc
        self.page_size = page_size
        self.body_width = page_size[0] - 2 * PAGE_MARGIN
        self.bottom = page_size[1] - PAGE_MARGIN
        self.page = None
        self.y = None

    def new_page(self):
        self.page = self.out.new_page(width=self.page_size[0], height=self.page_size[1])
        self.y = PAGE_MARGIN
        return self.page

    def ensure_page(self):
        if self.page is None:
            self.new_page()

    def add_paragraph(self, paragraph):
        self.ensure_page()
        lines = wrap_paragraph(paragraph, self.body_width, BODY_FONT_METRICS, BODY_FONT_SIZE)

        for line in lines:
            if self.y + LINE_HEIGHT > self.bottom:
                self.new_page()
            self.page.insert_text(
                (PAGE_MARGIN, self.y + BODY_FONT_SIZE),
                line,
                fontname=BODY_FONT,
                fontfile=str(BODY_FONT_FILE),
                fontsize=BODY_FONT_SIZE,
            )
            self.y += LINE_HEIGHT

        self.y += PARAGRAPH_GAP

    def add_illustration(self, en_page_index):
        """Insere a página de ilustração do PDF em inglês, escalada
        para o tamanho de página em uso, e retoma o texto numa página
        nova em seguida."""
        img_page = self.out.new_page(width=self.page_size[0], height=self.page_size[1])
        rect = fitz.Rect(0, 0, self.page_size[0], self.page_size[1])
        img_page.show_pdf_page(rect, self.en, en_page_index, keep_proportion=True)
        self.page = None  # força nova página pro texto seguinte


def add_chapter_title_page(doc, page_size, heading):
    page = doc.new_page(width=page_size[0], height=page_size[1])
    rect = fitz.Rect(
        PAGE_MARGIN,
        page_size[1] * 0.38,
        page_size[0] - PAGE_MARGIN,
        page_size[1] * 0.38 + 140,
    )
    page.insert_textbox(
        rect,
        heading,
        fontname=TITLE_FONT,
        fontfile=str(TITLE_FONT_FILE),
        fontsize=18,
        align=fitz.TEXT_ALIGN_CENTER,
    )
    return page


# -------------------------------------------------------------------
# Montagem principal
# -------------------------------------------------------------------

def rebuild(volume):
    en_path = ENGLISH_PDF_DIR / f"mt_v{volume:02d}.pdf"
    pt_dir = Path(f"translation/v{volume:02d}/pt")
    manifest_path = Path(f"translation/v{volume:02d}/en/manifest.json")
    out_path = Path(f"volumes/mt_v{volume:02d}_pt_retranslated_test.pdf")

    en_doc = fitz.open(en_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    page_size = (en_doc[0].rect.width, en_doc[0].rect.height)

    illustration_pages = find_illustration_pages(en_doc)
    front, by_chapter = classify_illustrations(illustration_pages, manifest)

    print(f"Páginas de ilustração na frente (EN): {[p + 1 for p in front]}")
    for order, items in by_chapter.items():
        if items:
            print(f"  capítulo {order}: {[(round(f, 2), p + 1) for f, p in items]}")

    out = fitz.open()

    # 1) frente do volume, direto do PDF em inglês (sem marca d'água)
    for pno in front:
        rect = fitz.Rect(0, 0, page_size[0], page_size[1])
        new_page = out.new_page(width=page_size[0], height=page_size[1])
        new_page.show_pdf_page(rect, en_doc, pno, keep_proportion=True)

    # 2) capítulos
    toc = []
    for ch in manifest:
        chapter_file = pt_dir / ch["file"]
        heading, paragraphs = parse_chapter_file(chapter_file)

        title_page = add_chapter_title_page(out, page_size, heading)
        toc.append([1, heading, title_page.number + 1])

        illustrations = sorted(by_chapter.get(ch["order"], []))
        total = max(len(paragraphs), 1)

        paginator = Paginator(out, en_doc, page_size)
        paginator.new_page()

        illus_idx = 0
        for i, paragraph in enumerate(paragraphs):
            progress = i / total
            while illus_idx < len(illustrations) and illustrations[illus_idx][0] <= progress:
                paginator.add_illustration(illustrations[illus_idx][1])
                illus_idx += 1
            paginator.add_paragraph(paragraph)

        while illus_idx < len(illustrations):
            paginator.add_illustration(illustrations[illus_idx][1])
            illus_idx += 1

        print(f"  {chapter_file.name}: {heading!r} -> {len(paragraphs)} parágrafos, "
              f"{len(illustrations)} ilustração(ões)")

    out.set_toc(toc)

    meta = {
        "title": f"Mushoku Tensei - Volume {volume}",
        "author": "Rifujin na Magonote",
        "subject": "Mushoku Tensei: Jobless Reincarnation",
        "keywords": "Mushoku Tensei, Light Novel, Rifujin na Magonote, Shirotaka",
    }
    out.set_metadata(meta)
    out.subset_fonts()

    out.save(out_path, garbage=4, deflate=True, clean=True)
    out.close()
    en_doc.close()

    check = fitz.open(out_path)
    print(f"\nGerado: {out_path}  ({len(check)} páginas)")
    check.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: rebuild_translated_pdf.py <numero_do_volume>")
        sys.exit(1)

    rebuild(int(sys.argv[1]))
