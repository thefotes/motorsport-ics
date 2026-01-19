#!/usr/bin/env python3
"""
Generate ICS calendar file from NASCAR schedule data.
Import the generated .ics file into Google Calendar.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib


def generate_uid(race_id: int, series: str) -> str:
    """Generate a unique ID for the calendar event."""
    unique_string = f"{race_id}-{series}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:16] + "@nascar-scraper"


def escape_ics_text(text: str) -> str:
    """Escape special characters for ICS format."""
    if not text:
        return ""
    # Escape backslashes, semicolons, commas, and newlines
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


def parse_race_datetime(date_str: str) -> datetime | None:
    """Parse NASCAR date string to datetime object."""
    if not date_str:
        return None

    # Format: "2026-02-15T14:30:00-0500"
    try:
        # Handle timezone offset format
        if len(date_str) > 19:
            # Parse with timezone
            dt_str = date_str[:19]
            tz_str = date_str[19:]
            dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")

            # Parse timezone offset
            if tz_str:
                tz_sign = 1 if tz_str[0] == '+' else -1
                tz_hours = int(tz_str[1:3])
                tz_mins = int(tz_str[3:5]) if len(tz_str) >= 5 else 0
                # Note: We'll store as UTC for ICS
                offset = timedelta(hours=tz_hours, minutes=tz_mins) * tz_sign
                dt = dt - offset  # Convert to UTC
            return dt
        else:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except (ValueError, IndexError):
        return None


def format_ics_datetime(dt: datetime) -> str:
    """Format datetime for ICS (UTC format)."""
    return dt.strftime("%Y%m%dT%H%M%SZ")


def create_ics_event(race: dict, series_name: str) -> str:
    """Create a single VEVENT for a race."""
    race_name = race.get("race_name", "NASCAR Race")
    track_name = race.get("track_name", "")
    state = race.get("state", "")
    date_str = race.get("date", "")
    start_time = race.get("start_time", "")
    scheduled_laps = race.get("scheduled_laps", "")
    tv_network = race.get("tv_network", "")
    radio = race.get("radio", "")
    streaming = race.get("streaming", "")
    race_url = race.get("race_url", "")
    race_id = race.get("race_id", 0)

    # Parse datetime
    dt = parse_race_datetime(date_str)
    if not dt:
        return ""

    # Create end time (estimate 3-4 hours for a race)
    end_dt = dt + timedelta(hours=4)

    # Build location
    location = f"{track_name}, {state}" if track_name else ""

    # Build description
    desc_parts = [
        f"Series: {series_name}",
        f"Track: {track_name}",
    ]
    if scheduled_laps:
        desc_parts.append(f"Laps: {scheduled_laps}")
    if start_time:
        desc_parts.append(f"Start Time: {start_time} (local)")
    if tv_network:
        desc_parts.append(f"TV: {tv_network}")
    if radio:
        desc_parts.append(f"Radio: {radio}")
    if streaming:
        desc_parts.append(f"Streaming: {streaming}")
    if race_url:
        desc_parts.append(f"")
        desc_parts.append(f"More info: {race_url}")

    description = "\\n".join(desc_parts)

    # Generate unique ID
    uid = generate_uid(race_id, series_name)

    # Build VEVENT
    event_lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{format_ics_datetime(datetime.now(timezone.utc))}",
        f"DTSTART:{format_ics_datetime(dt)}",
        f"DTEND:{format_ics_datetime(end_dt)}",
        f"SUMMARY:{escape_ics_text(f'{race_name} ({series_name})')}",
        f"LOCATION:{escape_ics_text(location)}",
        f"DESCRIPTION:{description}",
    ]

    if race_url:
        event_lines.append(f"URL:{race_url}")

    event_lines.append("END:VEVENT")

    return "\n".join(event_lines)


def generate_ics_calendar(schedule_file: str, output_file: str) -> int:
    """Generate ICS calendar from NASCAR schedule JSON."""

    # Load schedule data
    with open(schedule_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Get all races chronologically
    races = data.get("all_races_chronological", [])

    # ICS header
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//NASCAR Scraper//nascar-scraper//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:2026 NASCAR Schedule",
        "X-WR-TIMEZONE:America/New_York",
    ]

    # Track events added (avoid duplicates by race_id)
    added_events = set()
    event_count = 0

    for race in races:
        race_id = race.get("race_id")
        series = race.get("series", "")

        # Skip if we've already added this race (some races appear in multiple series)
        event_key = f"{race_id}-{series}"
        if event_key in added_events:
            continue

        event = create_ics_event(race, series)
        if event:
            ics_lines.append(event)
            added_events.add(event_key)
            event_count += 1

    # ICS footer
    ics_lines.append("END:VCALENDAR")

    # Write ICS file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(ics_lines))

    return event_count


def main():
    schedule_file = "nascar_schedules_2026.json"
    output_file = "nascar_2026_calendar.ics"

    if not Path(schedule_file).exists():
        print(f"Error: {schedule_file} not found. Run scrape_nascar.py first.")
        return

    print("Generating ICS calendar file...")
    event_count = generate_ics_calendar(schedule_file, output_file)

    print(f"\nCreated: {output_file}")
    print(f"Total events: {event_count}")
    print("\nTo import into Google Calendar:")
    print("1. Go to Google Calendar")
    print("2. Click the gear icon → Settings")
    print("3. Click 'Import & export' in the left sidebar")
    print("4. Click 'Select file from your computer'")
    print("5. Select the generated .ics file")
    print("6. Choose your '2026 NASCAR' calendar")
    print("7. Click 'Import'")


if __name__ == "__main__":
    main()
