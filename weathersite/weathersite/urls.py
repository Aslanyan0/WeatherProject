from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # allauth provider routes (un-namespaced) used by provider_login_url
    path("accounts/social/", include("allauth.urls")),
    # include accounts with an explicit namespace so templates can reverse namespaced URLs
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("", include("weather.urls")),
]
