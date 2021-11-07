import requests
import os

def get_weather_data():
    OWM_API_KEY = os.environ.get("OWM_API_KEY")
    OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/onecall"

    cracow_latitude = 50.06162
    cracow_longitude = 19.93741

    parameters = {
        "lat": cracow_latitude,
        "lon": cracow_longitude,
        "appid": OWM_API_KEY,
        "exclude": "minutely,daily,alerts",
        "units": "metric"
    }
    response = requests.get(OWM_ENDPOINT, params=parameters)
    response.raise_for_status()
    return response.json()