import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from statsmodels.tsa.seasonal import seasonal_decompose
import time

start = time.time()

df = pd.read_csv('data_csv_raw/raw_data.csv')
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
df = df.iloc[12:].reset_index(drop=True)
df.drop(df[df['weather_main'] == 'Smoke'].index, inplace=True)
df.drop(df[df['weather_main'] == 'Haze'].index, inplace=True)
df.drop(df[df['weather_main'] == 'Clear'].index, inplace=True)
df.drop(df[df['weather_main'] == 'Mist'].index, inplace=True)
df.dropna(subset=['visibility'], inplace=True)

df.to_csv('data_csv_out/data.csv')
print("✅ Raw data has been processed and saved to 'data_csv_out/data.csv'")
time_use = time.time() - start
print(f"Finished in {time_use} seconds.")