from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # include accounts with an explicit namespace so templates can reverse namespaced URLs
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("", include("weather.urls")),
]
