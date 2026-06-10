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
    resposta = responder(pergunta)
    Consulta.objects.create(user=request.user, pergunta=pergunta, resposta=resposta)
    return JsonResponse({"pergunta": pergunta, "resposta": resposta})
