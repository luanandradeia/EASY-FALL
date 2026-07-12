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
    is_admin = request.user.is_superuser or request.user.username.lower() == 'admin'
    p = get_object_or_404(models.Personagem, pk=pk)
    
    # Pode acessar se for dono ou admin
    if p.user == request.user or is_admin:
        p.is_readonly = False
    else:
        # Se não for dono nem admin, checa se é o mestre da mesa atual do personagem
        if p.mesa and p.mesa.mestre == request.user:
            p.is_readonly = True
        else:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Você não tem acesso a este personagem.")
            
    if request.method == "POST" and getattr(p, 'is_readonly', False):
        # Permite salvar apenas a tela de logs e ocultar personagem no modo visualização
        if request.POST.get("campo") not in ["logs", "oculto"]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Modo apenas visualização.")
    return p


def _visiveis(model, user):
    """Catálogo oficial + criações do próprio usuário."""
    return model.objects.filter(Q(criado_por=None) | Q(criado_por=user))


@login_required
def personagens(request):
    is_mestre = request.user.is_superuser or request.user.username.lower() == 'admin'
    logs_gerais = []
    
    if is_mestre:
        qs = models.Personagem.objects.all().select_related("user", "classe", "legado", "trilha").order_by("oculto", "nome")
        logs_gerais = models.RegistroLog.objects.select_related("personagem").order_by("-criado_em")[:100]
    else:
        qs = request.user.personagens.filter(oculto=False).select_related("classe", "legado", "trilha").order_by("nome")
        
    template_name = "core/_personagens_conteudo.html" if request.GET.get("ajax") else "core/personagens.html"
    return render(request, template_name, {
        "personagens": qs,
        "is_mestre": is_mestre,
        "logs_gerais": logs_gerais,
        "tela": "personagens",
    })


@login_required
def mesas(request):
    mesas_mestrando = models.Mesa.objects.filter(mestre=request.user).order_by("-criado_em")
    mesas_jogando = models.Mesa.objects.filter(personagens__user=request.user).distinct().order_by("-criado_em")
    return render(request, "core/mesas.html", {
        "mesas_mestrando": mesas_mestrando,
        "mesas_jogando": mesas_jogando,
        "tela": "mesas"
    })


