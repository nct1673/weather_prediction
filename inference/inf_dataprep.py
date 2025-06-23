import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from statsmodels.tsa.seasonal import seasonal_decompose
import time
from DataPrep import get_df, dataprep
import json
from my_api_key import API_KEY
import requests

raw_df = pd.read_csv('/home/chen/Desktop/weather/data_csv_raw/raw_data.csv')




# Example coordinates: Klang
lat = 3.033
lon = 101.45
# sunrise = 
# sunset = 
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

        # utc = datetime.fromtimestamp(dt, tz=ZoneInfo("Asia/Kuala_Lumpur"))
        filename_json = f'out_samplejson.json'
        # Save to JSON file
        with open(filename_json, "w") as f:
            json.dump(data, f, indent=4)

# Top-level metadata
tz = data.get("timezone", "NA")
tz_offset = data.get("timezone_offset", "NA")
sunrise = raw_df['sunrise'].iloc[-1]
sunset = raw_df['sunset'].iloc[-1]

# Function that returns a DataFrame
def build_record(lat, lon, tz, tz_offset, sunrise, sunset, entry, entry_type="hourly"):
    weather = entry.get("weather", [{}])[0]
    record = {
        "entry_type": entry_type,
        "lat": lat,
        "lon": lon,
        "timezone": tz,
        "timezone_offset": tz_offset,
        "dt": entry.get("dt", "NA"),
        "sunrise": sunrise,
        "sunset": sunset,
        "temp": entry.get("temp", "NA"),
        "feels_like": entry.get("feels_like", "NA"),
        "pressure": entry.get("pressure", "NA"),
        "humidity": entry.get("humidity", "NA"),
        "dew_point": entry.get("dew_point", "NA"),
        "uvi": entry.get("uvi", "NA"),
        "clouds": entry.get("clouds", "NA"),
        "visibility": entry.get("visibility", "NA"),
        "wind_speed": entry.get("wind_speed", "NA"),
        "wind_deg": entry.get("wind_deg", "NA"),
        # "wind_gust": entry.get("wind_gust", "NA"),
        # "pop": entry.get("pop", "NA"),  # Only in hourly
        # "rain_1h": entry.get("rain", {}).get("1h", "NA"),
        "weather_id": weather.get("id", "NA"),
        "weather_main": weather.get("main", "NA"),
        "weather_desc": weather.get("description", "NA"),
        "weather_icon": weather.get("icon", "NA")
    }
    return pd.DataFrame([record])  # Return as DataFrame

# Create DataFrame list
df_list = []

# Add current record
if "current" in data:
    df_list.append(build_record(lat, lon, tz, tz_offset, sunrise, sunset, data['current'], entry_type="hourly"))

# Add hourly records
for h in data.get("hourly", []):
    df_list.append(build_record(lat, lon, tz, tz_offset, sunrise, sunset, h, entry_type="hourly"))

# Concatenate all into one DataFrame
df = pd.concat(df_list, ignore_index=True)

# Save to CSV
df.to_csv("out_sample3.csv", index=False)
# df = get_df(data)
# df.to_csv('out_sample2.csv')

























