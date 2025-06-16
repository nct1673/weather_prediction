from datetime import datetime
from zoneinfo import ZoneInfo

# Example Unix timestamp
unix_timestamp = 1749962860  # e.g., represents some time in June 2024

# Convert to Kuala Lumpur time (UTC+8)
utc8 = datetime.fromtimestamp(unix_timestamp, tz=ZoneInfo("Asia/Kuala_Lumpur"))

# print(kl_time)  # Output: 2025-06-15 12:47:40+08:00

