# -*- coding: utf-8 -*-
"""Recuperação de trechos do livro de regras (RAG local, sem dependências).

O texto completo do livro fica em livro_texto/livro.txt (extraído do PDF).
A busca divide o livro em janelas de parágrafos e pontua por sobreposição
de termos normalizados, retornando os melhores trechos.
"""
import re
import os
import json
import urllib.request
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


def responder(pergunta, info_personagens=""):
    """Monta a resposta do Oráculo usando IA (Groq) com base nos trechos do livro."""
    trechos = buscar(pergunta)
    if not trechos:
        return ("As névoas do Aether estão densas... Não encontrei nada nos registros sobre isso. "
                "Tente reformular sua pergunta usando termos específicos de Easy Fall.")
                
    contexto = "\n\n".join([f"--- Página {t['pagina']} ---\n{t['texto']}" for t in trechos])
    
    prompt = f"""Você é o Oráculo de Opath, o mestre sábio do mundo de Easy Fall RPG.
Responda à pergunta do jogador usando APENAS as regras extraídas do livro abaixo.
Seja imersivo, como um mago antigo respondendo de forma clara e direta às regras.
Se a resposta não estiver no contexto abaixo, diga que as correntes do Aether não lhe revelaram isso.
Sempre cite a página correspondente na sua explicação (ex: "Como descrito na página X...").

[TRECHOS DO LIVRO]
{contexto}

{info_personagens}

[PERGUNTA DO JOGADOR]
{pergunta}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = os.environ.get("GROQ_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "Você é o Oráculo de Opath, especialista em Easy Fall RPG."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result['choices'][0]['message']['content']
    except Exception as e:
        # Fallback para o modo texto em caso de falha na API
        partes = ["(Erro de conexão com o Aether. Aqui estão os trechos brutos:)"]
        for t in trechos:
            corpo = t["texto"]
            if len(corpo) > 600:
                corpo = corpo[:600] + " […]"
            partes.append(f"\n📖 Página {t['pagina']}:\n{corpo}")
        return "\n".join(partes)
