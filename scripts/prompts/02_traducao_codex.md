# Prompt — Tradução EN → PT-BR (Codex)

Contexto: estou remontando os volumes 19-26 da light novel Mushoku
Tensei (já tenho os PDFs originais, isso não é sobre baixar nada) com
uma tradução PT-BR melhor do que a que eu tinha antes (era tradução
automática crua do Google Translate, cheia de erro e artefato tipo
"Machine Translated by Google" no meio do texto). Os volumes 17 e 18
já foram traduzidos e revisados — esse prompt é para os que faltam.

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
- **Fidelidade estrita ao conteúdo**: não adicione detalhes,
  qualificadores ou especificidade que não estejam no original (ex.:
  se o inglês diz "ficar com a gente", não vire "jantar com a gente";
  se diz "havia acabado de completar X anos", não escreva de um jeito
  que soe como "já tinha passado dos X anos"). Isso já causou 2
  correções no volume 18 — preste atenção especial nisso.
- O tom e a voz de cada personagem (formal, informal, sarcástico,
  infantil etc.), consistentes ao longo do texto.
- **Mesma intensidade do original, sem censura**: palavrões, cenas
  sexuais e insultos com o mesmo peso do inglês, nunca suavizados.
  Siga `translation/ESTILO.md` (leia inteiro antes de cada volume).
- Pronomes e gênero corretos conforme o contexto da cena (não
  assuma; infira pelo que já foi dito sobre o personagem).
- Diálogos naturais em português, incluindo gírias/expressões quando
  fizer sentido, sem soar robótico.
- Quebras de parágrafo e formatação do original (uma linha do
  original = uma linha/parágrafo na tradução; não junte nem separe).
  **Atenção**: cada linha do `.txt` em inglês é uma quebra de linha
  visual do PDF (word-wrap), não necessariamente um parágrafo
  completo — é esperado e correto unir linhas quebradas em um
  parágrafo de prosa fluido, só não pule/funda conteúdo de verdade.
- Nomes próprios e termos do glossário abaixo exatamente como
  especificado — não traduza nomes marcados como "mantém".
- A primeira linha do arquivo é um marcador de página tipo
  "Page | 23" — remova, não faz parte do texto (inclusive se
  aparecer de novo no meio do capítulo, em qualquer página).
- A linha seguinte é o cabeçalho do capítulo, tipo "Chapter 3:" e o
  título na linha de baixo — traduza para "Capítulo 3:" + título em
  português, mantendo as duas linhas separadas.
- Se o capítulo terminar com material tipo "About the Author",
  newsletter ou "[FIM DO VOLUME]" grudado no final (comum no último
  capítulo de cada volume), **não traduza essa parte** — corte fora,
  não é conteúdo do capítulo.

Não adicione comentários, notas de rodapé ou explicações. Devolva
apenas o texto traduzido, no mesmo formato/estrutura de linhas do
original.

## Glossário (usar em todos os volumes, para manter consistência)

Está em `translation/GLOSSARIO.md` — leia o arquivo inteiro antes de
começar cada volume (ele é atualizado entre volumes, releia mesmo se
já leu antes). Tem os nomes de personagens e termos já usados nos
volumes 17-18 (traduzidos e revisados). Se aparecer um nome ou termo
novo que não está no glossário, **adicione uma entrada nele antes de
seguir traduzindo o resto do capítulo** — isso é importante pra manter
os volumes 19-26 consistentes entre si e com os anteriores.

## Fluxo de trabalho

Para cada volume (comece pelo 19, depois 20, 21... até 26):

1. Leia todos os arquivos `.txt` de `translation/vNN/en/` (ignore o
   `manifest.json`, é só metadado).
2. Traduza capítulo por capítulo (não precisa ser um chat por
   capítulo — pode processar vários na mesma conversa, mas releia o
   glossário antes de cada capítulo novo, caso você mesmo tenha
   adicionado termos durante o volume).
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

Ao terminar cada volume, me avise aqui — a validação da tradução é
feita por outra pessoa (Claude), não precisa fazer isso você mesmo.
