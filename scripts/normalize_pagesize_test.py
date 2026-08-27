"""
TESTE ISOLADO — não sobrescreve o arquivo original.

Hipótese sendo testada: o Kindle Convert decide a orientação do livro
inteiro com base na (in)consistência do tamanho físico das páginas
(/MediaBox) ao longo do documento — não apenas por existir uma página
fisicamente landscape (isso já foi descartado: mt_v10/12/15, que
funcionam bem no Kindle, também têm 1 página landscape cada, um
spread colorido normal).

O que este script faz, para UM volume por vez:

1. Abre o PDF de entrada (já com a página landscape corrigida).
2. Descobre o tamanho de página DOMINANTE do próprio documento
   (moda entre todas as páginas — não um tamanho arbitrário tipo A4).
3. Copia sem nenhuma alteração as páginas que já têm esse tamanho
   (a grande maioria — nenhuma perda de qualidade, nenhuma
   re-renderização).
4. Para as páginas com tamanho diferente (tipicamente as páginas
   iniciais, menores, de outra fonte/proveniência), cria uma página
   nova no tamanho dominante e embute a página original como XObject
   vetorial (show_pdf_page), escalada proporcionalmente e centralizada
   (letterbox), sem rasterizar nada.
5. Preserva metadata e TOC do documento de entrada.
6. Salva em um arquivo de SAÍDA SEPARADO (nunca sobrescreve o
   original).

Uso:
    /usr/bin/python normalize_pagesize_test.py mt_v17.pdf mt_v17_kindletest.pdf
"""

import sys
from collections import Counter

import pymupdf as fitz


def normalize(input_path, output_path):
    doc = fitz.open(input_path)

    # ---------------------------------------------------------
    # Descobrir o tamanho dominante do documento (moda)
    # ---------------------------------------------------------

    sizes = [
        (round(page.rect.width, 1), round(page.rect.height, 1))
        for page in doc
    ]

    (target_width, target_height), count = Counter(sizes).most_common(1)[0]

    print(
        f"Tamanho dominante detectado: "
        f"{target_width} x {target_height} pt "
        f"({count}/{len(sizes)} páginas)"
    )

    distinct = Counter(sizes)
    print(f"Tamanhos distintos encontrados: {len(distinct)}")
    for size, n in distinct.most_common():
        print(f"  {size[0]} x {size[1]} pt  -> {n} página(s)")

    # ---------------------------------------------------------
    # Construir documento de saída
    # ---------------------------------------------------------

    out = fitz.open()
    changed_pages = []

    for pno, page in enumerate(doc):
        rect = page.rect
        w, h = round(rect.width, 1), round(rect.height, 1)

        if (w, h) == (target_width, target_height):
            # Já está no tamanho dominante: copia sem tocar
            out.insert_pdf(doc, from_page=pno, to_page=pno)
            continue

        changed_pages.append((pno + 1, w, h))

        new_page = out.new_page(width=target_width, height=target_height)

        scale = min(target_width / rect.width, target_height / rect.height)
        content_width = rect.width * scale
        content_height = rect.height * scale

        x0 = (target_width - content_width) / 2
        y0 = (target_height - content_height) / 2

        destination = fitz.Rect(
            x0, y0, x0 + content_width, y0 + content_height
        )

        # Embute a página original como XObject vetorial (sem rasterizar)
        new_page.show_pdf_page(
            destination,
            doc,
            pno,
            keep_proportion=True,
        )

    if changed_pages:
        print(f"\nPáginas reencaixadas ({len(changed_pages)}):")
        for pno, w, h in changed_pages:
            print(f"  página {pno}: {w} x {h} pt -> {target_width} x {target_height} pt")
    else:
        print("\nNenhuma página precisou ser reencaixada (já uniforme).")

    # ---------------------------------------------------------
    # Preservar metadata e TOC
    # ---------------------------------------------------------

    try:
        metadata = doc.metadata
        if metadata:
            out.set_metadata(metadata)
    except Exception as error:
        print(f"Aviso ao copiar metadados: {error}")

    try:
        toc = doc.get_toc()
        if toc:
            out.set_toc(toc)
    except Exception as error:
        print(f"Aviso ao copiar bookmarks: {error}")

    out.save(output_path, garbage=4, deflate=True, clean=True)
    out.close()
    doc.close()

    print(f"\nArquivo de teste gerado: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: normalize_pagesize_test.py <entrada.pdf> <saida.pdf>")
        sys.exit(1)

    normalize(sys.argv[1], sys.argv[2])
