import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from statsmodels.tsa.seasonal import seasonal_decompose
import time
from DataPrep import get_df, data_preprep, inference_prep
import json
from my_api_key import API_KEY
import requests
import joblib
import warnings
warnings.filterwarnings("ignore")


df_raw = pd.read_csv('/home/chen/Desktop/weather/data_csv_raw/raw_data.csv')

# Example coordinates: Klang
lat = 3.033
lon = 101.45


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
        # filename_json = f'out_samplejson.json'
        # # Save to JSON file
        # with open(filename_json, "w") as f:
        #     json.dump(data, f, indent=4)

# Top-level metadata
tz = data.get("timezone", "NA")
tz_offset = data.get("timezone_offset", "NA")
sunrise = df_raw['sunrise'].iloc[-1]
sunset = df_raw['sunset'].iloc[-1]


# Create DataFrame list to record inference data
df_json = []
if "current" in data:
    df_json.append(data_preprep(lat, lon, tz, tz_offset, sunrise, sunset, data['current'], entry_type="hourly"))

for h in data.get("hourly", []):
    df_json.append(data_preprep(lat, lon, tz, tz_offset, sunrise, sunset, h, entry_type="hourly"))

df_json = pd.concat(df_json, ignore_index=True) # concat current and hourly data
df_json.drop('entry_type', axis=1, inplace=True)

# concat with raw data for feature engineering
df_raw100 = df_raw.tail(100)
df_pre = pd.concat([df_raw100, df_json], ignore_index=True)

df_done = inference_prep(df_pre)
df = df_done.iloc[100:].reset_index(drop=True)
df = df.drop(['weather_main', 'weather_desc'], axis=1) 

# print(df_pre.shape)
# print(df_done.shape)
# print(df.iloc[0, :].shape)
# df.to_csv('out_sample2.csv')

X1 = df.iloc[0, :]
model = 'trained_model/Decision Tree.pkl'
loaded_model = joblib.load(model)
pred = loaded_model.predict([X1])

for i in range(7):
     X_i = X1 = df.iloc[i, :]
     pred = loaded_model.predict([X_i])
     if pred[0] == 0:
          pred_inv = 'Clouds'
     elif pred[0] == 1:
          pred_inv = 'Rain'
     else:
          pred_inv = 'Thunderstorm'
    
     print(pred_inv)

# print(type(pred))















