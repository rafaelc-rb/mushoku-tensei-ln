import os
import shutil
from collections import Counter

import pymupdf as fitz


START_VOLUME = 17
END_VOLUME = 26

BACKUP_DIR = "backup_orientation"


def fix_pdf(filename):
    print(f"\n=== {filename} ===")

    if not os.path.exists(filename):
        print("Arquivo não encontrado. Pulando.")
        return

    # ---------------------------------------------------------
    # Backup
    # ---------------------------------------------------------

    os.makedirs(BACKUP_DIR, exist_ok=True)

    backup_path = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(backup_path):
        shutil.copy2(filename, backup_path)
        print(f"Backup criado: {backup_path}")
    else:
        print(f"Backup já existe: {backup_path}")

    # ---------------------------------------------------------
    # Abrir PDF
    # ---------------------------------------------------------

    doc = fitz.open(filename)

    # ---------------------------------------------------------
    # Descobrir o tamanho vertical predominante
    # ---------------------------------------------------------

    portrait_sizes = []

    for page in doc:
        rect = page.rect

        if rect.height >= rect.width:
            portrait_sizes.append(
                (
                    round(rect.width, 2),
                    round(rect.height, 2),
                )
            )

    if not portrait_sizes:
        print("Nenhuma página vertical encontrada.")
        doc.close()
        return

    target_width, target_height = Counter(
        portrait_sizes
    ).most_common(1)[0][0]

    print(
        f"Tamanho vertical predominante: "
        f"{target_width} × {target_height} pt"
    )

    # ---------------------------------------------------------
    # Encontrar páginas horizontais
    # ---------------------------------------------------------

    landscape_pages = []

    for pno, page in enumerate(doc):
        rect = page.rect

        if rect.width > rect.height:
            landscape_pages.append(pno)

    if not landscape_pages:
        print("Nenhuma página horizontal encontrada.")
        doc.close()
        return

    print(
        "Páginas horizontais encontradas: "
        + ", ".join(str(p + 1) for p in landscape_pages)
    )

    # ---------------------------------------------------------
    # Criar novo PDF
    # ---------------------------------------------------------

    out = fitz.open()

    for pno, page in enumerate(doc):

        rect = page.rect

        # -----------------------------------------------------
        # Página vertical:
        # copiar sem alterar tamanho ou conteúdo
        # -----------------------------------------------------

        if rect.width <= rect.height:

            out.insert_pdf(
                doc,
                from_page=pno,
                to_page=pno,
            )

            continue

        # -----------------------------------------------------
        # Página horizontal:
        # criar uma página vertical e colocar o conteúdo dentro
        # -----------------------------------------------------

        print(
            f"Corrigindo página {pno + 1}: "
            f"{rect.width:.2f} × {rect.height:.2f} pt"
        )

        new_page = out.new_page(
            width=target_width,
            height=target_height,
        )

        # Escala máxima possível sem cortar conteúdo
        scale = min(
            target_width / rect.width,
            target_height / rect.height,
        )

        content_width = rect.width * scale
        content_height = rect.height * scale

        # Centralizar
        x0 = (target_width - content_width) / 2
        y0 = (target_height - content_height) / 2

        destination = fitz.Rect(
            x0,
            y0,
            x0 + content_width,
            y0 + content_height,
        )

        # Insere a página original como PDF vetorial,
        # sem rasterizar
        new_page.show_pdf_page(
            destination,
            doc,
            pno,
            keep_proportion=True,
        )

    # ---------------------------------------------------------
    # Preservar metadados
    # ---------------------------------------------------------

    try:
        metadata = doc.metadata

        if metadata:
            out.set_metadata(metadata)

    except Exception as error:
        print(f"Aviso ao copiar metadados: {error}")

    # ---------------------------------------------------------
    # Preservar bookmarks / sumário
    # ---------------------------------------------------------

    try:
        toc = doc.get_toc()

        if toc:
            out.set_toc(toc)

    except Exception as error:
        print(f"Aviso ao copiar bookmarks: {error}")

    # ---------------------------------------------------------
    # Salvar temporariamente
    # ---------------------------------------------------------

    temp_filename = filename.replace(
        ".pdf",
        "_orientation_fixed.pdf",
    )

    out.save(
        temp_filename,
        garbage=4,
        deflate=True,
        clean=True,
    )

    out.close()
    doc.close()

    # ---------------------------------------------------------
    # Substituir original
    # ---------------------------------------------------------

    os.replace(
        temp_filename,
        filename,
    )

    print(f"Concluído: {filename}")


# =============================================================
# PROCESSAR VOLUMES 17–26
# =============================================================

for volume in range(START_VOLUME, END_VOLUME + 1):

    filename = f"mt_v{volume:02d}.pdf"

    fix_pdf(filename)


print("\n================================")
print("Todos os arquivos processados.")
print("================================")
