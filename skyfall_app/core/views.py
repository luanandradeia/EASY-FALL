from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import forms, models


def registrar(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("personagens")
    else:
        form = UserCreationForm()
    return render(request, "registration/registrar.html", {"form": form})


def _meu(request, pk):
    return get_object_or_404(models.Personagem, pk=pk, user=request.user)


def _visiveis(model, user):
    """Catálogo oficial + criações do próprio usuário."""
    return model.objects.filter(Q(criado_por=None) | Q(criado_por=user))


@login_required
def personagens(request):
    return render(request, "core/personagens.html",
                  {"personagens": request.user.personagens.all()})


@login_required
def personagem_novo(request):
    if request.method == "POST":
        form = forms.PersonagemForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.save()
            # cria as perícias padrão do livro
            for per in models.Pericia.objects.filter(criado_por=None):
                models.PericiaPersonagem.objects.create(
                    personagem=p, pericia=per, atributo=per.atributo_padrao)
            messages.success(request, f"{p.nome} chegou em Opath!")
            return redirect("ficha", pk=p.pk)
    else:
        form = forms.PersonagemForm()
    return render(request, "core/personagem_form.html", {"form": form, "titulo": "Nova Personagem"})


@login_required
def personagem_editar(request, pk):
    p = _meu(request, pk)
    if request.method == "POST":
        form = forms.PersonagemForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            return redirect("ficha", pk=p.pk)
    else:
        form = forms.PersonagemForm(instance=p)
    return render(request, "core/personagem_form.html",
                  {"form": form, "titulo": f"Editar — {p.nome}", "personagem": p})


@login_required
@require_POST
def personagem_excluir(request, pk):
    p = _meu(request, pk)
    p.delete()
    return redirect("personagens")


@login_required
def ficha(request, pk):
    p = _meu(request, pk)
    atributos = [(s, v, 10 + v + p.proficiencia) for s, v in p.atributos.items()]
    return render(request, "core/ficha.html", {
        "p": p, "tela": "ficha", "atributos": atributos,
        "pericias": p.pericias.select_related("pericia").order_by("pericia__nome"),
    })


CAMPOS_AJUSTE = {
    "pv_atual", "pv_temporario", "catarse", "enfase_atual", "sombra",
    "dados_vida_usados", "morte_sucessos", "morte_falhas", "trocados", "pecas",
}

LIMITES = {"catarse": (0, 5), "morte_sucessos": (0, 3), "morte_falhas": (0, 3)}


@login_required
@require_POST
def ajuste_rapido(request, pk):
    """Contadores (+/-) da ficha e do modo cena, via fetch JS."""
    p = _meu(request, pk)
    campo = request.POST.get("campo")
    if campo not in CAMPOS_AJUSTE:
        return JsonResponse({"erro": "campo inválido"}, status=400)
    try:
        delta = int(request.POST.get("delta", 0))
        valor = getattr(p, campo) + delta
    except (TypeError, ValueError):
        return JsonResponse({"erro": "delta inválido"}, status=400)
    minimo, maximo = LIMITES.get(campo, (0, 9999))
    if campo == "pv_atual":
        maximo = p.pv_maximo
    if campo == "enfase_atual":
        maximo = p.enfase_total
    if campo == "dados_vida_usados":
        maximo = p.dados_vida_total
    valor = max(minimo, min(maximo, valor))
    setattr(p, campo, valor)
    p.save(update_fields=[campo])
    return JsonResponse({"campo": campo, "valor": valor})


@login_required
@require_POST
def pericia_toggle(request, pk):
    p = _meu(request, pk)
    pp = get_object_or_404(models.PericiaPersonagem, pk=request.POST.get("id"), personagem=p)
    estado = request.POST.get("estado")  # nenhum -> prof -> expert -> nenhum
    pp.proficiente = estado in ("prof", "expert")
    pp.expert = estado == "expert"
    if request.POST.get("atributo") in dict(models.Pericia.ATRIBUTOS):
        pp.atributo = request.POST["atributo"]
    pp.save()
    return JsonResponse({"ok": True, "bonus": pp.bonus})


@login_required
def inventario(request, pk):
    p = _meu(request, pk)
    itens_catalogo = _visiveis(models.Item, request.user)
    filtro = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "")
    if filtro:
        itens_catalogo = itens_catalogo.filter(nome__icontains=filtro)
    if tipo:
        itens_catalogo = itens_catalogo.filter(tipo=tipo)
    return render(request, "core/inventario.html", {
        "p": p, "tela": "inventario",
        "entradas": p.inventario.select_related("item", "material", "sigilo_prefixo", "sigilo_sufixo"),
        "catalogo": itens_catalogo[:80],
        "filtro": filtro, "tipo": tipo,
        "tipos": models.Item.TIPOS,
        "materiais": models.MaterialEspecial.objects.filter(criado_por=None),
        "sigilos": models.Sigilo.objects.filter(criado_por=None),
        "form_item": forms.ItemCustomForm(),
    })


