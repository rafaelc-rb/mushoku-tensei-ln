"""
Aplica a correção validada (uniformizar o tamanho de página para o
tamanho DOMINANTE de cada volume, reencaixando vetorialmente as
páginas divergentes via show_pdf_page) aos volumes indicados.

Não sobrescreve o arquivo original diretamente: gera um arquivo
"<nome>_normalized_tmp.pdf" ao lado, que depois passa por:
  1. qpdf (rebuild / remove incremental updates)
  2. exiftool (reaplica metadata canônica, remove Producer/Creator/etc)
antes de substituir o original (feito pelo apply_pagesize_fix.sh).

Uso:
    /usr/bin/python normalize_pagesize_batch.py 18 19 20 21 22 23 24 25 26
"""

import sys
from collections import Counter

import pymupdf as fitz


def normalize(input_path, output_path):
    doc = fitz.open(input_path)

    sizes = [
        (round(page.rect.width, 1), round(page.rect.height, 1))
        for page in doc
    ]

    (target_width, target_height), count = Counter(sizes).most_common(1)[0]

    print(
        f"  Tamanho dominante: {target_width} x {target_height} pt "
        f"({count}/{len(sizes)} páginas)"
    )

    distinct = Counter(sizes)
    if len(distinct) > 1:
        for size, n in distinct.most_common():
            print(f"    {size[0]} x {size[1]} pt -> {n} página(s)")

    out = fitz.open()
    changed = 0

    for pno, page in enumerate(doc):
        rect = page.rect
        w, h = round(rect.width, 1), round(rect.height, 1)

        if (w, h) == (target_width, target_height):
            out.insert_pdf(doc, from_page=pno, to_page=pno)
            continue

        changed += 1

        new_page = out.new_page(width=target_width, height=target_height)

        scale = min(target_width / rect.width, target_height / rect.height)
        content_width = rect.width * scale
        content_height = rect.height * scale

        x0 = (target_width - content_width) / 2
        y0 = (target_height - content_height) / 2

        destination = fitz.Rect(
            x0, y0, x0 + content_width, y0 + content_height
        )

        new_page.show_pdf_page(
            destination,
            doc,
            pno,
            keep_proportion=True,
        )

    print(f"  Páginas reencaixadas: {changed}")

    try:
        metadata = doc.metadata
        if metadata:
            out.set_metadata(metadata)
    except Exception as error:
        print(f"  Aviso ao copiar metadados: {error}")

    try:
        toc = doc.get_toc()
        if toc:
            out.set_toc(toc)
    except Exception as error:
        print(f"  Aviso ao copiar bookmarks: {error}")

    out.save(output_path, garbage=4, deflate=True, clean=True)
    out.close()
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: normalize_pagesize_batch.py <vol> [<vol> ...]")
        sys.exit(1)

    for vol in sys.argv[1:]:
        vol = int(vol)
        filename = f"mt_v{vol:02d}.pdf"
        tmp_out = f"mt_v{vol:02d}_normalized_tmp.pdf"

        print(f"\n=== {filename} ===")
        normalize(filename, tmp_out)
        print(f"  Gerado: {tmp_out}")
