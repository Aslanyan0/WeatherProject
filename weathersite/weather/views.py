from django.views.generic import TemplateView
from .utils import home, tomorrow, weekly, autocomplete


class MyView(TemplateView):
    template_name = "my_template.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = home()
        context["tomorrow"] = tomorrow()
        context["weekly"] = weekly()
        context["autocomplete"] = autocomplete()
        return context


# ip_address = request.META.get("HTTP_X_FORWARDED_FOR")
# if ip_address:
#     ip_address = ip_address.split(",")[0]
# else:
#     ip_address = request.META.get("REMOTE_ADDR")
# ip_address = "8.8.8.8"  # For testing purposes
# url = f"https://ipapi.co/{ip_address}/json/"
# response = requests.get(url, timeout=5)
# data = response.json()
# context = {
#     "city": data.get("city"),
#     "country": data.get("country_name"),
#     "region": data.get("region"),
# }
# print(data)
