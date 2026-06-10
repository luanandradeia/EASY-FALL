from django.contrib import admin

from . import models

admin.site.site_header = "Skyfall RPG — Administração"
admin.site.site_title = "Skyfall RPG"


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["nome", "tipo", "categoria", "preco", "volume", "dano", "criado_por"]
    list_filter = ["tipo", "categoria"]
    search_fields = ["nome"]


@admin.register(models.Magia)
class MagiaAdmin(admin.ModelAdmin):
    list_display = ["nome", "camada", "tipo", "custo_enfase", "execucao", "criado_por"]
    list_filter = ["camada", "tipo"]
    search_fields = ["nome"]


@admin.register(models.Habilidade)
class HabilidadeAdmin(admin.ModelAdmin):
    list_display = ["nome", "fonte_tipo", "fonte_nome", "custo_enfase", "criado_por"]
    list_filter = ["fonte_tipo"]
    search_fields = ["nome"]


@admin.register(models.Sigilo)
class SigiloAdmin(admin.ModelAdmin):
    list_display = ["nome", "tipo", "grau", "equipamento", "cargas"]
    list_filter = ["grau", "equipamento", "tipo"]
    search_fields = ["nome"]


class InventarioInline(admin.TabularInline):
    model = models.InventarioEntrada
    extra = 0


class PericiaInline(admin.TabularInline):
    model = models.PericiaPersonagem
    extra = 0


@admin.register(models.Personagem)
class PersonagemAdmin(admin.ModelAdmin):
    list_display = ["nome", "user", "nivel", "classe", "legado", "pv_atual", "pv_maximo"]
    inlines = [PericiaInline, InventarioInline]


for m in [models.Descritor, models.Pericia, models.Condicao, models.Legado,
          models.Maldicao, models.Classe, models.Trilha, models.Antecedente,
          models.Bencao, models.MaterialEspecial, models.Sinapse,
          models.InventarioEntrada, models.PericiaPersonagem]:
    admin.site.register(m)
