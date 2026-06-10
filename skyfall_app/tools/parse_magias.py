# -*- coding: utf-8 -*-
"""Extrai as magias do texto do livro (páginas 271-302) para magias.json."""
import json, re, unicodedata, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVRO = os.path.join(os.path.dirname(BASE), "livro_texto", "livro.txt")
OUT = os.path.join(BASE, "core", "seeds", "magias.json")

# Lista oficial (página 269-270) — nome: (camada, tipo)
LISTA = {
    "Abraço da Noite": ("truque", "controle"),
    "Barreira de Proteção": ("truque", "controle"),
    "Drenar Fortitude": ("truque", "controle"),
    "Orientação": ("truque", "controle"),
    "Resistência de Ruedim": ("truque", "controle"),
    "Sorriso de Sa'Al": ("truque", "controle"),
    "Corrente Psiônica": ("truque", "ofensivo"),
    "Disparo Arcano": ("truque", "ofensivo"),
    "Lâmina Cósmica": ("truque", "ofensivo"),
    "Mão Esquelética de Brunhil": ("truque", "ofensivo"),
    "Palminha Sagrada": ("truque", "ofensivo"),
    "Raio Elemental": ("truque", "ofensivo"),
    "Ilusão Menor": ("truque", "utilitario"),
    "Luz": ("truque", "utilitario"),
    "Mãos Mágicas": ("truque", "utilitario"),
    "Marca de Sangue": ("truque", "utilitario"),
    "Reparar": ("truque", "utilitario"),
    "Transmutar em Arma": ("truque", "utilitario"),
    "Curar Ferimentos": ("superficial", "controle"),
    "Elo do Destino de Talyiesin": ("superficial", "controle"),
    "Escudo Arcano": ("superficial", "controle"),
    "Escuridão": ("superficial", "controle"),
    "Inspiração Heroica": ("superficial", "controle"),
    "Pele-Casca": ("superficial", "controle"),
    "Profanar Solo": ("superficial", "controle"),
    "Reflexos de Thyesba": ("superficial", "controle"),
    "Restauração Menor": ("superficial", "controle"),
    "Silêncio Sepulcral": ("superficial", "controle"),
    "Sono de Notzferah": ("superficial", "controle"),
    "Sugestão": ("superficial", "controle"),
    "Aríete Elemental": ("superficial", "ofensivo"),
    "Arma Elemental": ("superficial", "ofensivo"),
    "Armamento Espectral": ("superficial", "ofensivo"),
    "Grito Agonizante de Warpinier": ("superficial", "ofensivo"),
    "Infligir Ferimentos": ("superficial", "ofensivo"),
    "Malícia Mental de Fofuxa": ("superficial", "ofensivo"),
    "Manifestação das Profundezas": ("superficial", "ofensivo"),
    "Mísseis Mágicos de Clebinho": ("superficial", "ofensivo"),
    "Presas": ("superficial", "ofensivo"),
    "Raio Brilhoso da Fé": ("superficial", "ofensivo"),
    "Raio do Enfraquecimento": ("superficial", "ofensivo"),
    "Tufão": ("superficial", "ofensivo"),
    "Alarme": ("superficial", "utilitario"),
    "Augúrio": ("superficial", "utilitario"),
    "Compreensão": ("superficial", "utilitario"),
    "Detectar Magia": ("superficial", "utilitario"),
    "Força Anuro": ("superficial", "utilitario"),
    "Imagem Silenciosa": ("superficial", "utilitario"),
    "Manifestar Familiar": ("superficial", "utilitario"),
    "Passo Nebuloso": ("superficial", "utilitario"),
    "Queda Suave": ("superficial", "utilitario"),
    "Simpatia Animal": ("superficial", "utilitario"),
    "Tele-entrega": ("superficial", "utilitario"),
    "Ventriloquismo": ("superficial", "utilitario"),
    "Acalma-multidão": ("rasa", "controle"),
    "Aspecto Aracnoide": ("rasa", "controle"),
    "Cubo Gentil": ("rasa", "controle"),
    "Imobilizar Criatura": ("rasa", "controle"),
    "Invisibilidade da Testemunha": ("rasa", "controle"),
    "Pele de Urodelo": ("rasa", "controle"),
    "Psionismo": ("rasa", "controle"),
    "Velocidade de Enoch": ("rasa", "controle"),
    "Amarras Elementais": ("rasa", "ofensivo"),
    "Asas Douradas de Seraph": ("rasa", "ofensivo"),
    "Bola de Fogo": ("rasa", "ofensivo"),
    "Derreter Mente": ("rasa", "ofensivo"),
    "Desespero das Almas Perdidas": ("rasa", "ofensivo"),
    "Gosma Ácida Amigável": ("rasa", "ofensivo"),
    "Maldição Fúngica de Simon": ("rasa", "ofensivo"),
    "Pó Ruidoso Catalisado": ("rasa", "ofensivo"),
    "Atoleiro Mágico de Dom Guilherme": ("rasa", "utilitario"),
    "Carroça Astral": ("rasa", "utilitario"),
    "Ligação Telepática": ("rasa", "utilitario"),
    "Mapeamento de Brunmul": ("rasa", "utilitario"),
    "Montaria Arcana": ("rasa", "utilitario"),
    "Portal Dimensional": ("rasa", "utilitario"),
    "Revelar Motivação Oculta": ("rasa", "utilitario"),
    "Seraph da Guarda": ("rasa", "utilitario"),
    "Escolher a Proteção": ("profunda", "controle"),
    "Quarteto de Sopro da Ordem": ("profunda", "controle"),
    "Palavras de Poder": ("profunda", "controle"),
    "Regeneração de Mirandinha": ("profunda", "controle"),
    "Carruagem Elemental de Ruedim": ("profunda", "ofensivo"),
    "Ilha Cadente": ("profunda", "ofensivo"),
    "Cone de Peste": ("profunda", "ofensivo"),
    "Raio Ricocheteante de Roberto": ("profunda", "ofensivo"),
    "Atração Gravitacional de Carminha": ("profunda", "utilitario"),
    "Familiar Maior de Telaril": ("profunda", "utilitario"),
    "Grande Mão Arcana": ("profunda", "utilitario"),
    "Porta com P Maiúsculo": ("profunda", "utilitario"),
}

