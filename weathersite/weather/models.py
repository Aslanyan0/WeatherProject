from django.db import models
from django.conf import settings


class SavedCity(models.Model):
    city_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=10)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_cities"
    )

    def __str__(self):
        return f"{self.city_name}, {self.country_code}"
