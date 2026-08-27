# Prompt — Montagem do PDF final PT-BR (Codex)

Contexto: projeto em `~/Documents/my-docs/manga/mushoku-tensei/`.
Estou remontando os volumes 18-26 da light novel Mushoku Tensei em
PT-BR. Já existe um script pronto e validado que faz a montagem final
do PDF: `scripts/rebuild_translated_pdf.py`. Ele já foi usado com
sucesso no volume 17 (funciona, resultado aprovado).

## O que o script faz

Para um volume `NN`, ele:
1. Lê `volumes/english version/mt_vNN.pdf` (fonte de ilustrações e de
   paginação de referência) e `translation/vNN/en/manifest.json`
   (intervalo de página de cada capítulo, gerado pelo
   `extract_chapters.py`).
2. Detecta, no PDF em inglês, as páginas que são só ilustração
   (pouquíssimo texto extraível — capa, spreads, cenas de ação sem
   texto).
3. Associa cada ilustração ao capítulo em cujo intervalo de página ela
   cai, calculando uma fração (posição relativa dentro do capítulo).
4. Lê a tradução em `translation/vNN/pt/*.txt` (deve já estar pronta e
   validada antes de rodar isso).
5. Tipografa o texto do zero (fonte serifada, justificado, com página
   de abertura de capítulo), inserindo cada ilustração no ponto
   correspondente à fração calculada — não é uma galeria solta, é
   posicionado dentro do fluxo do capítulo certo.
6. Gera `volumes/mt_vNN_pt_retranslated_test.pdf`.

## O que preciso que você faça

Para cada volume 18 a 26, **depois que a tradução daquele volume
estiver em `translation/vNN/pt/` e validada** (não rode antes disso
estar pronto):

```bash
cd ~/Documents/my-docs/manga/mushoku-tensei
/usr/bin/python scripts/rebuild_translated_pdf.py 18
```

Depois, para cada PDF gerado, rode a limpeza e os metadados padrão
(mesmo processo usado no volume 17):

```bash
qpdf volumes/mt_v18_pt_retranslated_test.pdf volumes/mt_v18_clean.pdf && \
mv volumes/mt_v18_clean.pdf volumes/mt_v18_pt_retranslated_test.pdf

exiftool -overwrite_original \
  -Title="Mushoku Tensei - Volume 18" \
  -Author="Rifujin na Magonote" \
  -Subject="Mushoku Tensei: Jobless Reincarnation" \
  -Keywords="Mushoku Tensei, Light Novel, Rifujin na Magonote, Shirotaka" \
  -Language="pt-BR" \
  -Creator= -Producer= -CreatorTool= -XMPToolkit= \
  volumes/mt_v18_pt_retranslated_test.pdf
```

(troque `18` pelo número do volume em cada passo)

## Validação depois de gerar cada PDF

```bash
qpdf --check volumes/mt_vNN_pt_retranslated_test.pdf
pdfinfo volumes/mt_vNN_pt_retranslated_test.pdf
```

Confirme, pra cada volume:
- `qpdf --check` sem erro
- um único tamanho de página em todo o PDF (dá pra conferir com
  `pdfinfo -f 1 -l 999 arquivo.pdf | awk '/Page +[0-9]+ size:/ {print $4"x"$6}' | sort -u`
  — deve retornar só uma linha)
- `Title`/`Author`/`Subject`/`Keywords`/`Language` corretos, sem
  `Producer`/`Creator`
- número de páginas do PDF final é maior que o número de capítulos
  (senão algo deu muito errado na geração)

Se o script der erro em algum volume específico (por exemplo, se a
detecção de capítulo daquele volume ficou estranha na etapa de
extração), me avise qual volume e o erro, em vez de alterar a lógica
do script sem eu revisar — ele foi ajustado com cuidado pra acertar o
posicionamento de imagem, e uma mudança errada pode quebrar isso pros
outros volumes.

## Entregável esperado

```
volumes/mt_v18_pt_retranslated_test.pdf
volumes/mt_v19_pt_retranslated_test.pdf
...
volumes/mt_v26_pt_retranslated_test.pdf
```

Cada um validado conforme acima. Me dê um resumo por volume: número de
páginas, número de ilustrações posicionadas, e se passou em todas as
checagens.