EXEC_MAP = {"A": "ação", "B": "ação bônus", "R": "reação", "N": "1 minuto ou mais", "L": "livre"}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def main():
    with open(LIVRO, encoding="utf-8") as f:
        text = f.read()

    # fatia páginas 271-303
    start = text.index("===== PAGINA 271 =====")
    end = text.index("===== PAGINA 303 =====")
    sec = text[start:end]
    # remove marcadores de página e cabeçalhos/rodapés
    sec = re.sub(r"===== PAGINA \d+ =====", "\n", sec)
    sec = re.sub(r"^\s*\d+\s*\|\s*Capítulo 4\s*$", "", sec, flags=re.M)
    sec = re.sub(r"^\s*magia\s*\|\s*\d+\s*$", "", sec, flags=re.M)
    sec = re.sub(r"^\s*magia\s*$", "", sec, flags=re.M)
    sec = re.sub(r"^\s*Capítulo 4\s*$", "", sec, flags=re.M)
    sec = re.sub(r"^\s*4\s*$", "", sec, flags=re.M)

    lines = sec.split("\n")
    # Junta cabeçalhos quebrados: procura sequência iniciando com ícone e
    # terminando com "<n> pe" em até 3 linhas.
    norm_lista = {norm(k): k for k in LISTA}
    # grafias alternativas no corpo do livro
    norm_lista[norm("Elo do Destino de Taliyesin")] = "Elo do Destino de Talyiesin"
    norm_lista[norm("Escolher Proteção")] = "Escolher a Proteção"
    headers = []  # (line_index_start, line_index_end, nome_oficial, custo, exec_icon)
    i = 0
    while i < len(lines):
        m = re.match(r"^\s*([ABRNL])(?:\s+(.+?))?\s*$", lines[i])
        if m:
            icon = m.group(1)
            acc = m.group(2) or ""
            for j in range(i, min(i + 5, len(lines))):
                if j > i:
                    acc = (acc + " " + lines[j].strip()).strip()
                m2 = re.match(r"^(.*?)\s+(\d+)\s*pe\b", acc, re.I)
                if m2:
                    nome_raw = re.sub(r"\s+", " ", m2.group(1)).strip()
                    key = norm(nome_raw)
                    if key in norm_lista:
                        headers.append((i, j, norm_lista[key], int(m2.group(2)), icon))
                        i = j
                        break
        i += 1

    magias = []
    for idx, (s, e, nome, custo, icon) in enumerate(headers):
        body_start = e + 1
        body_end = headers[idx + 1][0] if idx + 1 < len(headers) else len(lines)
        body = "\n".join(l for l in lines[body_start:body_end])
        # limpeza leve: des-hifeniza palavras quebradas
        body = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", body)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        camada, tipo = LISTA[nome]
        magias.append({
            "nome": nome,
            "camada": camada,
            "tipo": tipo,
            "custo_enfase": custo,
            "execucao": EXEC_MAP.get(icon, icon),
            "descricao": body,
        })

    encontradas = {m["nome"] for m in magias}
    faltando = [n for n in LISTA if n not in encontradas]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(magias, f, ensure_ascii=False, indent=2)
    print(f"{len(magias)} magias extraídas -> {OUT}")
    if faltando:
        print("FALTANDO:", faltando)


if __name__ == "__main__":
    main()
