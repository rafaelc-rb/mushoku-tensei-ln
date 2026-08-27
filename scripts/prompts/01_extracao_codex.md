# Prompt — Extração de capítulos (Codex)

Contexto: projeto em `~/Documents/my-docs/manga/mushoku-tensei/`. É uma
coleção pessoal de PDFs da light novel Mushoku Tensei, volumes 01-26,
organizados para leitura no Kindle. Os volumes 17-26 vieram de uma
fonte diferente (scan + tradução automática ruim do Google) e estão
sendo remontados com tradução melhor, usando como base os PDFs em
inglês que já tenho em `english version/mt_vNN.pdf`.

Já existe um script pronto que faz a extração:
`scripts/extract_chapters.py`. Ele abre o PDF em inglês de um volume,
detecta o início de cada capítulo procurando linhas no padrão
"Chapter N:" / "Extra Chapter" no corpo do texto, e gera:
  - um `.txt` por capítulo em `translation/vNN/en/`
  - um `manifest.json` com número, título e intervalo de página de
    cada capítulo (baseado na paginação do PDF em inglês)

Já rodei esse script pro volume 17 com sucesso (15 capítulos
extraídos corretamente, títulos batendo com o índice do livro).

## O que preciso que você faça

Rode `scripts/extract_chapters.py` para os volumes 18 a 26:

```bash
cd ~/Documents/my-docs/manga/mushoku-tensei
/usr/bin/python scripts/extract_chapters.py "english version/mt_v18.pdf" translation/v18/en
/usr/bin/python scripts/extract_chapters.py "english version/mt_v19.pdf" translation/v19/en
# ... e assim por diante até o v26
```

**Importante**: use `/usr/bin/python`, não `python` puro — o PyMuPDF só
está instalado no Python do sistema, não no do pyenv.

Para cada volume, confira a saída impressa no terminal:
- número de capítulos detectados bate com o esperado (geralmente
  13-15 capítulos + eventual "Extra Chapter")
- os títulos dos capítulos fazem sentido (não vieram cortados/vazios)
- não sobrou nenhum capítulo com 0 caracteres extraídos

Se algum volume tiver uma estrutura diferente (por exemplo, o padrão
"Chapter N:" não bater, ou o PDF ter uma paginação estranha), me avise
qual volume e o que saiu errado em vez de tentar consertar sozinho o
script sem contexto — pode ser algo específico daquele volume que eu
preciso decidir como tratar.

## Entregável esperado

Ao final, a pasta `translation/` deve ter, para cada volume 18-26:
```
translation/vNN/en/
  01_titulo.txt
  02_titulo.txt
  ...
  manifest.json
```

Me dê um resumo por volume: quantos capítulos, e se algo ficou
estranho.
