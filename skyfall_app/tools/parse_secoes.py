# -*- coding: utf-8 -*-
"""Fatia o livro em seções (legados, maldições, classes, trilhas, antecedentes,
bênçãos) e extrai habilidades ativáveis (custo em PE) para seeds JSON."""
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVRO = os.path.join(os.path.dirname(BASE), "livro_texto", "livro.txt")
SEEDS = os.path.join(BASE, "core", "seeds")

# (nome, página TOC) — fatiamos de toc+1 até o início da próxima seção
LEGADOS = [("Anuro", 66), ("Draco", 70), ("Elfe", 74), ("Gnomo", 78), ("Humani", 82),
           ("Kishin", 86), ("Sanguires", 90), ("Tatsunoko", 94), ("Tôra", 98),
           ("Urodelo", 102), ("Walshie", 106), ("__fim", 110)]
MALDICOES = [("Aetherídeo", 112), ("Górgon", 114), ("Retornado", 116), ("Sombrio", 118), ("__fim", 120)]
CLASSES = [("Combatente", 130), ("Especialista", 138), ("Ocultista", 146), ("__fim", 152)]
TRILHAS = [("Alquimista", 156), ("Artesão de Guilda", 160), ("Assassino", 162),
           ("Cavaleiro Tóptero", 164), ("Comandante", 168), ("Devoto", 170),
           ("Elementalista", 172), ("Guerreiro Koi", 176), ("Herdeiro Ancestral", 179),
           ("Magitécnico", 182), ("Malandro", 186), ("Mestre das Armas", 188),
           ("Mestre das Feras", 190), ("Necromante", 193), ("Pactuado", 197),
           ("Protetor dos Ermos", 200), ("Pugilista", 202), ("Vendedor Ambulante", 204),
           ("__fim", 208)]


def load_pages():
    with open(LIVRO, encoding="utf-8") as f:
        text = f.read()
    pages = {}
    parts = re.split(r"===== PAGINA (\d+) =====", text)
    for i in range(1, len(parts), 2):
        pages[int(parts[i])] = parts[i + 1]
    return pages


def clean(t):
    t = re.sub(r"^\s*\d+\s*\|\s*Capítulo \d+\s*$", "", t, flags=re.M)
    t = re.sub(r"^\s*Capítulo \d+\s*$", "", t, flags=re.M)
    t = re.sub(r"^\s*criação de personagem\s*\|\s*\d+\s*$", "", t, flags=re.M | re.I)
    t = re.sub(r"^\s*criação de Personagem\s*$", "", t, flags=re.M)
    t = re.sub(r"^\s*\d{1,2}\s*$", "", t, flags=re.M)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def slice_secoes(pages, lista, offset=1):
    out = []
    for (nome, pg), (_, prox) in zip(lista, lista[1:]):
        txt = "".join(pages.get(p, "") for p in range(pg + offset, prox + offset))
        out.append({"nome": nome, "texto": clean(txt)})
    return out


HAB_RE = re.compile(r"^\s*([ABRNL])\s+([A-ZÀ-ÿ][\wÀ-ÿ'’\- ]{2,48}?)\s+(\d+)\s*PE\s*$",
                    re.M | re.I)


def extrai_habilidades(secoes, fonte_tipo):
    habs = []
    for sec in secoes:
        txt = sec["texto"]
        matches = list(HAB_RE.finditer(txt))
        for k, m in enumerate(matches):
            fim = matches[k + 1].start() if k + 1 < len(matches) else min(len(txt), m.end() + 900)
            corpo = txt[m.end():fim].strip()
            # corta no próximo título de seção evidente
            corte = re.search(r"\n[A-ZÀ-ÿ][a-zà-ÿ]+(?: [A-Za-zà-ÿ]+){0,4}\n(?=[A-ZÀ-ÿ“\"])", corpo)
            nome = re.sub(r"\s+", " ", m.group(2)).strip().title()
            execucao = {"A": "ação", "B": "ação bônus", "R": "reação", "N": "1 minuto+", "L": "livre"}[m.group(1).upper()]
            habs.append({
                "nome": nome,
                "custo_enfase": int(m.group(3)),
                "execucao": execucao,
                "fonte_tipo": fonte_tipo,
                "fonte_nome": sec["nome"],
                "descricao": corpo[:1200],
            })
    return habs


def main():
    pages = load_pages()
    os.makedirs(SEEDS, exist_ok=True)

    legados = slice_secoes(pages, LEGADOS)
    maldicoes = slice_secoes(pages, MALDICOES)
    classes = slice_secoes(pages, CLASSES)
    trilhas = slice_secoes(pages, TRILHAS)

    json.dump(legados, open(os.path.join(SEEDS, "legados.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(maldicoes, open(os.path.join(SEEDS, "maldicoes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(classes, open(os.path.join(SEEDS, "classes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(trilhas, open(os.path.join(SEEDS, "trilhas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    habs = []
    habs += extrai_habilidades(legados, "legado")
    habs += extrai_habilidades(maldicoes, "maldicao")
    habs += extrai_habilidades(classes, "classe")
    habs += extrai_habilidades(trilhas, "trilha")
    json.dump(habs, open(os.path.join(SEEDS, "habilidades.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"legados={len(legados)} maldicoes={len(maldicoes)} classes={len(classes)} trilhas={len(trilhas)} habilidades={len(habs)}")
    for h in habs:
        print(f"  [{h['fonte_tipo']}/{h['fonte_nome']}] {h['nome']} ({h['custo_enfase']} PE)")


if __name__ == "__main__":
    main()
