from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .busca import responder
from .models import Consulta


@login_required
def oraculo(request):
    historico = request.user.consultas_oraculo.all()[:50]
    return render(request, "ai_bot/oraculo.html",
                  {"historico": historico, "tela": "oraculo"})


@login_required
@require_POST
def perguntar(request):
    pergunta = (request.POST.get("pergunta") or "").strip()
    if not pergunta:
        return JsonResponse({"erro": "pergunta vazia"}, status=400)
        
    info_personagens = ""
    personagens = request.user.personagens.filter(oculto=False)
    if personagens.exists():
        info_personagens = "[DADOS DOS PERSONAGENS DO JOGADOR]\n(Use esses dados se a pergunta for sobre os status ou habilidades específicas do personagem do jogador)\n"
        for p in personagens:
            classe_nome = p.classe.nome if p.classe else "Sem classe"
            info_personagens += f"- Nome: {p.nome} (Nível {p.nivel}, {classe_nome})\n"
            info_personagens += f"  Status: PV {p.pv_atual}/{p.pv_maximo}, PE {p.enfase_atual}/{p.enfase_total}, Catarse {p.catarse}, Sombra {p.sombra}\n"
            info_personagens += f"  Atributos: FOR {p.atributo('FOR')}, DES {p.atributo('DES')}, CON {p.atributo('CON')}, INT {p.atributo('INT')}, SAB {p.atributo('SAB')}, CAR {p.atributo('CAR')}\n"
            
            itens = [f"{e.quantidade}x {e.item.nome}" for e in p.inventario.select_related('item').all()]
            magias = [m.nome for m in p.magias.all()]
            habilidades = [h.nome for h in p.habilidades.all()]
            
            if itens:
                info_personagens += f"  Inventário: {', '.join(itens)}\n"
            if magias:
                info_personagens += f"  Magias: {', '.join(magias)}\n"
            if habilidades:
                info_personagens += f"  Habilidades: {', '.join(habilidades)}\n"
    
    resposta = responder(pergunta, info_personagens)
    Consulta.objects.create(user=request.user, pergunta=pergunta, resposta=resposta)
    return JsonResponse({"pergunta": pergunta, "resposta": resposta})
