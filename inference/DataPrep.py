import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from statsmodels.tsa.seasonal import seasonal_decompose
import time

def safe_get(d, key, default="NA"):
    return d.get(key, default)

def get_df(data):
    all_records = []
    lat = safe_get(data, "lat", "NA")
    lon = safe_get(data, "lon", "NA")
    tz = safe_get(data, "timezone", "NA")
    tz_offset = safe_get(data, "timezone_offset", "NA")

    for item in safe_get(data, "data", []):
        base = {
            "lat": lat,
            "lon": lon,
            "timezone": tz,
            "timezone_offset": tz_offset,
            "dt": safe_get(item, "dt", "NA"),
            "sunrise": safe_get(item, "sunrise", "NA"),
            "sunset": safe_get(item, "sunset", "NA"),
            "temp": safe_get(item, "temp", "NA"),
            "feels_like": safe_get(item, "feels_like", "NA"),
            "pressure": safe_get(item, "pressure", "NA"),
            "humidity": safe_get(item, "humidity", "NA"),
            "dew_point": safe_get(item, "dew_point", "NA"),
            "uvi": safe_get(item, "uvi", "NA"),
            "clouds": safe_get(item, "clouds", "NA"),
            "visibility": safe_get(item, "visibility", "NA"),
            "wind_speed": safe_get(item, "wind_speed", "NA"),
            "wind_deg": safe_get(item, "wind_deg", "NA"),
        }

        # Flatten weather array
        weather_list = safe_get(item, "weather", [])
        if weather_list:
            for w in weather_list:
                record = base.copy()
                record.update({
                    "weather_id": safe_get(w, "id", "NA"),
                    "weather_main": safe_get(w, "main", "NA"),
                    "weather_desc": safe_get(w, "description", "NA"),
                    "weather_icon": safe_get(w, "icon", "NA")
                })
                all_records.append(record)
        else:
            record = base.copy()
            record.update({
                "weather_id": "NA",
                "weather_main": "NA",
                "weather_desc": "NA",
                "weather_icon": "NA"
            })
            all_records.append(record)

    # Convert to DataFrame
    df = pd.DataFrame(all_records)
    return df






# Function that returns a DataFrame
def data_preprep(lat, lon, tz, tz_offset, sunrise, sunset, entry, entry_type="hourly"):
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



