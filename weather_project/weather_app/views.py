import datetime

from django.shortcuts import render

import requests

import logging
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    API_KEY = "4499809b056cf7cccca64b404fccf18a"

    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    
    if request.method == "POST":
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)
        
        complete_url = f"{base_url}appid={API_KEY}&q={city1}"
        
        weather_data1, daily_forecast1 = fetch_weather_and_forcecast(complete_url, API_KEY, city1)
        
        if city2:
            complete_url = f"{base_url}appid={API_KEY}&q={city2}"
            weather_data2, daily_forecast2 = fetch_weather_and_forcecast(complete_url, API_KEY, city2)
        else:
            weather_data2, daily_forecast2 = None, None
            
        context = {
            "weather_data1": weather_data1,
            "daily_forecast1": daily_forecast1,
            "weather_data2": weather_data2,
            "daily_forecast2": daily_forecast2
        }
        return render(request, "weather_app/index.html", context)
        
    else:
        return render(request, "weather_app/index.html")
    

def fetch_weather_and_forcecast(complete_url, api_key, city):
    response = requests.get(complete_url.format(api_key, city)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']
    
    #Retrieves the forecast data for the current city
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    #Stores the current weather data of the city in question
    weather_data = {
        "city": city,
        "temperature": round(response['main']['temp'] - 273.15, 2),
        "description": response['weather'][0]['description'],
        "icon": response['weather'][0]['icon']
    }
    
    daily_forecasts = []
    
    # To make sure we only get one piece of data from each day
    days_seen = []
    
    for daily_data in forecast_response['list']:
        if datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A") not in days_seen and len(days_seen) <= 4:
            days_seen.append(datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"))
            
            daily_forecasts.append({
                "day": datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
                "min_temp" : round(daily_data['main']['temp_min'] -273.15, 2),
                "max_temp" : round(daily_data['main']['temp_max'] -273.15, 2),
                "description": daily_data['weather'][0]['description'],
                "icon": daily_data['weather'][0]['icon']
        })
        else:
            continue
        
    return weather_data, daily_forecasts