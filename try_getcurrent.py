import requests
import json
import pandas as pd
from my_api_key import API_KEY
from datetime import datetime
from zoneinfo import ZoneInfo

# Replace with your actual API key
# API_KEY = ""

# Example coordinates: Klang
lat = 3.033
lon = 101.45
# dt = 1750046400

# One Call 3.0 endpoint
url = "https://api.openweathermap.org/data/3.0/onecall"
# url2 = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

params = {
    "lat": lat,
    "lon": lon, 
    "appid": API_KEY,
    # "units": "metric",  # or 'imperial'
    # 'dt': dt,
    "exclude": "minutely,daily"  # you can exclude parts you don't need
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()

    # extract date & time
    dt = data['current']['dt']
    utc8 = datetime.fromtimestamp(dt, tz=ZoneInfo("Asia/Kuala_Lumpur"))

    # Save to JSON file
    # /home/chen/Desktop/weather/try_getdata
    filename = f'/home/chen/Desktop/weather/try_getdata/weather_data_{utc8}.json'
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    # print("Weather data saved to weather_data.json")
    # print(type(data))
else:
    print("Error:", response.status_code, response.text)