@login_required
def mesa_nova(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        codigo = request.POST.get("codigo", "").strip()
        if nome and len(codigo) == 4:
            if models.Mesa.objects.filter(codigo=codigo).exists():
                messages.error(request, "Código já em uso.")
            else:
                models.Mesa.objects.create(nome=nome, codigo=codigo, mestre=request.user)
                messages.success(request, "Mesa criada com sucesso!")
                return redirect("mesas")
        else:
            messages.error(request, "Preencha todos os campos corretamente (código de 4 dígitos).")
    return render(request, "core/mesa_nova.html", {"tela": "mesas"})


@login_required
def mesa_entrar(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        personagem_id = request.POST.get("personagem_id")
        if codigo and personagem_id:
            mesa = models.Mesa.objects.filter(codigo=codigo).first()
            personagem = request.user.personagens.filter(pk=personagem_id).first()
            if mesa and personagem:
                personagem.mesa = mesa
                personagem.save(update_fields=["mesa"])
                messages.success(request, f"{personagem.nome} entrou na mesa {mesa.nome}!")
                return redirect("mesas")
            else:
                messages.error(request, "Mesa não encontrada ou personagem inválido.")
        else:
            messages.error(request, "Preencha o código e selecione um personagem.")
            
    personagens = request.user.personagens.filter(oculto=False)
    return render(request, "core/mesa_entrar.html", {"tela": "mesas", "personagens": personagens})


@login_required
def mesa_detalhe(request, pk):
    mesa = get_object_or_404(models.Mesa, pk=pk)
    # Somente o mestre ou os jogadores podem acessar
    if mesa.mestre != request.user and not mesa.personagens.filter(user=request.user).exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Você não faz parte desta mesa.")
        
    personagens = mesa.personagens.select_related('user', 'classe').all()
    return render(request, "core/mesa_detalhe.html", {"tela": "mesas", "mesa": mesa, "personagens": personagens})


@login_required
@require_POST
def mesa_remover_personagem(request, pk, personagem_id):
    mesa = get_object_or_404(models.Mesa, pk=pk)
    personagem = get_object_or_404(models.Personagem, pk=personagem_id, mesa=mesa)
    
    if mesa.mestre == request.user or personagem.user == request.user:
        personagem.mesa = None
        personagem.save(update_fields=["mesa"])
        messages.success(request, f"{personagem.nome} saiu da mesa.")
    else:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Sem permissão.")
        
    return redirect("mesa_detalhe", pk=mesa.pk)


@login_required
def mesa_painel_cena(request, pk):
    mesa = get_object_or_404(models.Mesa, pk=pk, mestre=request.user)
    cena, _ = models.CenaMesa.objects.get_or_create(mesa=mesa)
    
    if request.method == "POST":
        acao = request.POST.get("acao")
        if acao == "toggle_cena":
            cena.ativa = not cena.ativa
            if cena.ativa:
                # Sincroniza participantes com os personagens da mesa automaticamente
                for p in mesa.personagens.all():
                    models.CenaParticipante.objects.get_or_create(
                        cena=cena, personagem=p, defaults={"nome": p.nome, "iniciativa": p.iniciativa_atual}
                    )
            cena.save(update_fields=["ativa"])
        elif acao == "mudar_tipo":
            cena.tipo = request.POST.get("tipo", "combate")
            cena.save(update_fields=["tipo"])
        elif acao == "adicionar_npc":
            nome = request.POST.get("nome", "NPC")
            inic = int(request.POST.get("iniciativa", 0) or 0)
            pv = int(request.POST.get("pv", 10) or 10)
            models.CenaParticipante.objects.create(cena=cena, nome=nome, iniciativa=inic, pv_atual=pv, pv_maximo=pv)
        elif acao == "remover_participante":
            part_id = request.POST.get("participante_id")
            models.CenaParticipante.objects.filter(id=part_id, cena=cena).delete()
        elif acao == "proximo_turno":
            total = cena.participantes.count()
            if total > 0:
                cena.turno_atual = (cena.turno_atual + 1) % total
                cena.save(update_fields=["turno_atual"])
        elif acao == "atualizar_anotacoes":
            cena.anotacoes = request.POST.get("anotacoes", "")
            cena.save(update_fields=["anotacoes"])
            
        return redirect("mesa_painel_cena", pk=mesa.pk)
        
    participantes = cena.participantes.all()
    return render(request, "core/mesa_painel_cena.html", {
        "tela": "mesas", 
        "mesa": mesa, 
        "cena": cena, 
        "participantes": participantes
    })





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
    atributos = [
        (s, p.atributo_valor(s), p.atributo(s), p.protecoes[s], getattr(p, f"p_{s.lower()}"))
        for s in ["FOR", "DES", "CON", "INT", "SAB", "CAR"]
    ]
    return render(request, "core/ficha.html", {
        "p": p, "tela": "ficha", "atributos": atributos,
        "pericias": p.pericias.select_related("pericia").order_by("pericia__nome"),
    })


CAMPOS_AJUSTE = {
    "pv_atual", "pv_temporario", "catarse", "enfase_atual", "sombra",
    "dados_vida_usados", "morte_falhas", "trocados",
    "inspiracao", "p_for", "p_des", "p_con", "p_int", "p_sab", "p_car",
    "agua", "racoes", "desafio_sucessos", "desafio_falhas", "condicoes_ativas",
    "notas_terreno", "diario", "logs", "iniciativa_atual", "reducao_dano",
    "oculto",
}

LIMITES = {"catarse": (0, 99), "morte_falhas": (0, 3), "desafio_sucessos": (0, 10), "desafio_falhas": (0, 10), "catarse": (0, 99), "sombra": (0, 99)}


@login_required
@require_POST
def ajuste_rapido(request, pk):
    """Contadores (+/-) da ficha e do modo cena, via fetch JS."""
    p = _meu(request, pk)
    campo = request.POST.get("campo")
    if campo not in CAMPOS_AJUSTE:
        return JsonResponse({"erro": "campo inválido"}, status=400)
    
    if campo in ("inspiracao", "p_for", "p_des", "p_con", "p_int", "p_sab", "p_car"):
        valor_str = request.POST.get("estado", "").lower()
        valor = valor_str in ("true", "1")
        setattr(p, campo, valor)
        p.save(update_fields=[campo])
        return JsonResponse({"campo": campo, "valor": valor})

    if campo == "condicoes_ativas":
        condicao = request.POST.get("valor", "").strip()
        lista = [c.strip() for c in p.condicoes_ativas.split(",") if c.strip()]
        if condicao in lista:
            lista.remove(condicao)
            models.RegistroLog.objects.create(personagem=p, mensagem=f"Removeu a condição: {condicao}")
        else:
            lista.append(condicao)
            models.RegistroLog.objects.create(personagem=p, mensagem=f"Adquiriu a condição: {condicao}")
        p.condicoes_ativas = ",".join(lista)
        p.save(update_fields=["condicoes_ativas"])
        return JsonResponse({"campo": campo, "valor": p.condicoes_ativas})

    if campo == "notas_terreno":
        p.notas_terreno = request.POST.get("valor", "")
        p.save(update_fields=["notas_terreno"])
        return JsonResponse({"campo": campo, "valor": p.notas_terreno})

    if campo == "diario":
        p.diario = request.POST.get("valor", "")
        p.save(update_fields=["diario"])
        return JsonResponse({"campo": campo, "valor": p.diario})

    if campo == "logs":
        p.logs = request.POST.get("valor", "")
        p.save(update_fields=["logs"])
        return JsonResponse({"campo": campo, "valor": p.logs})

    if campo == "oculto":
        is_oculto = request.POST.get("valor", "false").lower() == "true"
        p.oculto = is_oculto
        models.RegistroLog.objects.create(personagem=p, mensagem="Personagem ocultado" if is_oculto else "Personagem revelado")
        p.save(update_fields=["oculto"])
        return JsonResponse({"campo": campo, "valor": is_oculto})

    try:
        delta = int(request.POST.get("delta", 0))
        if "valor" in request.POST:
            valor = int(request.POST["valor"])
        else:
            valor = getattr(p, campo) + delta
    except (TypeError, ValueError):
        return JsonResponse({"erro": "delta ou valor inválido"}, status=400)
    
    minimo, maximo = LIMITES.get(campo, (0, 9999))
    if campo == "pv_atual":
        maximo = p.pv_maximo
    if campo == "dados_vida_usados":
        maximo = p.dados_vida_total
    if campo in ("enfase_atual", "trocados", "agua", "racoes", "pv_atual", "pv_temporario", "sombra", "catarse"):
        minimo = 0
    
    valor = max(minimo, min(maximo, valor))
    old_valor = getattr(p, campo)
    
    if old_valor != valor:
        nomes = {
            "pv_atual": "PV", "pv_temporario": "PV Temporário", "trocados": "Trocados (T$)", 
            "enfase_atual": "Ênfase", "catarse": "Catarse", "sombra": "Sombra",
            "dados_vida_usados": "Dados de Vida Usados"
        }
        nome_campo = nomes.get(campo, campo)
        
        # Só registra se for um dos campos importantes
        if campo in nomes:
            diff = valor - old_valor
            acao = "Ganhou" if diff > 0 else "Perdeu"
            models.RegistroLog.objects.create(personagem=p, mensagem=f"{acao} {abs(diff)} {nome_campo} (agora: {valor})")

    setattr(p, campo, valor)
    p.save(update_fields=[campo])
    
    # Se for iniciativa, atualiza também a CenaParticipante (se houver cena ativa na mesa)
    if campo == "iniciativa_atual":
        if p.mesa and hasattr(p.mesa, 'cena_atual'):
            part = models.CenaParticipante.objects.filter(cena=p.mesa.cena_atual, personagem=p).first()
            if part:
                part.iniciativa = valor
                part.save(update_fields=["iniciativa"])
                
    return JsonResponse({"campo": campo, "valor": valor})


@login_required
@require_POST
def arma_update(request, pk):
    p = _meu(request, pk)
    entrada_id = request.POST.get("id")
    e = get_object_or_404(models.InventarioEntrada, pk=entrada_id, personagem=p)
    
    atributo = request.POST.get("atributo")
    if atributo in dict(models.Pericia.ATRIBUTOS):
        e.atributo_attack = atributo # Wait, typo in model? checking... 
        # Checking model... it is atributo_ataque.
        e.atributo_ataque = atributo
    
    prof = request.POST.get("proficiente")
    if prof is not None:
        e.proficiente = prof.lower() in ("true", "1")
        
    e.save()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def pericia_toggle(request, pk):
    p = _meu(request, pk)
    pp = get_object_or_404(models.PericiaPersonagem, pk=request.POST.get("id"), personagem=p)
    estado = request.POST.get("estado")  # nenhum -> prof -> expert -> nenhum
    if estado:
        pp.proficiente = estado in ("prof", "expert")
        pp.expert = estado == "expert"
    if request.POST.get("atributo") in dict(models.Pericia.ATRIBUTOS):
        pp.atributo = request.POST["atributo"]
    pp.save()
    return JsonResponse({"ok": True, "bonus": pp.bonus})


@login_required
def inventario(request, pk):
    p = _meu(request, pk)

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        obj_id = request.POST.get("id")
        
        if tipo == "magia":
            m = get_object_or_404(_visiveis(models.Magia, request.user), pk=obj_id)
            p.magias.remove(m)
        elif tipo == "habilidade":
            h = get_object_or_404(_visiveis(models.Habilidade, request.user), pk=obj_id)
            p.habilidades.remove(h)
        return redirect(f"{request.path}?{request.GET.urlencode()}")

    secao = request.GET.get("secao", "todos")
    q = request.GET.get("q", "").strip()

    contexto = {"p": p, "tela": "inventario", "secao": secao, "q": q}
    
    entradas_base = p.inventario.select_related("item", "material", "sigilo_prefixo", "sigilo_sufixo")
    magias_base = p.magias.all()
    habilidades_base = p.habilidades.all()

    if q:
        entradas_base = entradas_base.filter(item__nome__icontains=q)
        magias_base = magias_base.filter(nome__icontains=q)
        habilidades_base = habilidades_base.filter(nome__icontains=q)

    secoes = {
        "armas": entradas_base.filter(item__tipo="arma"),
        "armaduras": entradas_base.filter(item__tipo__in=["armadura", "escudo"]),
        "equipamentos": entradas_base.filter(item__tipo__in=["equipamento", "municao", "servico", "transporte"]),
        "consumiveis": entradas_base.filter(item__tipo="consumivel"),
        "magitech": entradas_base.filter(item__tipo="magitech"),
        "magias": magias_base,
        "habilidades": habilidades_base,
    }
    
    if secao == "todos":
        resultados_list = []
        for k, qs in secoes.items():
            lst = list(qs)
            for obj in lst:
                obj.inventario_secao = k
            resultados_list.extend(lst)
        # Para ordenação mista, os itens usam item.nome, e magias/habilidades usam nome
        resultados_list.sort(key=lambda x: x.item.nome if hasattr(x, 'item') else x.nome)
        contexto["resultados"] = resultados_list
    else:
        contexto["resultados"] = secoes.get(secao, secoes["armas"])
        
    contexto["nomes_secoes"] = [
        ("todos", "Todos"),
        ("armas", "Armas"), ("armaduras", "Armaduras"), ("equipamentos", "Equipamentos"),
        ("consumiveis", "Consumíveis"), ("magitech", "Magitech"), ("magias", "Magias"),
        ("habilidades", "Habilidades"),
    ]
    
    contexto["materiais"] = models.MaterialEspecial.objects.filter(criado_por=None)
    contexto["sigilos"] = models.Sigilo.objects.filter(criado_por=None)
    
    return render(request, "core/inventario.html", contexto)


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
    
    # Dedução automática de moedas
    if item.preco:
        from django.db.models import F
        models.Personagem.objects.filter(pk=p.pk).update(trocados=F('trocados') - item.preco)
        models.RegistroLog.objects.create(personagem=p, mensagem=f"Adquiriu {item.nome} e gastou T$ {item.preco}")
        messages.success(request, f"{item.nome} adicionado. T${item.preco} descontados.")
    else:
        models.RegistroLog.objects.create(personagem=p, mensagem=f"Adquiriu {item.nome}")
        messages.success(request, f"{item.nome} adicionado ao inventário.")
        
    return redirect("inventario", pk=p.pk)


@login_required
@require_POST
def inventario_update(request, pk, entrada):
    p = _meu(request, pk)
    e = get_object_or_404(models.InventarioEntrada, pk=entrada, personagem=p)
    acao = request.POST.get("acao")
    if acao == "remover":
        models.RegistroLog.objects.create(personagem=p, mensagem=f"Removeu {e.item.nome} do inventário")
        e.delete()
    elif acao == "equipar":
        e.equipado = not e.equipado
        estado = "Equipou" if e.equipado else "Desequipou"
        models.RegistroLog.objects.create(personagem=p, mensagem=f"{estado} {e.item.nome}")
        e.save(update_fields=["equipado"])
    elif acao == "qtd":
        try:
            e.quantidade = max(1, int(request.POST.get("quantidade", 1)))
        except (TypeError, ValueError):
            pass
        e.save(update_fields=["quantidade"])
    elif acao == "consumir":
        models.RegistroLog.objects.create(personagem=p, mensagem=f"Consumiu {e.item.nome}")
        if e.quantidade > 1:
            e.quantidade -= 1
            e.save(update_fields=["quantidade"])
        else:
            e.delete()
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
def notas(request, pk):
    p = _meu(request, pk)
    return render(request, "core/notas.html", {"p": p, "tela": "notas"})


@login_required
def logs(request, pk):
    p = _meu(request, pk)
    return render(request, "core/logs.html", {"p": p, "tela": "logs"})


@login_required
def cena(request, pk):
    p = _meu(request, pk)
    armas = (p.inventario.filter(equipado=True, item__tipo="arma")
             .select_related("item", "material", "sigilo_prefixo", "sigilo_sufixo"))
    magias = p.magias.all().order_by("camada", "nome")
    
    # Categorizar magias por execução para facilitar abas (A, B, R)
    magias_padrao = [m for m in magias if "ação" in m.execucao.lower() and "bônus" not in m.execucao.lower()]
    magias_bonus = [m for m in magias if "bônus" in m.execucao.lower()]
    magias_reacao = [m for m in magias if "reação" in m.execucao.lower()]
    
    # Categorizar habilidades
    habilidades = p.habilidades.all().order_by("nome")
    habs_padrao = [h for h in habilidades if "ação padrão" in h.execucao.lower()]
    habs_bonus = [h for h in habilidades if "ação bônus" in h.execucao.lower()]
    habs_reacao = [h for h in habilidades if "reação" in h.execucao.lower()]
    habs_livre = [h for h in habilidades if "ação livre" in h.execucao.lower()]
    habs_passivas = [h for h in habilidades if h not in habs_padrao and h not in habs_bonus and h not in habs_reacao and h not in habs_livre]
    
    # Perícias ordenadas
    pericias = p.pericias.select_related("pericia").order_by("pericia__nome")
    pericias_sociais = pericias.filter(pericia__nome__in=["Cultura", "Diplomacia", "Intimidação", "Intuição", "Manipulação"])
    
    # Condições globais
    condicoes_lista = models.Condicao.objects.all()
    
    # Consumíveis de cura/recuperação
    consumiveis = (p.inventario.filter(item__tipo__in=["consumivel", "equipamento", "outro"])
                   .select_related("item").filter(
                       Q(item__nome__icontains="Poção") | 
                       Q(item__nome__icontains="Antídoto") | 
                       Q(item__nome__icontains="Kit de curandeiro") |
                       Q(item__nome__icontains="Ambrosia")
                   ))
                   
    # Ações especiais de itens
    kit_curandeiro = p.inventario.filter(item__nome__icontains="Kit de Curandeiro").first()
    pocao_cura = p.inventario.filter(item__nome__icontains="Poção de Cura").first()
    
    # Verifica se há cena ativa
    cena_atual = p.mesa.cena_atual if p.mesa and hasattr(p.mesa, 'cena_atual') and p.mesa.cena_atual.ativa else None

    return render(request, "core/cena.html", {
        "p": p, "tela": "cena",
        "armas": armas,
        "magias_padrao": magias_padrao,
        "magias_bonus": magias_bonus,
        "magias_reacao": magias_reacao,
        "pericias": pericias,
        "pericias_sociais": pericias_sociais,
        "condicoes_lista": condicoes_lista,
        "condicoes_ativas_lista": [c.strip() for c in p.condicoes_ativas.split(",") if c.strip()],
        "consumiveis": consumiveis,
        "kit_curandeiro": kit_curandeiro,
        "pocao_cura": pocao_cura,
        "habs_padrao": habs_padrao,
        "habs_bonus": habs_bonus,
        "habs_reacao": habs_reacao,
        "habs_livre": habs_livre,
        "habs_passivas": habs_passivas,
        "atributo_choices": models.Pericia.ATRIBUTOS,
        "cena_atual": cena_atual,
    })


@login_required
def cena_sync(request, pk):
    """Endpoint AJAX para manter a tela de Cena sincronizada em tempo real"""
    p = get_object_or_404(models.Personagem, pk=pk)
    
    if not p.mesa or not hasattr(p.mesa, 'cena_atual') or not p.mesa.cena_atual.ativa:
        return JsonResponse({"ativa": False})
        
    cena = p.mesa.cena_atual
    participantes = []
    
    # Adicionar campo meu_turno para o JS saber se pisca a tela
    meu_turno = False
    
    for i, part in enumerate(cena.participantes.all()):
        is_ativo = (i == cena.turno_atual)
        if is_ativo and part.personagem == p:
            meu_turno = True
            
        participantes.append({
            "nome": part.nome,
            "iniciativa": part.iniciativa,
            "ativo": is_ativo,
            "is_npc": part.personagem is None,
            "pv_atual": part.personagem.pv_atual if part.personagem else None,
            "pv_maximo": part.personagem.pv_maximo if part.personagem else None
        })
        
    return JsonResponse({
        "ativa": True,
        "tipo": cena.tipo,
        "tipo_display": cena.get_tipo_display(),
        "turno_atual": cena.turno_atual,
        "anotacoes": cena.anotacoes,
        "participantes": participantes,
        "meu_turno": meu_turno
    })


@login_required
@require_POST
def consumir_item(request, pk, entrada_id):
    p = _meu(request, pk)
    e = get_object_or_404(models.InventarioEntrada, pk=entrada_id, personagem=p)
    models.RegistroLog.objects.create(personagem=p, mensagem=f"Consumiu {e.item.nome}")
    if e.quantidade > 1:
        e.quantidade -= 1
        e.save(update_fields=["quantidade"])
    else:
        e.delete()
    return JsonResponse({"ok": True, "nova_qtd": e.quantidade if e.pk else 0})


@login_required
@require_POST
def descanso_longo(request, pk):
    p = _meu(request, pk)
    p.pv_atual = p.pv_maximo
    p.enfase_atual = p.enfase_total
    p.dados_vida_usados = max(0, p.dados_vida_usados - p.dados_vida_total // 2)
    p.morte_falhas = 0
    p.save()
    models.RegistroLog.objects.create(personagem=p, mensagem="Realizou um Descanso Longo (recuperou tudo)")
    messages.success(request, "Descanso Longo finalizado!")
    return redirect("cena", pk=p.pk)


@login_required
def catalogo(request, pk):
    p = _meu(request, pk)

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        obj_id = request.POST.get("id")
        acao = request.POST.get("acao", "toggle")

        if tipo == "item":
            item = get_object_or_404(_visiveis(models.Item, request.user), pk=obj_id)
            if acao == "add":
                entrada, criada = p.inventario.get_or_create(item=item, defaults={"quantidade": 1})
                if not criada:
                    entrada.quantidade += 1
                    entrada.save(update_fields=["quantidade"])
                if item.preco:
                    from django.db.models import F
                    models.Personagem.objects.filter(pk=p.pk).update(trocados=F('trocados') - item.preco)
                    messages.success(request, f"{item.nome} adicionado. T${item.preco} descontados.")
                else:
                    messages.success(request, f"{item.nome} adicionado ao inventário.")
        elif tipo == "magia":
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

    secao = request.GET.get("secao", "todos")
    q = request.GET.get("q", "").strip()
    user = request.user

    def filtra(qs):
        return qs.filter(nome__icontains=q) if q else qs

    contexto = {"tela": "catalogo", "secao": secao, "q": q, "p": p}
    contexto["minhas_magias"] = set(p.magias.values_list("pk", flat=True))
    contexto["minhas_habilidades"] = set(p.habilidades.values_list("pk", flat=True))
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
    if secao == "todos":
        resultados_list = []
        for k, qs in secoes.items():
            lst = list(qs)
            for obj in lst:
                obj.catalogo_secao = k
            resultados_list.extend(lst)
        resultados_list.sort(key=lambda x: x.nome)
        contexto["resultados"] = resultados_list
    else:
        contexto["resultados"] = secoes.get(secao, secoes["armas"])

    contexto["nomes_secoes"] = [
        ("todos", "Todos"),
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


@login_required
def pericia_nova(request):
    return _criar_custom(request, forms.PericiaCustomForm, "Criar Aptidão Customizada", "/catalogo/?secao=pericias")


@login_required
def pericias_gerenciar(request, pk):
    """Seleciona perícias e aptidões do catálogo para a personagem."""
    p = _meu(request, pk)
    if request.method == "POST":
        obj_id = request.POST.get("id")
        per = get_object_or_404(_visiveis(models.Pericia, request.user), pk=obj_id)
        pp = p.pericias.filter(pericia=per).first()
        if pp:
            pp.delete()
        else:
            models.PericiaPersonagem.objects.create(
                personagem=p, pericia=per, atributo=per.atributo_padrao)
        return redirect(f"{request.path}?{request.GET.urlencode()}")

    q = request.GET.get("q", "").strip()
    pericias_catalogo = _visiveis(models.Pericia, request.user)
    if q:
        pericias_catalogo = pericias_catalogo.filter(nome__icontains=q)
    
    return render(request, "core/pericias_gerenciar.html", {
        "p": p, "tela": "ficha",
        "catalogo": pericias_catalogo,
        "minhas_pericias": set(p.pericias.values_list("pericia_id", flat=True)),
        "q": q,
        "form_pericia": forms.PericiaCustomForm(),
    })
