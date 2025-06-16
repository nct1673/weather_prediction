import requests
import json
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from my_api_key import API_KEY

# Replace with your actual API key
API_KEY = ""

# Example coordinates: Klang
lat = 3.033
lon = 101.45
dt = 1749834000 #14/6/25

# One Call 3.0 endpoint
url = "https://api.openweathermap.org/data/3.0/onecall"
url2 = "https://api.openweathermap.org/data/3.0/onecall/timemachine" # timestamp data


var_names = [
    "lat","lon","timezone","timezone_offset","dt",
    "sunrise","sunset","temp","feels_like","pressure",
    "humidity","dew_point","uvi","clouds","visibility",
    "wind_speed","wind_deg","id","main","description","icon"
]


#######################################################################################33

# empty df to store temp data
df = pd.DataFrame()


start = time.time()

for i in range(48):
    dt = 1749834000 # Sunday, June 14, 2025 12:00:00 AM GMT+08:00
    dt += i*3600 # 3600secs = 1 hour
    params = {
    "lat": lat,
    "lon": lon, 
    "appid": API_KEY,
    # "units": "metric",  # or 'imperial'
    'dt': dt,
    # "exclude": "minutely,daily"  # you can exclude parts you don't need
    }

    response = requests.get(url2, params=params)
    if response.status_code == 200:
        data = response.json()

        utc = datetime.fromtimestamp(dt, tz=ZoneInfo("Asia/Kuala_Lumpur"))
        filename_json = f'data_json/weather_data_{utc}.json'
        # Save to JSON file
        with open(filename_json, "w") as f:
            json.dump(data, f, indent=4)
    
        # print("Weather data saved to weather_data.json")
        # print(type(data))
    else:
        print("Error:", response.status_code, response.text)

    lat = data['lat']
    lon = data['lon']
    timezone = data['timezone']
    timezone_offset = data['timezone_offset']

    # current
    curr = data['data'][0]
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
    weather = data['data'][0]['weather'][0]
    id = weather['id']
    main = weather['main']
    description = weather['description']
    icon = weather['icon']
    
    data_df = {var: globals()[var] for var in var_names}
    df_temp = pd.DataFrame([data_df])
    df = pd.concat([df, df_temp], ignore_index=True)

df.to_csv('data_csv/data_raw_250614.csv')
time_use = time.time() - start
print(f"Done, finished in {time_use} seconds")






