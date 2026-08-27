# Prompt — Validação da tradução (Codex)

Contexto: projeto em `~/Documents/my-docs/manga/mushoku-tensei/`.
Estou remontando os volumes 18-26 da light novel Mushoku Tensei com
tradução PT-BR nova (feita por outro assistente, capítulo por
capítulo). Preciso de uma segunda checagem, independente de quem
traduziu, pra pegar erro de tradução, inconsistência de termo e
problema estrutural antes de eu montar o PDF final.

Os arquivos estão em:
- `translation/vNN/en/NN_titulo.txt` — texto original em inglês
- `translation/vNN/pt/NN_titulo.txt` — tradução em PT-BR (mesmo nome
  de arquivo, pasta `pt` em vez de `en`)
- `translation/GLOSSARIO.md` — glossário de nomes/termos que a
  tradução deveria seguir

## O que preciso que você valide, por capítulo

1. **Estrutura**: o arquivo PT-BR tem aproximadamente o mesmo número
   de linhas/parágrafos que o EN (diferença grande de linha sugere
   trecho pulado ou parágrafo fundido incorretamente). Não precisa
   bater exato, mas se um capítulo em EN tem 200 linhas e o PT-BR tem
   80, isso é um sinal de alerta — sinalize.
2. **Nomes e termos**: os nomes de personagens/lugares que aparecem no
   PT-BR seguem exatamente o que está em `translation/GLOSSARIO.md`
   (grafia, quando manter em inglês vs quando traduzir). Sinalize
   qualquer nome que apareça com grafia diferente do glossário.
3. **Resíduos indesejados**: confira se sobrou algum "Page | N" no
   meio do corpo do texto (não só na primeira linha), ou qualquer
   texto em inglês não traduzido misturado no meio do português
   (indicativo de trecho que passou direto sem tradução).
4. **Amostra de qualidade de tradução**: pegue ~3-5 parágrafos por
   capítulo, espalhados (início, meio, fim), compare o EN com o PT-BR
   e avalie se a tradução está natural (não literal/robótica) e fiel
   ao sentido. Não precisa reescrever nada — só sinalizar trechos que
   pareçam estranhos, com nota de qual parágrafo (posição
   aproximada) e por quê.

**Importante**: não precisa (e não deve) me devolver o texto original
nem a tradução completa de volta na resposta — isso é o conteúdo
integral de um livro protegido por direitos autorais. Me devolva só
um relatório: lista de problemas encontrados, com localização
(capítulo + posição aproximada do parágrafo) e uma frase descrevendo
o problema. Se um capítulo não tiver nenhum problema, só diga "OK".

## Formato do relatório

Para cada volume, algo como:

```
Volume 18
  Capítulo 03: OK
  Capítulo 05: nome "Isolde" apareceu como "Izolde" 2x — não bate com glossário
  Capítulo 07: contagem de linhas EN=210 PT=95 — checar se faltou trecho
  Capítulo 09: parágrafo ~40, tradução parece literal demais / estranha
  ...
```

Comece pelo volume 18 e vá seguindo a ordem, conforme as traduções
forem ficando prontas em `translation/vNN/pt/`.
