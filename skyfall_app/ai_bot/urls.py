from django.urls import path

from . import views

urlpatterns = [
    path("", views.oraculo, name="oraculo"),
    path("perguntar/", views.perguntar, name="oraculo_perguntar"),
]
