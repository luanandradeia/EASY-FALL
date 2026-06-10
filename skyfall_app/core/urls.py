from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("registrar/", views.registrar, name="registrar"),

    path("", views.personagens, name="personagens"),
    path("personagem/novo/", views.personagem_novo, name="personagem_novo"),
    path("personagem/<int:pk>/", views.ficha, name="ficha"),
    path("personagem/<int:pk>/editar/", views.personagem_editar, name="personagem_editar"),
    path("personagem/<int:pk>/excluir/", views.personagem_excluir, name="personagem_excluir"),
    path("personagem/<int:pk>/ajuste/", views.ajuste_rapido, name="ajuste_rapido"),
    path("personagem/<int:pk>/pericia/", views.pericia_toggle, name="pericia_toggle"),

    path("personagem/<int:pk>/inventario/", views.inventario, name="inventario"),
    path("personagem/<int:pk>/inventario/add/", views.inventario_add, name="inventario_add"),
    path("personagem/<int:pk>/inventario/<int:entrada>/", views.inventario_update, name="inventario_update"),

    path("personagem/<int:pk>/cena/", views.cena, name="cena"),
    path("personagem/<int:pk>/grimorio/", views.grimorio, name="grimorio"),

    path("catalogo/", views.catalogo, name="catalogo"),
    path("catalogo/item/novo/", views.item_novo, name="item_novo"),
    path("catalogo/magia/nova/", views.magia_nova, name="magia_nova"),
    path("catalogo/habilidade/nova/", views.habilidade_nova, name="habilidade_nova"),
]