@login_required
@require_POST
def inventario_add(request, pk):
    p = _meu(request, pk)
    item = get_object_or_404(
        _visiveis(models.Item, request.user), pk=request.POST.get("item"))
    entrada, criada = p.inventario.get_or_create(item=item, defaults={"quantidade": 1})
    if not criada:
        entrada.quantidade += 1
        entrada.save(update_fields=["quantidade"])
    messages.success(request, f"{item.nome} adicionado ao inventário.")
    return redirect("inventario", pk=p.pk)


@login_required
@require_POST
def inventario_update(request, pk, entrada):
    p = _meu(request, pk)
    e = get_object_or_404(models.InventarioEntrada, pk=entrada, personagem=p)
    acao = request.POST.get("acao")
    if acao == "remover":
        e.delete()
    elif acao == "equipar":
        e.equipado = not e.equipado
        e.save(update_fields=["equipado"])
    elif acao == "qtd":
        try:
            e.quantidade = max(1, int(request.POST.get("quantidade", 1)))
        except (TypeError, ValueError):
            pass
        e.save(update_fields=["quantidade"])
    elif acao == "encantar":
        for campo, modelo in [("sigilo_prefixo", models.Sigilo), ("sigilo_sufixo", models.Sigilo),
                              ("material", models.MaterialEspecial)]:
            valor = request.POST.get(campo)
            setattr(e, campo, modelo.objects.filter(pk=valor).first() if valor else None)
        frag = 0
        for s in (e.sigilo_prefixo, e.sigilo_sufixo):
            if s:
                frag += s.grau
        e.fragmentos = frag
        e.save()
    return redirect("inventario", pk=p.pk)


@login_required
def cena(request, pk):
    p = _meu(request, pk)
    armas = (p.inventario.filter(equipado=True, item__tipo="arma")
             .select_related("item", "material", "sigilo_prefixo", "sigilo_sufixo"))
    return render(request, "core/cena.html", {
        "p": p, "tela": "cena",
        "armas": armas,
        "magias": p.magias.all().order_by("camada", "nome"),
        "habilidades": p.habilidades.all(),
        "pericias": p.pericias.select_related("pericia").order_by("pericia__nome"),
    })


@login_required
def grimorio(request, pk):
    """Seleciona magias e habilidades do catálogo para a personagem."""
    p = _meu(request, pk)
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        obj_id = request.POST.get("id")
        if tipo == "magia":
            m = get_object_or_404(_visiveis(models.Magia, request.user), pk=obj_id)
            if p.magias.filter(pk=m.pk).exists():
                p.magias.remove(m)
            else:
                p.magias.add(m)
        elif tipo == "habilidade":
            h = get_object_or_404(_visiveis(models.Habilidade, request.user), pk=obj_id)
            if p.habilidades.filter(pk=h.pk).exists():
                p.habilidades.remove(h)
            else:
                p.habilidades.add(h)
        return redirect(f"{request.path}?{request.GET.urlencode()}")

    q = request.GET.get("q", "").strip()
    camada = request.GET.get("camada", "")
    magias = _visiveis(models.Magia, request.user)
    habilidades = _visiveis(models.Habilidade, request.user)
    if q:
        magias = magias.filter(nome__icontains=q)
        habilidades = habilidades.filter(nome__icontains=q)
    if camada:
        magias = magias.filter(camada=camada)
    return render(request, "core/grimorio.html", {
        "p": p, "tela": "grimorio",
        "magias": magias, "habilidades": habilidades,
        "minhas_magias": set(p.magias.values_list("pk", flat=True)),
        "minhas_habilidades": set(p.habilidades.values_list("pk", flat=True)),
        "q": q, "camada": camada, "camadas": models.Magia.CAMADAS,
        "form_magia": forms.MagiaCustomForm(),
        "form_habilidade": forms.HabilidadeCustomForm(),
    })


