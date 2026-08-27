# Mushoku Tensei — PDFs para Kindle

Volumes 01–26 de *Mushoku Tensei: Jobless Reincarnation*, organizados e
corrigidos para envio ao Kindle por e-mail usando `CONVERT` no assunto.

## Estrutura

```
mushoku-tensei/
├── volumes/                        # PDFs finais, prontos para enviar ao Kindle
│   ├── mt_v01.pdf ... mt_v26.pdf
├── scripts/                        # scripts usados na correção (reutilizáveis)
│   ├── fix_orientation.py
│   ├── normalize_pagesize_test.py
│   └── normalize_pagesize_batch.py
├── backups/
│   ├── original/                   # v17–26 como estavam antes de qualquer correção
│   └── pagesize_pre_normalize/     # v17–26 com a página landscape já corrigida,
│                                    # mas ainda com tamanhos de página mistos
└── README.md
```

Os volumes 01–16 nunca tiveram problema — não passaram por nenhum dos
scripts abaixo, só pela padronização de metadados (exiftool).

## Metadados padrão

Todo volume `XX` segue:

```
Title:    Mushoku Tensei - Volume XX
Author:   Rifujin na Magonote
Subject:  Mushoku Tensei: Jobless Reincarnation
Keywords: Mushoku Tensei, Light Novel, Rifujin na Magonote, Shirotaka
Language: pt-BR
```

Sem `Creator`, `Producer`, `CreatorTool` ou `XMPToolkit`. Comando usado:

```bash
exiftool -overwrite_original \
  -Title="Mushoku Tensei - Volume $i" \
  -Author="Rifujin na Magonote" \
  -Subject="Mushoku Tensei: Jobless Reincarnation" \
  -Keywords="Mushoku Tensei, Light Novel, Rifujin na Magonote, Shirotaka" \
  -Language="pt-BR" \
  -Creator= -Producer= -CreatorTool= -XMPToolkit= \
  "mt_v$i.pdf"
```

## O problema: v17–26 chegavam em paisagem no Kindle

Os volumes 01–16 sempre ficaram em retrato ao converter. A partir do 17
(fonte diferente: scan + tradução automática do Google, mesclado com
páginas de capa/material inicial de outra edição), o Kindle convertia o
livro inteiro para paisagem — mesmo depois de corrigir a única página
fisicamente landscape de cada volume (um ilustração de página dupla,
comum também nos volumes 10/12/15, que nunca deram problema).

### O que foi investigado e descartado

Comparação estrutural completa entre `mt_v16.pdf` (funciona) e
`mt_v17.pdf` (falhava): `/Rotate`, `/CropBox` vs `/MediaBox`, matrizes
`cm` nos content streams, orientação das imagens brutas (JPEGs
embutidos), fontes, presença de texto real vs. imagem. Nenhum desses
pontos diferenciava os dois grupos de forma consistente — em especial,
`mt_v10.pdf`, `mt_v12.pdf` e `mt_v15.pdf` também têm uma página
fisicamente landscape cada e sempre funcionaram bem, o que descarta
"existir uma página landscape" como causa.

### Causa real identificada

**Inconsistência real de tamanho físico de página dentro do mesmo PDF.**

- v01–16: uma única geometria de página em todo o volume (A4, com
  variação de décimos de ponto por arredondamento).
- v17–26: pelo menos duas geometrias diferentes de verdade — o corpo
  do livro (scan traduzido) em um tamanho (ex.: 612×792 pt, US Letter)
  e as páginas iniciais/capa (de outra fonte) em outro, bem menor
  (ex.: 454×648 pt).

O conversor do Kindle parece tratar documentos com geometria de página
inconsistente de forma diferente de um manuscrito uniforme, caindo num
modo de renderização que escolhe paisagem.

### Correção aplicada

