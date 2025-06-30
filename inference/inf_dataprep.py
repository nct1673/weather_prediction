import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from statsmodels.tsa.seasonal import seasonal_decompose
import time
from DataPrep import data_preprep, inference_prep
import json
from my_api_key import API_KEY
import requests
import joblib
import warnings
warnings.filterwarnings("ignore")
import xgboost as xgb
from config import server_config

filename_dfraw = f'/home/{server_config}/weather/data_csv_raw/raw_data.csv'
filename_model = f'/home/{server_config}/weather/trained_model/XGBoost.pkl'
filename_predout = f'/home/{server_config}/weather_web/data/pred_out.json'

df_raw = pd.read_csv(filename_dfraw)

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

# df_viz = df_json.head(7)
df_viz = df_json.drop(['weather_main', 'weather_desc', 'weather_id', 'weather_icon'], axis=1) 


# concat with raw data for feature engineering
df_raw100 = df_raw.tail(100)
df_pre = pd.concat([df_raw100, df_json], ignore_index=True)

df_done = inference_prep(df_pre)
df = df_done.iloc[100:].reset_index(drop=True)
df = df.drop(['weather_main', 'weather_desc'], axis=1) 
# df = df.head(7)

# print(df.shape)
# print(df_json.shape)
# print(df_pre.shape)
# print(df_done.shape)
# print(df.iloc[0, :].shape)
# df.to_csv('out_sample2.csv')

# X1 = df.iloc[0, :]
# model_file = '/home/{server_config}/weather/trained_model/XGBoost.pkl'
model = joblib.load(filename_model)


preds = []
for i in range(49):
     X_i = X1 = df.iloc[i, :]
     pred = model.predict([X_i])
     preds.append(pred[0])

ref = ['Clouds', 'Rain', 'Thunderstorm']
weather_pred = [ref[i] for i in preds]
df_viz['weather_pred'] = weather_pred
df_viz = df_viz.iloc[1:].reset_index(drop=True)


def save_weather_data(df):
    # Convert Unix time to readable time string (e.g., "14:00")
    # df['timestamp'] = df['dt'].apply(
    #     lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M')
    # )

    df['timestamp'] = df['dt'].apply(
    lambda x: datetime.fromtimestamp(x, tz=ZoneInfo("Asia/Kuala_Lumpur")).strftime('%Y-%m-%d %H:%M')
    )
    df['temp'] = (df['temp'] - 273.15).round(2)
    df['feels_like'] = df['feels_like'] - 273.15
    df['visibility'] = df['visibility']/1000

    return df.to_dict(orient='records')

df2 = save_weather_data(df_viz)
with open(filename_predout, "w") as f:
    json.dump(df2, f, indent=2)
# df_viz.to_csv('/home/{server_config}/weather_web/data/pred_out.csv', index=False)
# print(weather_pred)
# print(type(pred))















