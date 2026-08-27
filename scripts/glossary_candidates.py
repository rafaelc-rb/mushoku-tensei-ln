"""
Varre os capítulos extraídos (.txt) em busca de candidatos a termo de
glossário: nomes próprios e termos recorrentes, usando frequência de
palavras capitalizadas que NÃO estão no início de frase (heurística
simples de "provável nome próprio").

Não reproduz trechos de prosa — a saída é só uma lista de
palavras/termos com contagem, para você preencher a tradução ao lado.

Uso:
    /usr/bin/python glossary_candidates.py ../translation/v17/en > glossario_v17.txt
"""

import re
import sys
from collections import Counter
from pathlib import Path

COMMON_WORDS = {
    "I", "The", "A", "An", "But", "And", "Or", "So", "If", "When", "As",
    "It", "He", "She", "They", "We", "You", "There", "Then", "That",
    "This", "These", "Those", "His", "Her", "Their", "Our", "Its",
    "What", "Why", "How", "Who", "Which", "Yes", "No", "Well", "Now",
    "Still", "Even", "Just", "Perhaps", "Maybe", "Suddenly", "After",
    "Before", "Once", "Here", "Chapter", "Page", "Sure", "Right", "Okay",
    "Instead", "Meanwhile", "However", "Therefore", "Besides", "Indeed",
    "Of", "In", "On", "At", "For", "With", "Without", "Not", "All",
    "Some", "Many", "Few", "Every", "Each", "Both", "Either", "Neither",
}


def find_candidates(text_dir):
    files = sorted(Path(text_dir).glob("*.txt"))

    counts = Counter()

    for f in files:
        text = f.read_text(encoding="utf-8")
        # separa em "sentenças" grosseiramente por pontuação forte
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sentence in sentences:
            words = sentence.split()
            for i, w in enumerate(words):
                clean = re.sub(r"[^\w’'-]", "", w)
                if not clean or not clean[0].isupper():
                    continue
                if clean in COMMON_WORDS:
                    continue
                if i == 0:
                    # primeira palavra da "sentença": ambíguo, ignora
                    continue
                if clean.isupper() and len(clean) <= 4:
                    # provável sigla/ênfase (THE, ALL caps curtos)
                    continue
                counts[clean] += 1

    return counts


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: glossary_candidates.py <dir_com_txts>")
        sys.exit(1)

    counts = find_candidates(sys.argv[1])

    for word, n in counts.most_common(80):
        print(f"{n:4d}  {word}")
