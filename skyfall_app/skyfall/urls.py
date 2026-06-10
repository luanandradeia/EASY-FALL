from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("oraculo/", include("ai_bot.urls")),
    path("", include("core.urls")),
]
