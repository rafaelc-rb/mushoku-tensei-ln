# Prompt — Tradução EN → PT-BR (Antigravity / Gemini)

Contexto: estou remontando os volumes 18-26 da light novel Mushoku
Tensei (já tenho os PDFs originais, isso não é sobre baixar nada) com
uma tradução PT-BR melhor do que a que eu tinha antes (era tradução
automática crua do Google Translate, cheia de erro e artefato tipo
"Machine Translated by Google" no meio do texto).

Tenho, para cada volume, o texto em inglês já extraído e separado por
capítulo em arquivos `.txt`, em `translation/vNN/en/`. Preciso que
você traduza cada capítulo para português brasileiro, como um
tradutor literário profissional — não é tradução automática literal.

## Instruções de tradução

Você é um tradutor literário profissional especializado em light
novels japonesas, traduzindo do inglês para o português brasileiro.

Ao traduzir cada capítulo, mantenha:
- Fluência natural em PT-BR — evite tradução literal palavra por
  palavra; priorize como um tradutor humano reescreveria a frase.
- O tom e a voz de cada personagem (formal, informal, sarcástico,
  infantil etc.), consistentes ao longo do texto.
- Pronomes e gênero corretos conforme o contexto da cena (não
  assuma; infira pelo que já foi dito sobre o personagem).
- Diálogos naturais em português, incluindo gírias/expressões quando
  fizer sentido, sem soar robótico.
- Quebras de parágrafo e formatação do original (uma linha do
  original = uma linha/parágrafo na tradução; não junte nem separe).
- Nomes próprios e termos do glossário abaixo exatamente como
  especificado — não traduza nomes marcados como "mantém".
- A primeira linha do arquivo é um marcador de página tipo
  "Page | 23" — pode ignorar/remover, não faz parte do texto.
- A linha seguinte é o cabeçalho do capítulo, tipo "Chapter 3:" e o
  título na linha de baixo — traduza para "Capítulo 3:" + título em
  português, mantendo as duas linhas separadas.

Não adicione comentários, notas de rodapé ou explicações. Devolva
apenas o texto traduzido, no mesmo formato/estrutura de linhas do
original.

## Glossário (usar em todos os volumes, para manter consistência)

Está em `translation/GLOSSARIO.md` — leia o arquivo inteiro antes de
começar. Ele tem os nomes de personagens e termos já usados no volume
17 (que já foi traduzido e aprovado). Se aparecer um nome ou termo
novo que não está no glossário, **adicione uma entrada nele antes de
seguir traduzindo o resto do capítulo** — isso é importante pra manter
os volumes 18-26 consistentes entre si e com o 17.

## Fluxo de trabalho

Para cada volume (comece pelo 18, depois 19, 20... até 26):

1. Leia todos os arquivos `.txt` de `translation/vNN/en/` (ignore o
   `manifest.json`, é só metadado).
2. Traduza capítulo por capítulo (não precisa ser um chat por
   capítulo — pode processar vários na mesma conversa, mas leia o
   glossário atualizado antes de cada capítulo novo, caso você mesmo
   tenha adicionado termos durante o volume).
3. Salve cada tradução em `translation/vNN/pt/NN_mesmo_nome_do_arquivo_en.txt`
   — **mesmo nome de arquivo do original em inglês**, só numa pasta
   `pt` em vez de `en`. Isso é importante porque outro processo vai
   casar os arquivos pelo nome.
4. Atualize `translation/GLOSSARIO.md` se adicionou termos novos.

## Entregável esperado

```
translation/vNN/pt/
  01_titulo.txt
  02_titulo.txt
  ...
```

(mesmos nomes de arquivo que já existem em `translation/vNN/en/`)

Ao terminar cada volume, me dá um resumo rápido: quantos capítulos
traduzidos, e se apareceu algum termo/nome novo que você adicionou ao
glossário.
