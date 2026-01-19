# NASCAR Data API Documentation

This document describes the undocumented NASCAR APIs discovered through network traffic analysis of nascar.com.

## Base URLs

- **Primary CDN**: `https://cf.nascar.com/cacher/`
- **Data CDN**: `https://cf.nascar.com/data/cacher/`

## Authentication

No authentication required. APIs are publicly accessible but require browser-like headers (User-Agent) to avoid 403 errors. Direct HTTP requests may be blocked; using a headless browser to intercept responses is recommended.

---

## Schedule API

### Combined Schedule Feed

Returns complete schedule data for a series/year including race details, track info, TV coverage, and more.

**Endpoint**: `https://cf.nascar.com/cacher/{year}/{series_id}/schedule-combined-feed.json`

**Series IDs**:
| Series | ID |
|--------|-----|
| NASCAR Cup Series | 1 |
| NASCAR Xfinity Series | 2 |
| NASCAR Craftsman Truck Series | 3 |

**Example**: `https://cf.nascar.com/cacher/2026/1/schedule-combined-feed.json`

**Response Structure**:
```json
{
  "status": 200,
  "message": "Successfully invoked feed: schedule",
  "response": [
    {
      "Race_Name": "DAYTONA 500",
      "Race_Id": 5592,
      "Race_State": "FL",
      "Series_Id": "1",
      "Track_Id": 22,
      "Track_Name": "Daytona International Speedway",
      "Alt_Track_Name": "",
      "Track_Page_URL": "https://www.daytonainternationalspeedway.com/",
      "Track_Image_URL": "https://www.nascar.com/wp-content/uploads/...",
      "Track_Background_Image_URL": "https://www.nascar.com/wp-content/uploads/...",
      "Race_Date": "2026-02-15T14:30:00-0500",
      "Race_Date_Plain": "2026-02-15",
      "Race_Start": "2:30 PM",
      "Scheduled_Laps": 200,
      "Actual_Laps": 200,
      "Race_TV": "FOX",
      "Race_Radio": "MRN",
      "Race_Live_Stream": "SiriusXM",
      "Race_In_Car": "MAX",
      "Qualifying_Date": "2026-02-12T20:45:00-0500",
      "Playoff_Round": "",
      "Race_Tickets": "https://...",
      "Race_URL": "https://www.nascar.com/live-results/...",
      "Previous_Winner_Name": "William Byron",
      "Previous_Winner": 4015,
      "Average_Speed": 0
    }
  ]
}
```

**Key Fields**:
| Field | Description |
|-------|-------------|
| `Race_Id` | Unique race identifier |
| `Track_Id` | Unique track identifier |
| `Scheduled_Laps` | Number of scheduled laps |
| `Actual_Laps` | Actual laps completed (same as scheduled for future races) |
| `Race_Date` | ISO 8601 datetime with timezone |
| `Race_Date_Plain` | Date in YYYY-MM-DD format |
| `Qualifying_Date` | Qualifying session datetime |
| `Playoff_Round` | Playoff round designation (empty for regular season) |

**Note**: This API does NOT include:
- Race distance in miles (calculated as `track_length × laps`)
- Track length
- Track latitude/longitude coordinates

---

### Basic Race List

Returns a simplified list of races.

**Endpoint**: `https://cf.nascar.com/cacher/{year}/{series_id}/race_list_basic.json`

**Example**: `https://cf.nascar.com/cacher/2026/1/race_list_basic.json`

---

## Live Data APIs

### Live Race Feed

Real-time race data during active sessions.

**Endpoint**: `https://cf.nascar.com/cacher/staging/live/live-feed.json`

**Response Structure** (during active race):
```json
{
  "lap_number": 45,
  "elapsed_time": 3600,
  "flag_state": 1,
  "race_id": 5592,
  "laps_in_race": 200,
  "laps_to_go": 155,
  "track_id": 22,
  "track_length": 2.5,
  "track_name": "Daytona International Speedway",
  "vehicles": [...],
  "number_of_caution_segments": 2,
  "number_of_caution_laps": 8,
  "number_of_lead_changes": 12,
  "number_of_leaders": 5
}
```

**Note**: `track_length` is only populated during a live race.

---

### Current Results

**Endpoint**: `https://cf.nascar.com/data/cacher/production/live/current-results.json`

---

### Live Operations

**Endpoint**: `https://cf.nascar.com/live-ops/live-ops.json`

---

## Driver Data

### Drivers List

Returns all NASCAR drivers across all series.

**Endpoint**: `https://cf.nascar.com/cacher/drivers.json`

**Note**: This endpoint is loaded on driver-related pages but not on schedule pages. Contains 900+ driver records.

**Key Fields**:
- `Nascar_Driver_ID`
- `Driver_ID`
- `Driver_Series`
- `First_Name`, `Last_Name`, `Full_Name`
- `Hometown_City`, `Hometown_State`, `Hometown_Country`
- `Rookie_Year_Series_1/2/3`
- `Laps_Led`, `Stage_Wins` (career stats)

---

## Track Assets

### Track SVG Images

Vector track layouts are available at:

**Endpoint**: `https://cf.nascar.com/data/images/vector-tracks/svg/{track_id}.svg`

**Example**: `https://cf.nascar.com/data/images/vector-tracks/svg/22.svg` (Daytona)

---

## Known Limitations

1. **No Track Length API**: Track length is only available in the live-feed during active races. For calculating race distance, you would need a separate lookup table of track lengths.

2. **No Geolocation Data**: Track latitude/longitude coordinates are not provided in any discovered API. Location data would need to be obtained from a geocoding service using the track name and state.

3. **Rate Limiting**: Unknown, but APIs appear to be designed for website use. Aggressive scraping may result in blocks.

4. **CORS**: APIs may have CORS restrictions. Using a headless browser (Playwright/Puppeteer) bypasses this.

---

## Track Length Reference (for distance calculation)

Since track length is not available via API, here are known track lengths for reference:

| Track | Length (miles) |
|-------|---------------|
| Daytona International Speedway | 2.5 |
| Talladega Superspeedway | 2.66 |
| Charlotte Motor Speedway | 1.5 |
| Atlanta Motor Speedway | 1.54 |
| Bristol Motor Speedway | 0.533 |
| Martinsville Speedway | 0.526 |
| Phoenix Raceway | 1.0 |
| Las Vegas Motor Speedway | 1.5 |
| Texas Motor Speedway | 1.5 |
| Kansas Speedway | 1.5 |
| Michigan International Speedway | 2.0 |
| Pocono Raceway | 2.5 |
| Homestead-Miami Speedway | 1.5 |
| Darlington Raceway | 1.366 |
| Richmond Raceway | 0.75 |
| Dover Motor Speedway | 1.0 |
| Nashville Superspeedway | 1.33 |
| Gateway Motorsports Park | 1.25 |
| New Hampshire Motor Speedway | 1.058 |
| Sonoma Raceway | 1.99 (road) |
| Watkins Glen International | 2.45 (road) |
| Circuit of The Americas | 3.426 (road) |
| Indianapolis Motor Speedway (Road) | 2.439 (road) |
| Chicago Street Course | 2.2 (street) |

**Formula**: `Race Distance (miles) = Track Length × Scheduled Laps`

---

## Weather Forecast Integration

Since NASCAR APIs don't provide track coordinates, weather forecasts require geocoding. See `WEATHER_API.md` for recommendations.