def inference_prep(df):
    df.drop_duplicates(inplace=True)
    df = df.sort_values(by='dt')

    df['utc8'] = pd.to_datetime(df['dt'], unit='s', utc=True).dt.tz_convert('Asia/Kuala_Lumpur')
    # df['year']       = df['utc8'].dt.year
    df['month']      = df['utc8'].dt.month
    # df['day']        = df['utc8'].dt.day
    df['hour']       = df['utc8'].dt.hour
    df['hour_stan'] = (df['hour'] - df['hour'].min()) / (df['hour'].max() - df['hour'].min())
    # df['minute']     = df['utc8'].dt.minute
    # df['second']     = df['utc8'].dt.second
    # df['date']       = df['utc8'].dt.date
    # df['time']       = df['utc8'].dt.time
    # df['weekday']    = df['utc8'].dt.day_name()     # e.g., 'Monday'
    df['week'] = df['utc8'].dt.isocalendar().week
    df['week'] = df['week']/52
    df['day_of_year'] = df['utc8'].dt.dayofyear
    df['day_of_year'] = df['day_of_year']/365
    df['quarter']    = df['utc8'].dt.quarter
    df['quarter'] = df['quarter'] /4

    conditions = [
        df['dt'] <= df['sunrise'],
        (df['dt'] > df['sunrise']) & (df['dt'] <= df['sunset'])
    ]
    choices = [0, 1]
    df['wind_deg'] = df['wind_deg']/360
    df['sunrise_sunset'] = np.select(conditions, choices, default=2)
    df['sunrise_sunset'] = df['sunrise_sunset']/3
    df['sun_on'] = np.select(conditions, choices, default=0)
    df['pressure_norm'] = (df['pressure'] - df['pressure'].mean()) / df['pressure'].std()
    df['visibility'] = (df['visibility'] - df['visibility'].min()) / (df['visibility'].max() - df['visibility'].min())
    df['temp_stan'] = (df['temp'] - df['temp'].min()) / (df['temp'].max() - df['temp'].min())
    df['feelslike_stan'] = (df['feels_like'] - df['feels_like'].min()) / (df['feels_like'].max() - df['feels_like'].min())
    df['humidity_stan'] = (df['humidity'] - df['humidity'].min()) / (df['humidity'].max() - df['humidity'].min())
    df['dewpoint_stan'] = (df['dew_point'] - df['dew_point'].min()) / (df['dew_point'].max() - df['dew_point'].min())

    # lag (in hour)
    for i in range(6):
        i+=1
        var1 = f'templag_{i}'
        var2 = f'pressurelag_{i}'
        var3 = f'humiditylag_{i}'
        var4 = f'dewpointlag_{i}'
        var5 = f'feelslikelag_{i}'
        df[var1] = df['temp_stan'].shift(i)
        df[var2] = df['pressure_norm'].shift(i)
        df[var3] = df['humidity_stan'].shift(i)
        df[var4] = df['dewpoint_stan'].shift(i)
        df[var5] = df['feelslike_stan'].shift(i)

    # moving average
    for i in range(1, 11, 2):
        i+=1
        var1 = f'tempMA_{i-1}'
        var2 = f'pressureMA_{i-1}'
        var3 = f'humidityMA_{i-1}'
        var4 = f'dewpointMA_{i-1}'
        var5 = f'feelslikeMA_{i-1}'
        df[var1] = df['temp_stan'].rolling(window=i).mean()
        df[var2] = df['pressure_norm'].rolling(window=i).mean()
        df[var3] = df['humidity_stan'].rolling(window=i).mean()
        df[var4] = df['dewpoint_stan'].rolling(window=i).mean()
        df[var5] = df['feelslike_stan'].rolling(window=i).mean()

    decomp_temp = seasonal_decompose(df['temp_stan'], model='additive', period=24)
    decomp_pressure = seasonal_decompose(df['pressure_norm'], model='additive', period=24)
    decomp_humidity = seasonal_decompose(df['humidity_stan'], model='additive', period=24)
    decomp_dewpoint = seasonal_decompose(df['dewpoint_stan'], model='additive', period=24)
    decomp_feelslike = seasonal_decompose(df['feelslike_stan'], model='additive', period=24)

    df['temp_trend'] = decomp_temp.trend.ffill().bfill()
    df['temp_seasonal'] = decomp_temp.seasonal
    df['temp_residual'] = decomp_temp.resid.ffill().bfill()
    df['pressure_trend'] = decomp_pressure.trend.ffill().bfill()
    df['pressure_seasonal'] = decomp_pressure.seasonal
    df['pressure_residual'] = decomp_pressure.resid.ffill().bfill()
    df['humidity_trend'] = decomp_humidity.trend.ffill().bfill()
    df['humidity_seasonal'] = decomp_humidity.seasonal
    df['humidity_residual'] = decomp_humidity.resid.ffill().bfill()
    df['dewpoint_trend'] = decomp_dewpoint.trend.ffill().bfill()
    df['dewpoint_seasonal'] = decomp_dewpoint.seasonal
    df['dewpoint_residual'] = decomp_dewpoint.resid.ffill().bfill()
    df['feelslike_trend'] = decomp_feelslike.trend.ffill().bfill()
    df['feelslike_seasonal'] = decomp_feelslike.seasonal
    df['feelslike_residual'] = decomp_feelslike.resid.ffill().bfill()

    df['temp_w_seas'] = df['temp_stan'] * (1 + df['temp_seasonal'])
    df['pressure_w_seas'] = df['pressure_norm'] * (1 + df['pressure_seasonal'])
    df['humidity_w_seas'] = df['humidity_stan'] * (1 + df['humidity_seasonal'])
    df['dewpoint_w_seas'] = df['dewpoint_stan'] * (1 + df['dewpoint_seasonal'])
    df['feelslike_w_seas'] = df['feelslike_stan'] * (1 + df['feelslike_seasonal'])

    drop_cols = [
        'lat',
        'lon',
        'timezone',
        'timezone_offset',
        'dt',
        'sunrise',
        'sunset',
        'temp', 
        'feels_like',
        'pressure',
        'humidity',
        'dew_point',
        'uvi',
        'utc8',
        'hour',
        'weather_id',
        'weather_icon'
    ]

    df.drop(drop_cols, axis=1, inplace=True)
    # df = df.iloc[12:].reset_index(drop=True)
    # df.drop(df[df['weather_main'] == 'Smoke'].index, inplace=True)
    # df.drop(df[df['weather_main'] == 'Haze'].index, inplace=True)
    # df.drop(df[df['weather_main'] == 'Clear'].index, inplace=True)
    # df.drop(df[df['weather_main'] == 'Mist'].index, inplace=True)
    # df.dropna(subset=['visibility'], inplace=True)

    return df