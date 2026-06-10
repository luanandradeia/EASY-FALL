# -*- coding: utf-8 -*-
"""Extrai antecedentes (pág. 122-128) e bênçãos (pág. 214-216) para seeds."""
import json, os, re, unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVRO = os.path.join(os.path.dirname(BASE), "livro_texto", "livro.txt")
SEEDS = os.path.join(BASE, "core", "seeds")

ANTECEDENTES = ["Agente de organização", "Agouro", "Aristocrata", "Artista",
                "Assistente Magitec", "Caçador", "Comerciante", "Contrabandista",
                "Cosmopolita", "Detetive", "DEvedor", "Erudito", "Estudioso Feérico",
                "Herói do Povo", "Juramentado", "Militar", "Navegante", "Procurado",
                "Proletário", "Viajante Intrépido"]


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def load(a, b):
    with open(LIVRO, encoding="utf-8") as f:
        t = f.read()
    parts = re.split(r"===== PAGINA (\d+) =====", t)
    pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
    txt = "".join(pages[p] for p in range(a, b))
    txt = re.sub(r"^\s*\d+\s*\|\s*Capítulo \d+\s*$", "", txt, flags=re.M)
    txt = re.sub(r"^\s*Capítulo \d+\s*$", "", txt, flags=re.M)
    txt = re.sub(r"^\s*criação de personagem\s*\|\s*\d+\s*$", "", txt, flags=re.M | re.I)
    txt = re.sub(r"^\s*criação de Personagem\s*$", "", txt, flags=re.M)
    txt = re.sub(r"^\s*2\s*$", "", txt, flags=re.M)
    txt = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", txt)
    return txt


def main():
    txt = load(122, 129)
    lines = txt.split("\n")
    idx = []
    alvo = {norm(a): a for a in ANTECEDENTES}
    for i, l in enumerate(lines):
        key = norm(l.strip())
        if key in alvo:
            idx.append((i, alvo[key]))
            del alvo[key]
    antecedentes = []
    for k, (i, nome) in enumerate(idx):
        fim = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
        corpo = "\n".join(lines[i + 1:fim]).strip()
        corpo = re.sub(r"\n{3,}", "\n\n", corpo)
        antecedentes.append({"nome": nome.title() if nome.isupper() else (nome[0].upper() + nome[1:]), "descricao": corpo})
    # corrige "DEvedor"
    for a in antecedentes:
        if a["nome"].lower() == "devedor":
            a["nome"] = "Devedor"
    json.dump(antecedentes, open(os.path.join(SEEDS, "antecedentes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("antecedentes:", len(antecedentes), [a["nome"] for a in antecedentes])

    # Bênçãos: padrão "Nome Da Bênção: texto..." nas páginas 214-217
    btxt = load(214, 218)
    pos = btxt.find("Lista de Bênçãos")
    if pos > 0:
        btxt = btxt[pos + len("Lista de Bênçãos"):]
    pat = re.compile(r"^([A-ZÀ-ÿ][\w’'’À-ÿ,]*(?:[ \-][\wd’'À-ÿ,]+){0,7}):\s", re.M)
    ms = list(pat.finditer(btxt))
    bencaos = []
    for k, m in enumerate(ms):
        fim = ms[k + 1].start() if k + 1 < len(ms) else len(btxt)
        nome = re.sub(r"\s+", " ", m.group(1)).strip()
        if nome.lower().startswith(("alcance", "alvo", "dura", "efeito", "especial", "ataque", "acerto", "gatilho", "componentes", "execu", "ritos", "símbolo", "dogmas", "expia", "bênçãos", "canalizar", "pré-requisito")):
            continue
        corpo = btxt[m.end():fim].strip()
        corpo = re.sub(r"\n{3,}", "\n\n", corpo)
        bencaos.append({"nome": nome, "descricao": corpo[:1500]})
    json.dump(bencaos, open(os.path.join(SEEDS, "bencaos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("bencaos:", len(bencaos), [b["nome"] for b in bencaos])


if __name__ == "__main__":
    main()
