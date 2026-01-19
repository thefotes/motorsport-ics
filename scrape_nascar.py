#!/usr/bin/env python3
"""
NASCAR Schedule Scraper
Scrapes schedules for Cup Series, Xfinity Series, and Craftsman Truck Series
Uses direct API endpoints discovered from the NASCAR website.
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

# NASCAR API endpoints (discovered from website network traffic)
# Series IDs: 1 = Cup Series, 2 = Xfinity Series, 3 = Craftsman Truck Series
SERIES_CONFIG = {
    "nascar_cup_series": {
        "name": "NASCAR Cup Series",
        "series_id": 1,
        "api_url": "https://cf.nascar.com/cacher/2026/1/schedule-combined-feed.json",
    },
    "xfinity_series": {
        "name": "NASCAR Xfinity Series",
        "series_id": 2,
        "api_url": "https://cf.nascar.com/cacher/2026/2/schedule-combined-feed.json",
    },
    "craftsman_truck_series": {
        "name": "NASCAR Craftsman Truck Series",
        "series_id": 3,
        "api_url": "https://cf.nascar.com/cacher/2026/3/schedule-combined-feed.json",
    },
}


def clean_string(value) -> str:
    """Clean string values - strip whitespace and handle None."""
    if value is None:
        return ""
    return str(value).strip()


def extract_race_info(race: dict) -> dict:
    """Extract relevant race information from API response."""
    return {
        "race_name": clean_string(race.get("Race_Name")),
        "race_id": race.get("Race_Id"),
        "track_name": clean_string(race.get("Track_Name")),
        "track_id": race.get("Track_Id"),
        "state": clean_string(race.get("Race_State")),
        "date": clean_string(race.get("Race_Date")),
        "date_plain": clean_string(race.get("Race_Date_Plain")),
        "start_time": clean_string(race.get("Race_Start")),
        "scheduled_laps": race.get("Scheduled_Laps"),
        "actual_laps": race.get("Actual_Laps"),
        "qualifying_date": clean_string(race.get("Qualifying_Date")),
        "playoff_round": clean_string(race.get("Playoff_Round")),
        "tv_network": clean_string(race.get("Race_TV")),
        "radio": clean_string(race.get("Race_Radio")),
        "streaming": clean_string(race.get("Race_Live_Stream")),
        "in_car_camera": clean_string(race.get("Race_In_Car")),
        "tickets_url": clean_string(race.get("Race_Tickets")),
        "race_url": clean_string(race.get("Race_URL")),
        "previous_winner": clean_string(race.get("Previous_Winner_Name")),
    }


def extract_track_info(race: dict) -> dict:
    """Extract track information from a race entry."""
    return {
        "track_id": race.get("Track_Id"),
        "track_name": clean_string(race.get("Track_Name")),
        "alt_track_name": clean_string(race.get("Alt_Track_Name")),
        "state": clean_string(race.get("Race_State")),
        "track_page_url": clean_string(race.get("Track_Page_URL")),
        "track_image_url": clean_string(race.get("Track_Image_URL")),
        "track_background_image_url": clean_string(race.get("Track_Background_Image_URL")),
    }


async def fetch_schedule_via_browser(series_key: str, config: dict) -> tuple[dict, list]:
    """Fetch schedule data by intercepting API calls during page load."""
    api_url = config["api_url"]
    schedule_data = None
    raw_races = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        async def handle_response(response):
            nonlocal schedule_data, raw_races
            if api_url in response.url:
                try:
                    data = await response.json()
                    schedule_data = data
                    if "response" in data:
                        raw_races = data["response"]
                except Exception:
                    pass

        page.on("response", handle_response)

        # Navigate to trigger the API call
        if "cup" in series_key:
            web_url = "https://www.nascar.com/nascar-cup-series/2026/schedule/"
        elif "xfinity" in series_key:
            web_url = "https://www.nascar.com/nascar-xfinity-series/2026/schedule/"
        else:
            web_url = "https://www.nascar.com/nascar-craftsman-truck-series/2026/schedule/"

        try:
            await page.goto(web_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"  Page load issue (expected): {e}")

        await browser.close()

    return schedule_data, raw_races


async def main():
    print("=" * 60)
    print("NASCAR Schedule Scraper")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    all_schedules = {}
    all_races_flat = []
    all_tracks = {}  # Track ID -> track info

    for series_key, config in SERIES_CONFIG.items():
        print(f"\nFetching {config['name']}...")
        print(f"  API: {config['api_url']}")

        schedule_data, raw_races = await fetch_schedule_via_browser(series_key, config)

        if schedule_data and raw_races:
            races = [extract_race_info(race) for race in raw_races]

            # Extract track info from raw races
            for race in raw_races:
                track_id = race.get("Track_Id")
                if track_id and track_id not in all_tracks:
                    all_tracks[track_id] = extract_track_info(race)

            # Sort by date
            races.sort(key=lambda x: x["date_plain"])

            all_schedules[series_key] = {
                "series_name": config["name"],
                "series_id": config["series_id"],
                "total_races": len(races),
                "races": races,
            }

            # Add to flat list with series identifier
            for race in races:
                race_with_series = race.copy()
                race_with_series["series"] = config["name"]
                race_with_series["series_key"] = series_key
                all_races_flat.append(race_with_series)

            print(f"  Found {len(races)} races")

            # Print first few races as preview
            for race in races[:3]:
                print(f"    - {race['date_plain']}: {race['race_name']} @ {race['track_name']}")
            if len(races) > 3:
                print(f"    ... and {len(races) - 3} more races")
        else:
            print(f"  ERROR: Could not fetch schedule data")
            all_schedules[series_key] = {
                "series_name": config["name"],
                "series_id": config["series_id"],
                "error": "Failed to fetch data",
            }

    # Sort flat list by date
    all_races_flat.sort(key=lambda x: x["date_plain"])

    # Convert tracks dict to sorted list
    tracks_list = sorted(all_tracks.values(), key=lambda x: x["track_name"])

    # Save detailed JSON output
    output = {
        "scraped_at": datetime.now().isoformat(),
        "year": 2026,
        "schedules_by_series": all_schedules,
        "all_races_chronological": all_races_flat,
    }

    output_file = "nascar_schedules_2026.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n{'=' * 60}")
    print(f"Saved detailed schedule to: {output_file}")

    # Save tracks data
    tracks_output = {
        "scraped_at": datetime.now().isoformat(),
        "total_tracks": len(tracks_list),
        "tracks": tracks_list,
    }
    tracks_file = "nascar_tracks_2026.json"
    with open(tracks_file, "w", encoding="utf-8") as f:
        json.dump(tracks_output, f, indent=2, ensure_ascii=False)
    print(f"Saved tracks data to: {tracks_file}")

    # Save a human-readable CSV
    csv_file = "nascar_schedules_2026.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("Series,Date,Race Name,Track,State,Start Time,Laps,TV,Streaming,Previous Winner\n")
        for race in all_races_flat:
            # Escape commas and quotes in fields for proper CSV
            def escape_csv(val):
                if val is None:
                    return ""
                val = str(val).replace('"', '""')
                if ',' in val or '"' in val or '\n' in val:
                    return f'"{val}"'
                return val

            row = [
                escape_csv(race.get("series", "")),
                escape_csv(race.get("date_plain", "")),
                escape_csv(race.get("race_name", "")),
                escape_csv(race.get("track_name", "")),
                escape_csv(race.get("state", "")),
                escape_csv(race.get("start_time", "")),
                escape_csv(race.get("scheduled_laps")),
                escape_csv(race.get("tv_network", "")),
                escape_csv(race.get("streaming", "")),
                escape_csv(race.get("previous_winner", "")),
            ]
            f.write(",".join(row) + "\n")
    print(f"Saved CSV schedule to: {csv_file}")

    # Summary
    total_races = sum(
        s.get("total_races", 0) for s in all_schedules.values() if "total_races" in s
    )
    print(f"\nTotal races across all series: {total_races}")
    print(f"Total unique tracks: {len(tracks_list)}")
    print("=" * 60)

    return output


if __name__ == "__main__":
    asyncio.run(main())
