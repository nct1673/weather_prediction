import requests
import json
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from my_api_key import API_KEY



# Things to change:
# 1. dt (first is below this part, second is in for loop)
# 2. check for loop range
# 3. record dt for next time execution

# GMT+8
# 1735660800 250101:0000
# 250617 last dt: 1738854000 250206:2300
# 250618 last dt: 1742310000 250318:2300
# 250619 last dt: 1745766000 250427:2300
# 250620 last dt: 1749222000 250606:2300

#250621 last dt: 1732204800 241122:0000

# Replace with your actual API key
# API_KEY = ""

# Example coordinates: Klang
lat = 3.033
lon = 101.45
dt = 1735660800 #19/3/25

# One Call 3.0 endpoint
url = "https://api.openweathermap.org/data/3.0/onecall"
url2 = "https://api.openweathermap.org/data/3.0/onecall/timemachine" # timestamp data


#######################################################################################33

# empty df to store temp data
df = pd.DataFrame()


start = time.time()

for i in range(960):
    print(f'Extracting step: {i}')
    dt = 1735660800-3600
    dt -= i*3600 # 3600secs = 1 hour
    params = {
    "lat": lat,
    "lon": lon, 
    "appid": API_KEY,
    "units": "metric",  # or 'imperial'
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

    

print(f'Last dt: {dt}')
time_use = time.time() - start
print(f"Done, finished in {time_use} seconds.")