Para cada volume 17–26: detectar o tamanho de página **dominante do
próprio volume** (não um valor arbitrário como A4) e reencaixar
vetorialmente (via `show_pdf_page` do PyMuPDF — sem rasterizar) apenas
as páginas com tamanho diferente, escaladas proporcionalmente e
centralizadas (letterbox). As páginas que já estavam no tamanho
dominante (a grande maioria) foram copiadas sem nenhuma alteração.

Resultado: cada volume passou a ter um único `/MediaBox` em todas as
páginas, texto e imagens preservados sem perda de qualidade,
metadados e (quando existente) sumário preservados.

**Confirmado por teste real no Kindle** com `mt_v17.pdf` antes de
aplicar aos demais.

## Scripts

### `scripts/fix_orientation.py`
Primeira tentativa: corrige apenas páginas fisicamente landscape
(`width > height`), reencaixando-as centralizadas dentro do tamanho
vertical predominante. Sozinho não resolveu o problema do Kindle (ver
acima), mas é um pré-requisito útil caso apareça um volume novo com
página landscape solta.

### `scripts/normalize_pagesize_test.py`
Versão de teste para um único arquivo: uniformiza todas as páginas de
um PDF para o tamanho dominante do próprio documento. Usada para gerar
e validar `mt_v17_kindletest.pdf` antes de aplicar em lote.

```bash
cd volumes
/usr/bin/python ../scripts/normalize_pagesize_test.py mt_v17.pdf mt_v17_kindletest.pdf
```

### `scripts/normalize_pagesize_batch.py`
Mesma lógica, em lote, para vários volumes de uma vez. Foi o script
usado para corrigir 18–26 depois que o teste do 17 foi validado no
Kindle.

```bash
cd volumes
/usr/bin/python ../scripts/normalize_pagesize_batch.py 18 19 20 21 22 23 24 25 26
```

Gera `mt_vXX_normalized_tmp.pdf` ao lado de cada original — ainda
precisa passar por `qpdf` (remover incremental updates) e `exiftool`
(reaplicar metadados) antes de substituir o arquivo final:

```bash
for i in 18 19 20 21 22 23 24 25 26; do
  qpdf "mt_v${i}_normalized_tmp.pdf" "mt_v${i}_clean.pdf" && \
  mv "mt_v${i}_clean.pdf" "mt_v${i}_normalized_tmp.pdf"

  exiftool -overwrite_original \
    -Title="Mushoku Tensei - Volume $i" \
    -Author="Rifujin na Magonote" \
    -Subject="Mushoku Tensei: Jobless Reincarnation" \
    -Keywords="Mushoku Tensei, Light Novel, Rifujin na Magonote, Shirotaka" \
    -Language="pt-BR" \
    -Creator= -Producer= -CreatorTool= -XMPToolkit= \
    "mt_v${i}_normalized_tmp.pdf"

  mv "mt_v${i}_normalized_tmp.pdf" "mt_v${i}.pdf"
done
```

## Ambiente (EndeavourOS)

```bash
sudo pacman -S perl-image-exiftool qpdf poppler python-pymupdf ghostscript
```

- `exiftool`, `qpdf`, `pdfinfo`/`pdftoppm`/`pdffonts` (poppler) — no PATH normal.
- PyMuPDF (`import pymupdf`) só está disponível no Python do sistema:
  `/usr/bin/python`, **não** no `python` do pyenv (`~/.pyenv/shims/python`).
  Sempre rode os scripts `.py` deste projeto com `/usr/bin/python`.

## Validação usada em cada volume

```bash
qpdf --check mt_vXX.pdf
pdfinfo -f 1 -l 999 mt_vXX.pdf | awk '/Page +[0-9]+ size:/ {print $4"x"$6}' | sort -u
exiftool mt_vXX.pdf | grep -E "^Producer|^Creator|^Language|^Title"
```

Espera-se: sem erros no qpdf, uma única linha de tamanho de página,
nenhum Producer/Creator, Language `pt-BR` e Title correto.