@login_required
def catalogo(request):
    secao = request.GET.get("secao", "armas")
    q = request.GET.get("q", "").strip()
    user = request.user

    def filtra(qs):
        return qs.filter(nome__icontains=q) if q else qs

    contexto = {"tela": "catalogo", "secao": secao, "q": q}
    secoes = {
        "armas": filtra(_visiveis(models.Item, user).filter(tipo="arma")),
        "armaduras": filtra(_visiveis(models.Item, user).filter(tipo__in=["armadura", "escudo"])),
        "equipamentos": filtra(_visiveis(models.Item, user).filter(
            tipo__in=["equipamento", "municao", "servico", "transporte"])),
        "consumiveis": filtra(_visiveis(models.Item, user).filter(tipo="consumivel")),
        "magitech": filtra(_visiveis(models.Item, user).filter(tipo="magitech")),
        "magias": filtra(_visiveis(models.Magia, user)),
        "habilidades": filtra(_visiveis(models.Habilidade, user)),
        "sigilos": filtra(_visiveis(models.Sigilo, user)),
        "sinapses": filtra(models.Sinapse.objects.all()),
        "materiais": filtra(models.MaterialEspecial.objects.all()),
        "pericias": filtra(models.Pericia.objects.all()),
        "condicoes": filtra(models.Condicao.objects.all()),
        "descritores": filtra(models.Descritor.objects.all()),
        "legados": filtra(models.Legado.objects.all()),
        "maldicoes": filtra(models.Maldicao.objects.all()),
        "classes": filtra(models.Classe.objects.all()),
        "trilhas": filtra(models.Trilha.objects.all()),
        "antecedentes": filtra(models.Antecedente.objects.all()),
        "bencaos": filtra(models.Bencao.objects.all()),
    }
    contexto["resultados"] = secoes.get(secao, secoes["armas"])
    contexto["nomes_secoes"] = [
        ("armas", "Armas"), ("armaduras", "Armaduras"), ("equipamentos", "Equipamentos"),
        ("consumiveis", "Consumíveis"), ("magitech", "Magitech"), ("magias", "Magias"),
        ("habilidades", "Habilidades"), ("sigilos", "Sigilos"), ("sinapses", "Sinapses"),
        ("materiais", "Materiais"), ("pericias", "Perícias"), ("condicoes", "Condições"),
        ("descritores", "Descritores"), ("legados", "Legados"), ("maldicoes", "Maldições"),
        ("classes", "Classes"), ("trilhas", "Trilhas"), ("antecedentes", "Antecedentes"),
        ("bencaos", "Bênçãos"),
    ]
    return render(request, "core/catalogo.html", contexto)


def _criar_custom(request, form_cls, template_titulo, redireciona):
    if request.method == "POST":
        form = form_cls(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.criado_por = request.user
            obj.save()
            messages.success(request, f"{obj.nome} criado!")
            destino = request.POST.get("next") or redireciona
            return redirect(destino)
    else:
        form = form_cls()
    return render(request, "core/custom_form.html",
                  {"form": form, "titulo": template_titulo, "tela": "catalogo"})


@login_required
def item_novo(request):
    return _criar_custom(request, forms.ItemCustomForm, "Criar Item Customizado", "/catalogo/?secao=armas")


@login_required
def magia_nova(request):
    return _criar_custom(request, forms.MagiaCustomForm, "Criar Magia Customizada", "/catalogo/?secao=magias")


@login_required
def habilidade_nova(request):
    return _criar_custom(request, forms.HabilidadeCustomForm, "Criar Habilidade Customizada", "/catalogo/?secao=habilidades")
