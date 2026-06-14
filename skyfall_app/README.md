# Skyfall RPG — Companion App (Django + SQLite)

Sistema web mobile-first para jogadores e Mestres de Skyfall RPG, conforme a
documentação técnica oficial: Python/Django, SQLite, monolito modular.

## Rodando localmente

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_catalogo
python manage.py runserver
```

Acesse http://127.0.0.1:8000 — crie sua conta em "Registre-se".
Admin: http://127.0.0.1:8000/admin (usuário `admin` / senha `admin1234` — troque!).
Usuário de teste: `teste` / `opath1234` (personagem Liesel já criada).

## Com Docker

```bash
docker compose up --build
```

O banco fica em `db_data/db.sqlite3` (volume persistente).

## O que tem dentro

- **Login / Registro** — django.contrib.auth.
- **Ficha** — atributos com proteções automáticas (10 + atributo + proficiência),
  PV, catarse (máx 5), ênfase, sombra, dados de vida, testes de morte e perícias
  com ciclo proficiente → expert.
- **Inventário** — barra de volume (tabela 3-1 do livro), fragmentação arcana
  (CAR + 2×proficiência), carteira T$/P$, encantamento de itens com materiais
  especiais e sigilos (prefixo/sufixo, fragmentos automáticos pelo grau).
- **Modo Cena** — rolagens 1d20 com vantagem/desvantagem, ataques das armas
  equipadas, dano por fórmula (ex.: 2d6+1), cartões de magias/habilidades com
  gasto de PE em um toque.
- **Grimório** — aprender/remover magias e habilidades do catálogo.
- **Catálogo** — 19 seções extraídas do livro oficial (466 registros):
  armas (46), armaduras/escudos, equipamentos, consumíveis, magitech, magias (90),
  habilidades (33), sigilos (57), sinapses, materiais, perícias, condições,
  descritores, legados (11), maldições, classes, trilhas (18), antecedentes (20),
  bênçãos (30).
- **Conteúdo customizado** — qualquer jogador pode criar arma/item, magia ou
  habilidade própria; aparece marcado como CUSTOM só para quem criou, lado a
  lado com o catálogo oficial.
- **Oráculo de Opath** — chatbot de regras que busca no texto completo do livro
  (`livro_texto/livro.txt`) e responde com trechos e número de página (RAG local,
  sem custo de API; chave LLM opcional via env `LLM_API_KEY` para evolução).

## Re-extração dos catálogos

Os seeds em `core/seeds/*.json` foram extraídos do PDF do livro. Os scripts de
extração estão em `tools/` (`parse_magias.py`, `parse_secoes.py`,
`parse_antecedentes.py`) e podem ser rodados de novo se o texto do livro mudar.
