# Weather API Recommendations

This document provides recommendations for adding weather forecasts to NASCAR race data.

## The Challenge

NASCAR's schedule API provides:
- Track name (e.g., "Daytona International Speedway")
- State (e.g., "FL")
- Race date and time

It does NOT provide:
- Latitude/longitude coordinates
- City name
- Zip code

Most weather APIs require coordinates, so we need either:
1. A weather API with built-in geocoding
2. A separate geocoding step to convert track names to coordinates

---

## Recommended: Tomorrow.io

**Why Tomorrow.io?**
- Built-in geocoding (accepts location names directly)
- Free tier: 500 calls/day (was 1,000, verify current limits)
- 16-day forecast available
- Hyperlocal data at ZIP code level
- Used by Uber, JetBlue, Ford

**Website**: https://www.tomorrow.io/weather-api/

### Location Formats Supported

Tomorrow.io accepts multiple location formats:
- Latitude/longitude: `location=42.3478,-71.0466`
- City name: `location=daytona beach, fl`
- Place name: `location=daytona international speedway`

### Example Request

```bash
curl "https://api.tomorrow.io/v4/weather/forecast?location=daytona%20international%20speedway&apikey=YOUR_API_KEY"
```

### Response includes resolved coordinates:
```json
{
  "location": {
    "lat": 29.1856,
    "lon": -81.0693,
    "name": "Daytona International Speedway, Daytona Beach, FL",
    "type": "administrative"
  },
  "timelines": {
    "daily": [...]
  }
}
```

### Free Tier Limits
- ~500 calls/day (verify at signup)
- 16-day forecast
- Hourly data available

---

## Alternative: OpenWeatherMap

**Why OpenWeatherMap?**
- Very popular, well-documented
- Free tier: 1,000 calls/day
- 8-day forecast on free tier
- Established company, reliable

**Website**: https://openweathermap.org/api/one-call-3

### Limitation: Requires Coordinates

OpenWeatherMap's One Call API 3.0 requires lat/long coordinates. You must:
1. Use their Geocoding API first to convert location names
2. Then call the weather API with coordinates

### Two-Step Process

**Step 1: Geocode the location**
```bash
curl "https://api.openweathermap.org/geo/1.0/direct?q=Daytona+International+Speedway,FL,US&limit=1&appid=YOUR_API_KEY"
```

Response:
```json
[{
  "name": "Daytona Beach",
  "lat": 29.2108,
  "lon": -81.0228,
  "country": "US",
  "state": "Florida"
}]
```

**Step 2: Get weather forecast**
```bash
curl "https://api.openweathermap.org/data/3.0/onecall?lat=29.2108&lon=-81.0228&appid=YOUR_API_KEY"
```

### Free Tier Limits
- 1,000 calls/day for One Call API 3.0
- 60 calls/minute max
- 8-day forecast

---

## Comparison Table

| Feature | Tomorrow.io | OpenWeatherMap |
|---------|-------------|----------------|
| Free tier | ~500 calls/day | 1,000 calls/day |
| Built-in geocoding | Yes | No (separate API) |
| Forecast range | 16 days | 8 days |
| Location formats | lat/long, city, place name | lat/long only |
| API calls per forecast | 1 | 2 (geocode + weather) |
| Minute-by-minute | Yes (6 hours) | Yes (1 hour) |
| Historical data | Paid | 47+ years included |

---

## Recommended Implementation

### Option A: Tomorrow.io (Simpler)

```python
import httpx

async def get_race_weather(track_name: str, state: str, race_date: str, api_key: str):
    """Get weather forecast for a race using Tomorrow.io."""
    location = f"{track_name}, {state}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.tomorrow.io/v4/weather/forecast",
            params={
                "location": location,
                "apikey": api_key,
                "timesteps": "1d",
                "units": "imperial"
            }
        )
        return response.json()
```

### Option B: OpenWeatherMap (More calls available)

```python
import httpx

async def geocode_track(track_name: str, state: str, api_key: str):
    """Convert track name to coordinates."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openweathermap.org/geo/1.0/direct",
            params={
                "q": f"{track_name},{state},US",
                "limit": 1,
                "appid": api_key
            }
        )
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
        return None, None

async def get_weather_forecast(lat: float, lon: float, api_key: str):
    """Get weather forecast for coordinates."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openweathermap.org/data/3.0/onecall",
            params={
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "imperial",
                "exclude": "minutely,alerts"
            }
        )
        return response.json()
```

---

## Option C: Static Track Coordinates Lookup

For maximum reliability, maintain a lookup table of track coordinates:

```python
TRACK_COORDINATES = {
    "Daytona International Speedway": (29.1856, -81.0693),
    "Talladega Superspeedway": (33.5669, -86.0642),
    "Charlotte Motor Speedway": (35.3522, -80.6828),
    "Atlanta Motor Speedway": (33.3847, -84.3169),
    "Bristol Motor Speedway": (36.5158, -82.2569),
    "Martinsville Speedway": (36.6342, -79.8514),
    "Phoenix Raceway": (33.3753, -112.3119),
    "Las Vegas Motor Speedway": (36.2719, -115.0103),
    "Texas Motor Speedway": (33.0372, -97.2817),
    "Kansas Speedway": (39.1158, -94.8311),
    "Michigan International Speedway": (42.0650, -84.2403),
    "Pocono Raceway": (41.0558, -75.5122),
    "Homestead-Miami Speedway": (25.4517, -80.4089),
    "Darlington Raceway": (34.2947, -79.9056),
    "Richmond Raceway": (37.5933, -77.4197),
    "Dover Motor Speedway": (39.1900, -75.5303),
    "Nashville Superspeedway": (36.0328, -86.3903),
    "Gateway Motorsports Park": (38.6292, -90.1378),
    "New Hampshire Motor Speedway": (43.3628, -71.4606),
    "Sonoma Raceway": (38.1611, -122.4550),
    "Watkins Glen International": (42.3369, -76.9272),
    "Circuit of The Americas": (30.1328, -97.6411),
    "Indianapolis Motor Speedway": (39.7950, -86.2353),
    "Iowa Speedway": (41.6778, -92.7050),
    # Add more as needed...
}
```

This approach:
- Eliminates geocoding API calls
- Provides exact track coordinates (not city center)
- Works offline
- No API key required for location lookup

---

## Forecast Limitations

Weather forecasts become less accurate beyond ~7 days. For races more than 7-10 days away, treat forecasts as rough estimates.

| Days Out | Accuracy |
|----------|----------|
| 1-3 days | High |
| 4-7 days | Moderate |
| 8-14 days | Low |
| 15+ days | Very Low |

---

## Sources

- [Tomorrow.io Weather API](https://www.tomorrow.io/weather-api/)
- [Tomorrow.io API Formats](https://docs.tomorrow.io/reference/api-formats)
- [OpenWeatherMap One Call 3.0](https://openweathermap.org/api/one-call-3)
- [Dark Sky Alternatives Comparison](https://www.tomorrow.io/blog/dark-sky-weather-api-alternatives/)
- [Best Weather APIs 2025](https://www.visualcrossing.com/resources/blog/best-weather-api-for-2025/)
