import requests
import json
import pandas as pd
from my_api_key import API_KEY

# Replace with your actual API key
API_KEY = ""

# Example coordinates: Klang
lat = 3.033
lon = 101.45
dt = 1750046400

# One Call 3.0 endpoint
url = "https://api.openweathermap.org/data/3.0/onecall"
url2 = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

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

    # Save to JSON file
    with open("current_data.json", "w") as f:
        json.dump(data, f, indent=4)
    
    print("Weather data saved to weather_data.json")
    # print(type(data))
else:
    print("Error:", response.status_code, response.text)


lat = data['lat']
lon = data['lon']
timezone = data['timezone']
timezone_offset = data['timezone_offset']

# current
curr = data['current']
dt = curr['dt']
sunrise = curr['sunrise']
sunset = curr['sunset']
temp = curr['temp']
feels_like = curr['feels_like']
pressure = curr['pressure']
humidity = curr['humidity']
dew_point = curr['dew_point']
uvi = curr['uvi']
clouds = curr['clouds']
visibility = curr['visibility']
wind_speed = curr['wind_speed']
wind_deg = curr['wind_deg']

#  current >> weather >> :
weather = data['current']['weather'][0]
id = weather['id']
main = weather['main']
description = weather['description']
icon = weather['icon']

# print()

# Create list of variable names to record
var_names = ['lat', 'dt', 'icon']

# Use locals() or globals() to fetch their values dynamically
data_df = {var: globals()[var] for var in var_names}
df = pd.DataFrame([data_df])
print(df)

# h = data['hourly']
# print(len(h))

