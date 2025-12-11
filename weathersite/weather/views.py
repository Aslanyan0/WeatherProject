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

    # city = SavedCity{
    #     "name": weather_res.get(city),
    #     "country": weather_res.get("country", ""),
    # }
    print(weather_res)
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

    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={API_KEY}&units=metric"
    )

    data = requests.get(forecast_url).json()

    # список прогнозов по 3 часа
    forecasts = data["list"]

    # завтра
    tomorrow_day = (datetime.now() + timedelta(days=1)).date()

    # фильтруем все записи на завтра
    tomorrow_entries = [
        item
        for item in forecasts
        if datetime.fromtimestamp(item["dt"]).date() == tomorrow_day
    ]

    # --- если данных нет ---
    if not tomorrow_entries:
        return HttpResponse("No forecast data for tomorrow.")

    # --- ночные температуры (00:00–06:00) ---
    night_temps = [
        item["main"]["temp"]
        for item in tomorrow_entries
        if 0 <= datetime.fromtimestamp(item["dt"]).hour <= 6
    ]

    # --- дневные температуры (12:00–18:00) ---
    day_temps = [
        item["main"]["temp"]
        for item in tomorrow_entries
        if 12 <= datetime.fromtimestamp(item["dt"]).hour <= 18
    ]

    temp_min_night = min(night_temps)
    temp_max_day = max(day_temps)

    # --- выбираем прогноз на 12:00 как "главный" ---
    main_entry = next(
        (
            item
            for item in tomorrow_entries
            if datetime.fromtimestamp(item["dt"]).hour == 12
        ),
        tomorrow_entries[0],
    )

    humidity = main_entry["main"]["humidity"]
    visibility = main_entry.get("visibility", 0)
    pressure = main_entry["main"]["pressure"]
    wind = main_entry["wind"]["speed"]

    weather_code = main_entry["weather"][0]["icon"]
    icon = f"/static/weather_icons/{weather_code}.png"

    context = {
        "city": city,
        "date": tomorrow_day.strftime("%a, %b %d"),
        "temp_min_night": temp_min_night,
        "temp_max_day": temp_max_day,
        "humidity": humidity,
        "visibility": visibility,
        "pressure": pressure,
        "wind": wind,
        "icon": icon,
        "hourly": tomorrow_entries,
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
