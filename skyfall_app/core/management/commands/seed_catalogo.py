import json
from pathlib import Path

from django.core.management.base import BaseCommand

from core import models

SEEDS = Path(__file__).resolve().parents[2] / "seeds"


def carregar(nome):
    caminho = SEEDS / f"{nome}.json"
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


class Command(BaseCommand):
    help = "Carrega os catálogos oficiais do livro de regras Skyfall RPG no banco."

    def handle(self, *args, **options):
        total = 0

        # Descritores primeiro (armas referenciam eles)
        for d in carregar("descritores"):
            obj, criado = models.Descritor.objects.update_or_create(
                nome=d["nome"], criado_por=None, defaults={"descricao": d["descricao"]})
            total += criado

        def descritor_objs(nomes):
            objs = []
            for n in nomes:
                base = n.split("(")[0].strip().rstrip(":").upper()
                obj = models.Descritor.objects.filter(nome__iexact=base, criado_por=None).first()
                if obj:
                    objs.append(obj)
            return objs

        for a in carregar("armas"):
            obj, criado = models.Item.objects.update_or_create(
                nome=a["nome"], tipo="arma", criado_por=None,
                defaults={
                    "categoria": a.get("categoria", ""),
                    "empunhadura": a.get("empunhadura", ""),
                    "preco": a.get("preco"),
                    "volume": a.get("volume") or 0,
                    "dano": a.get("dano", ""),
                    "alcance": a.get("alcance", ""),
                    "descricao": a.get("descricao", ""),
                    "descritores_texto": ", ".join(a.get("descritores", [])),
                })
            obj.descritores.set(descritor_objs(a.get("descritores", [])))
            total += criado

        for a in carregar("armaduras"):
            tipo = "escudo" if a.get("categoria") == "escudo" else "armadura"
            obj, criado = models.Item.objects.update_or_create(
                nome=a["nome"], tipo=tipo, criado_por=None,
                defaults={
                    "categoria": a.get("categoria", ""),
                    "preco": a.get("preco"),
                    "volume": a.get("volume") or 0,
                    "reducao_dano": a.get("reducao_dano") or 0,
                    "descricao": a.get("descricao", ""),
                    "descritores_texto": ", ".join(a.get("descritores", [])),
                })
            obj.descritores.set(descritor_objs(a.get("descritores", [])))
            total += criado

        for e in carregar("equipamentos"):
            _, criado = models.Item.objects.update_or_create(
                nome=e["nome"], tipo=e.get("tipo", "equipamento") if e.get("tipo") in
                ("municao", "servico", "transporte") else "equipamento", criado_por=None,
                defaults={"preco": e.get("preco"), "volume": e.get("volume") or 0,
                          "descricao": e.get("descricao", "")})
            total += criado

        for c in carregar("consumiveis"):
            _, criado = models.Item.objects.update_or_create(
                nome=c["nome"], tipo="consumivel", criado_por=None,
                defaults={"preco": c.get("preco"), "volume": c.get("volume") or 0,
                          "descricao": c.get("descricao", "")})
            total += criado

        for m in carregar("magitech"):
            _, criado = models.Item.objects.update_or_create(
                nome=m["nome"], tipo="magitech", criado_por=None,
                defaults={"preco": m.get("preco"), "volume": m.get("volume") or 0,
                          "descricao": m.get("descricao", ""),
                          "nome_registrado": m.get("nome_registrado", "")})
            total += criado

        for s in carregar("sinapses"):
            _, criado = models.Sinapse.objects.update_or_create(
                nome=s["nome"], criado_por=None,
                defaults={"raridade": s.get("raridade", "comum"),
                          "multiplicador": s.get("multiplicador", 1),
                          "descricao": s.get("descricao", "")})
            total += criado

        for m in carregar("materiais"):
            _, criado = models.MaterialEspecial.objects.update_or_create(
                nome=m["nome"], criado_por=None,
                defaults={"efeito_resumo": m.get("efeito_resumo", ""),
                          "aumento_preco": m.get("aumento_preco", 300),
                          "descricao": m.get("descricao", "")})
            total += criado

        for s in carregar("sigilos"):
            _, criado = models.Sigilo.objects.update_or_create(
                nome=s["nome"], equipamento=s.get("equipamento", "arma"), criado_por=None,
                defaults={"tipo": s.get("tipo", "prefixo"), "grau": s.get("grau", 1),
                          "disparo": s.get("disparo", ""), "cargas": s.get("cargas", 2),
                          "efeito": s.get("efeito", ""), "imbuindo": s.get("imbuindo", ""),
                          "descricao": s.get("efeito", "")})
            total += criado

        for m in carregar("magias"):
            _, criado = models.Magia.objects.update_or_create(
                nome=m["nome"], criado_por=None,
                defaults={"camada": m.get("camada", "truque"), "tipo": m.get("tipo", "utilitario"),
                          "custo_enfase": m.get("custo_enfase", 0),
                          "execucao": m.get("execucao", "ação"),
                          "descricao": m.get("descricao", "")})
            total += criado

        for h in carregar("habilidades"):
            _, criado = models.Habilidade.objects.update_or_create(
                nome=h["nome"], fonte_nome=h.get("fonte_nome", ""), criado_por=None,
                defaults={"custo_enfase": h.get("custo_enfase", 0),
                          "execucao": h.get("execucao", "ação"),
                          "fonte_tipo": h.get("fonte_tipo", "outro"),
                          "descricao": h.get("descricao", "")})
            total += criado

        for p in carregar("pericias"):
            _, criado = models.Pericia.objects.update_or_create(
                nome=p["nome"], criado_por=None,
                defaults={"descricao": p.get("descricao", "")})
            total += criado

        for c in carregar("condicoes"):
            _, criado = models.Condicao.objects.update_or_create(
                nome=c["nome"], criado_por=None,
                defaults={"descricao": c.get("descricao", "")})
            total += criado

        simples = [("legados", models.Legado), ("maldicoes", models.Maldicao),
                   ("classes", models.Classe), ("trilhas", models.Trilha)]
        for arquivo, modelo in simples:
            for s in carregar(arquivo):
                texto = s.get("texto", "")
                _, criado = modelo.objects.update_or_create(
                    nome=s["nome"], criado_por=None,
                    defaults={"texto": texto, "descricao": texto[:400]})
                total += criado

        for a in carregar("antecedentes"):
            _, criado = models.Antecedente.objects.update_or_create(
                nome=a["nome"], criado_por=None,
                defaults={"descricao": a.get("descricao", "")})
            total += criado

        for b in carregar("bencaos"):
            _, criado = models.Bencao.objects.update_or_create(
                nome=b["nome"], criado_por=None,
                defaults={"descricao": b.get("descricao", "")})
            total += criado

        contagens = {
            "Itens": models.Item.objects.count(),
            "Magias": models.Magia.objects.count(),
            "Sigilos": models.Sigilo.objects.count(),
            "Habilidades": models.Habilidade.objects.count(),
            "Perícias": models.Pericia.objects.count(),
            "Condições": models.Condicao.objects.count(),
            "Legados": models.Legado.objects.count(),
            "Maldições": models.Maldicao.objects.count(),
            "Classes": models.Classe.objects.count(),
            "Trilhas": models.Trilha.objects.count(),
            "Antecedentes": models.Antecedente.objects.count(),
            "Bênçãos": models.Bencao.objects.count(),
            "Descritores": models.Descritor.objects.count(),
            "Sinapses": models.Sinapse.objects.count(),
            "Materiais": models.MaterialEspecial.objects.count(),
        }
        self.stdout.write(self.style.SUCCESS(f"{total} novos registros criados."))
        for k, v in contagens.items():
            self.stdout.write(f"  {k}: {v}")
