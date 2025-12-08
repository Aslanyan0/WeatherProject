from django.shortcuts import render
import requests
from .models import SavedCity
import json
from django.http import JsonResponse
from datetime import datetime, timedelta


API_KEY = "0f57bed10657b67a10861b1642817e6d"


def home(request):

    city = request.GET.get("city", "Yerevan")

    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={API_KEY}&units=metric"
    )
    weather_res = requests.get(weather_url).json()

    if "main" not in weather_res:
        return render(
            request, "weather/home.html", {"error": "City not found", "city": city}
        )

    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={API_KEY}&units=metric"
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
    city = request.GET.get("city", "Yerevan")

    # get geo data
    geo_url = (
        f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    )
    geo_data = requests.get(geo_url).json()

    if not geo_data:
        return JsonResponse({"error": "City not found"})

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    # get weather data
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,relative_humidity_2m,visibility,pressure_msl,wind_speed_10m,"
        f"weathercode"
        f"&timezone=auto"
    )

    data = requests.get(weather_url).json()
    hourly = data["hourly"]

    # ---- date ----
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%a, %b %d")

    # ---- min/max ----
    night_temps = hourly["temperature_2m"][0:7]  # 00:00–06:00
    day_temps = hourly["temperature_2m"][12:18]  # 12:00–17:00

    temp_min_night = min(night_temps)
    temp_max_day = max(day_temps)

    humidity = hourly["relative_humidity_2m"][12]
    visibility = hourly["visibility"][12]
    pressure = hourly["pressure_msl"][12]
    wind = hourly["wind_speed_10m"][12]

    # ---- icons ----
    weather_code = hourly["weathercode"][12]
    icon = f"/static/weather_icons/{weather_code}.png"

    context = {
        "city": city,
        "date": tomorrow_date,
        "temp_min_night": temp_min_night,
        "temp_max_day": temp_max_day,
        "icon": icon,
        "humidity": humidity,
        "visibility": visibility,
        "pressure": pressure,
        "wind": wind,
    }
    return render(request, "weather/tomorrow.html", context)


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
