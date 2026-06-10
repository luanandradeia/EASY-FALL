from django.conf import settings
from django.db import models


class Consulta(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="consultas_oraculo")
    pergunta = models.TextField()
    resposta = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]

    def __str__(self):
        return self.pergunta[:60]
