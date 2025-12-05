from django.shortcuts import render
import requests
from .models import SavedCity
import json
from django.http import JsonResponse
from datetime import datetime, timedelta


def home(request):

    city = request.GET.get("city", "Yerevan")

    api_key = "0f57bed10657b67a10861b1642817e6d"

    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={api_key}&units=metric"
    )
    weather_res = requests.get(weather_url).json()

    if "main" not in weather_res:
        return render(
            request, "weather/home.html", {"error": "City not found", "city": city}
        )

    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={api_key}&units=metric"
    )
    forecast_res = requests.get(forecast_url).json()
    hourly_full = forecast_res.get("list", [])
    hourly = hourly_full[:8]
    context = {
        "city": city,
        "temperature": round(weather_res["main"]["temp"]),
        "description": weather_res["weather"][0]["description"],
        "icon": weather_res["weather"][0]["icon"],
        "humidity": weather_res["main"]["humidity"],
        "visibility": weather_res.get("visibility", "—"),
        "air_pressure": weather_res["main"]["pressure"],
        "speed": weather_res["wind"]["speed"],
        "forecast": forecast_res.get("list", []),
        "hourly": hourly,
    }

    return render(request, "weather/home.html", context)


def tomorrow(request):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Gyumri&appid=0f57bed10657b67a10861b1642817e6d&units=metric&lang=en"
    forecast_data = requests.get(url).json()
    forecast_list = forecast_data.get("list", [])

    tomorrow_date = (datetime.utcnow() + timedelta(days=1)).date()

    tomorrow_item = next(
        (
            item
            for item in forecast_list
            if datetime.utcfromtimestamp(item["dt"]).date() == tomorrow_date
            and datetime.utcfromtimestamp(item["dt"]).hour == 12
        ),
        None,
    )

    if tomorrow_item is None:
        tomorrow_item = next(
            (
                item
                for item in forecast_list
                if datetime.utcfromtimestamp(item["dt"]).date() == tomorrow_date
            ),
            None,
        )

    tomorrow_temp = tomorrow_item["main"]["temp"] if tomorrow_item else None

    context = {
        "city": city,
        "temperature": tomorrow_temp,
    }

    return render(request, "tomorrow.html", context)


API_KEY = "0f57bed10657b67a10861b1642817e6d"


def autocomplete(request):
    query = request.GET.get("query", "")

    if len(query) < 2:
        return JsonResponse([], safe=False)

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=10&appid={API_KEY}"
    resp = requests.get(url)
    items = resp.json()

    results = []

    for c in items:
        results.append(
            {
                "city": c.get("name"),
                "region": c.get("state") or "",
                "country_code": c.get("country"),
                "lat": c.get("lat"),
                "lon": c.get("lon"),
            }
        )

    return JsonResponse(results, safe=False)

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
