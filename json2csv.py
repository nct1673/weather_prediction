import os
import json
import pandas as pd

# Things to change:
# 1. csv filename in last two lines

folder_path = "data_json"  # 🔁 Change to your actual path
all_records = []

def safe_get(d, key, default="NA"):
    return d.get(key, default)

for file in os.listdir(folder_path):
    if file.endswith(".json"):
        file_path = os.path.join(folder_path, file)
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
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

            except json.JSONDecodeError:
                print(f"⚠️ Skipped invalid JSON file: {file}")

# Convert to DataFrame
df = pd.DataFrame(all_records)

# Optional: Replace "NA" with np.nan if you want to apply numeric operations
# import numpy as np
# df.replace("NA", np.nan, inplace=True)

# Save to CSV
df.to_csv("data_csv/raw_250101.csv", index=False)
print("✅ All JSON files have been processed and saved to 'data_csv/raw_250101.csv'")

