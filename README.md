# Motorsport ICS

Auto-updating ICS calendar feeds for motorsport schedules. Subscribe to the calendar URL in Google Calendar, Apple Calendar, or any calendar app that supports ICS subscriptions.

## Calendar Feeds

| Series | Subscribe URL |
|--------|---------------|
| All Series (Combined) | `https://raw.githubusercontent.com/thefotes/motorsport-ics/main/nascar_2026_calendar.ics` |

## How to Subscribe

### Google Calendar
1. Go to [Google Calendar](https://calendar.google.com)
2. Click the **+** next to "Other calendars"
3. Select **"From URL"**
4. Paste the subscribe URL from above
5. Click **"Add calendar"**

Google will automatically refresh the calendar every 12-24 hours.

### Apple Calendar
1. Open Calendar app
2. File → New Calendar Subscription
3. Paste the subscribe URL
4. Set auto-refresh to your preference

### Other Calendar Apps
Most calendar apps support ICS URL subscriptions. Look for "Add calendar from URL" or "Subscribe to calendar" in your app's settings.

## Data Included

Each event includes:
- Race name and series
- Track location
- Scheduled laps
- TV network, radio, and streaming info
- Link to official race page

## Update Schedule

The calendar is automatically updated weekly via GitHub Actions. Schedule changes from the official source are reflected within a week.

## Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install playwright
playwright install chromium

# Run scraper
python scrape_nascar.py

# Generate calendar
python generate_calendar.py
```

## License

MIT
