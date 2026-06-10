# -*- coding: utf-8 -*-
"""Recuperação de trechos do livro de regras (RAG local, sem dependências).

O texto completo do livro fica em livro_texto/livro.txt (extraído do PDF).
A busca divide o livro em janelas de parágrafos e pontua por sobreposição
de termos normalizados, retornando os melhores trechos.
"""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

LIVRO = Path(__file__).resolve().parents[1] / "livro_texto" / "livro.txt"
if not LIVRO.exists():
    LIVRO = Path(__file__).resolve().parents[2] / "livro_texto" / "livro.txt"

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "em",
    "no", "na", "nos", "nas", "que", "como", "para", "por", "com", "e", "ou",
    "se", "ao", "sao", "ser", "tem", "seu", "sua", "funciona", "funcionam",
    "regra", "regras", "sobre", "qual", "quais", "quando", "onde", "porque",
    "pode", "podem", "posso", "voce", "vocês", "eu", "me", "skyfall", "rpg",
}


def normalizar(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]{2,}", t)


@lru_cache(maxsize=1)
def blocos():
    """Divide o livro em blocos de ~40 linhas com referência de página."""
    if not LIVRO.exists():
        return []
    texto = LIVRO.read_text(encoding="utf-8")
    paginas = re.split(r"===== PAGINA (\d+) =====", texto)
    saida = []
    for i in range(1, len(paginas), 2):
        numero = paginas[i]
        linhas = [l for l in paginas[i + 1].split("\n") if l.strip()]
        for j in range(0, len(linhas), 40):
            trecho = "\n".join(linhas[j:j + 46])
            tokens = set(normalizar(trecho)) - STOPWORDS
            saida.append({"pagina": int(numero), "texto": trecho, "tokens": tokens})
    return saida


def buscar(pergunta, top=3):
    termos = [t for t in normalizar(pergunta) if t not in STOPWORDS]
    if not termos:
        return []
    termos_set = set(termos)
    pontuados = []
    for b in blocos():
        inter = termos_set & b["tokens"]
        if not inter:
            continue
        score = len(inter) / len(termos_set)
        # bônus para frase exata
        if len(termos) > 1 and " ".join(termos) in " ".join(normalizar(b["texto"])):
            score += 1
        pontuados.append((score, b))
    pontuados.sort(key=lambda x: -x[0])
    return [b for s, b in pontuados[:top] if s >= 0.3]


def responder(pergunta):
    """Monta a resposta do Oráculo a partir dos trechos do livro."""
    trechos = buscar(pergunta)
    if not trechos:
        return ("Não encontrei nada no livro de regras sobre isso. "
                "Tente reformular usando termos do jogo (ex.: 'fragmentação arcana', "
                "'pontos de ênfase', 'testes de morte').")
    partes = ["Encontrei isto no livro de regras:"]
    for t in trechos:
        corpo = t["texto"]
        corpo = re.sub(r"\s+\n", "\n", corpo)
        if len(corpo) > 1100:
            corpo = corpo[:1100] + " […]"
        partes.append(f"\n📖 Página {t['pagina']}:\n{corpo}")
    return "\n".join(partes)
