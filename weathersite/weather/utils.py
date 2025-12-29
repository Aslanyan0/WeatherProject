from django.shortcuts import render
import requests
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

    if "main" not in weather_res:
        return render(
            request, "weather/home.html", {"error": "City not found", "city": city}
        )

    return render(request, "weather/home.html", context)


def tomorrow(request):
    city = request.GET.get("city", "Yerevan")

    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={API_KEY}&units=metric"
    )

    data = requests.get(forecast_url).json()

    # Check for city not found
    if data.get("cod") != "200" or "list" not in data:
        return render(
            request,
            "weather/tomorrow.html",
            {"error": "City not found", "city": city},
        )

    # 3-hour forecasts
    forecasts = data["list"]

    # tomorrow date
    tomorrow_day = (datetime.now() + timedelta(days=1)).date()

    # tomorrow entries
    tomorrow_entries = [
        item
        for item in forecasts
        if datetime.fromtimestamp(item["dt"]).date() == tomorrow_day
    ]

    if not tomorrow_entries:
        return render(
            request,
            "weather/tomorrow.html",
            {"error": "No forecast data for tomorrow", "city": city},
        )

    # ---  (00:00–06:00) ---
    night_temps = [
        item["main"]["temp"]
        for item in tomorrow_entries
        if 0 <= datetime.fromtimestamp(item["dt"]).hour <= 6
    ]

    # ---  (12:00–18:00) ---
    day_temps = [
        item["main"]["temp"]
        for item in tomorrow_entries
        if 12 <= datetime.fromtimestamp(item["dt"]).hour <= 18
    ]

    temp_min_night = min(night_temps) if night_temps else None
    temp_max_day = max(day_temps) if day_temps else None

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


def weekly(request):
    city = request.GET.get("city", "Yerevan")

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={API_KEY}&units=metric&lang=en"
    )

    data = requests.get(url).json()

    # Check for city not found
    if data.get("cod") != "200" or "list" not in data:
        return render(
            request,
            "weather/weekly.html",
            {"city": city, "weekly": [], "error": "City not found"},
        )

    today = datetime.now().date()
    forecasts = data["list"]

    days = {}

    for item in forecasts:
        dt = datetime.fromtimestamp(item["dt"])
        date = dt.date()

        # Skip today's date
        if date == today:
            continue

        temp = item["main"]["temp"]
        humidity = item["main"]["humidity"]
        pressure = item["main"]["pressure"]
        wind = item["wind"]["speed"]
        icon = item["weather"][0]["icon"]

        if date not in days:
            days[date] = {
                "temps": [],
                "humidity": [],
                "pressure": [],
                "wind": [],
                "icons": [],
            }

        days[date]["temps"].append(temp)
        days[date]["humidity"].append(humidity)
        days[date]["pressure"].append(pressure)
        days[date]["wind"].append(wind)
        days[date]["icons"].append(icon)

    # for next 5 days
    weekly = []
    for date, v in list(days.items())[:5]:
        weekly.append(
            {
                "date": date.strftime("%a, %b %d"),
                "temp_min": round(min(v["temps"])),
                "temp_max": round(max(v["temps"])),
                "humidity": sum(v["humidity"]) // len(v["humidity"]),
                "pressure": sum(v["pressure"]) // len(v["pressure"]),
                "wind": round(sum(v["wind"]) / len(v["wind"]), 1),
                "icon": f"/static/weather_icons/{max(set(v['icons']), key=v['icons'].count)}.png",
                "weather": " / ".join(sorted(set(v["icons"]))),
            }
        )

    if request.GET.get("format") == "json":
        return JsonResponse({"weekly": weekly})

    return render(request, "weather/weekly.html", {"city": city, "weekly": weekly})


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
