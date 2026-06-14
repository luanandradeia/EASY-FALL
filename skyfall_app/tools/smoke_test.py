# -*- coding: utf-8 -*-
"""Smoke test: cria usuário, personagem, percorre todas as telas."""
import os, sys, django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyfall.settings")
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from core import models

User.objects.filter(username="teste").delete()
user = User.objects.create_user("teste", password="opath1234")

c = Client()
ok = c.login(username="teste", password="opath1234")
print("login:", ok)

r = c.post("/personagem/novo/", {
    "nome": "Liesel", "pronomes": "ela/dela", "jogadore": "Andra", "nivel": 3,
    "classe": models.Classe.objects.get(nome="Especialista").pk,
    "legado": models.Legado.objects.get(nome="Anuro").pk,
    "heranca": "Ranin", "melancolia": "O peso do coração",
    "f_for": 1, "f_des": 3, "f_con": 1, "f_int": 2, "f_sab": 0, "f_car": 1,
    "pv_maximo": 24, "pv_atual": 24, "pv_temporario": 0,
    "dados_vida_total": 3, "dados_vida_usados": 0, "catarse": 1,
    "enfase_total": 4, "enfase_atual": 4, "sombra": 0,
    "morte_sucessos": 0, "morte_falhas": 0,
    "reducao_dano": 1, "iniciativa_bonus": 3, "tamanho": "Pequeno",
    "deslocamento": "9 m / 6 q", "trocados": 25, "pecas": 2,
})
print("criar personagem:", r.status_code, r.headers.get("Location"))
p = models.Personagem.objects.get(nome="Liesel")
print("  perícias criadas:", p.pericias.count())
print("  proficiência:", p.proficiencia, "| limite volume:", p.limite_volume,
      "| limite frag:", p.limite_fragmentacao)

# adiciona itens do catálogo
sabre = models.Item.objects.get(nome="Sabre flexível")
couro = models.Item.objects.get(nome="Armadura de couro")
for item in (sabre, couro):
    r = c.post(f"/personagem/{p.pk}/inventario/add/", {"item": item.pk})
    print(f"add {item.nome}:", r.status_code)
e = p.inventario.get(item=sabre)
c.post(f"/personagem/{p.pk}/inventario/{e.pk}/", {"acao": "equipar"})
# encanta com material + sigilo
nacar = models.MaterialEspecial.objects.get(nome="Nácar")
sig = models.Sigilo.objects.filter(tipo="sufixo", equipamento="arma", grau=2).first()
r = c.post(f"/personagem/{p.pk}/inventario/{e.pk}/",
           {"acao": "encantar", "material": nacar.pk, "sigilo_sufixo": sig.pk, "sigilo_prefixo": ""})
e.refresh_from_db()
print("encantar:", r.status_code, "| nome completo:", e.nome_completo, "| frag:", e.fragmentos)

# aprende magia e habilidade
magia = models.Magia.objects.get(nome="Disparo Arcano")
hab = models.Habilidade.objects.get(nome="Produzir Soro")
c.post(f"/personagem/{p.pk}/catalogo/", {"tipo": "magia", "id": magia.pk})
c.post(f"/personagem/{p.pk}/catalogo/", {"tipo": "habilidade", "id": hab.pk})
print("magias:", list(p.magias.values_list("nome", flat=True)),
      "| habilidades:", list(p.habilidades.values_list("nome", flat=True)))

# item customizado
r = c.post("/catalogo/item/novo/", {
    "nome": "Lâmina de Aetherium Bruto", "tipo": "arma", "categoria": "regional",
    "empunhadura": "uma_mao", "preco": 500, "volume": 2, "dano": "1d10",
    "alcance": "", "reducao_dano": 0, "descritores_texto": "LEVE, MÁGICO, LETAL",
    "descricao": "Arma criada pelo jogador — só aparece para ele."})
custom = models.Item.objects.filter(criado_por=user).first()
print("item custom:", r.status_code, "→", custom)

# ajuste rápido (PV -3)
r = c.post(f"/personagem/{p.pk}/ajuste/", {"campo": "pv_atual", "delta": -3})
print("ajuste PV:", r.status_code, r.json())

# todas as telas
for url in ["/", f"/personagem/{p.pk}/", f"/personagem/{p.pk}/inventario/",
            f"/personagem/{p.pk}/cena/", f"/personagem/{p.pk}/catalogo/",
            f"/personagem/{p.pk}/notas/",
            f"/personagem/{p.pk}/catalogo/?secao=magias", f"/personagem/{p.pk}/catalogo/?secao=sigilos", "/oraculo/"]:
    r = c.get(url)
    print(f"GET {url}: {r.status_code}")

# oráculo
r = c.post("/oraculo/perguntar/", {"pergunta": "como funciona a fragmentação arcana?"})
print("oráculo:", r.status_code, "| resposta contém 'Página':", "Página" in r.json()["resposta"])
print("\nSMOKE TEST OK")
