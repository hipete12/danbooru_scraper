# Quick Start Guide

## First Time Setup

1. Install Python dependencies:
```powershell
pip install -r requirements.txt
```

2. Run the scraper:
```powershell
python scraper.py
```

## What Happens

The scraper will:
- Start downloading posts from Danbooru API
- Save data to `danbooru_posts.jsonl` (one JSON object per line)
- Save progress to `scraper_state.json`
- Log activity to `scraper.log` and console

## Interrupting and Resuming

- Press `Ctrl+C` to stop the scraper at any time
- Run `python scraper.py` again to resume from where you left off
- The scraper automatically saves progress after each batch

## Monitoring Progress

View the log file in real-time:
```powershell
Get-Content scraper.log -Wait
```

Check how much data has been collected:
```powershell
Get-Item danbooru_posts.jsonl | Select-Object Name, @{Name="Size (MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

## Analyzing Downloaded Data

Once you have some data, run the analysis script:
```powershell
python analyze_posts.py
```

This will show you:
- Total post count
- Sample post structure
- Rating distribution
- Most common tags
- Date range

## Adjusting Settings

Edit `config.py` to change:
- `DELAY_BETWEEN_REQUESTS`: Increase to be more conservative (default: 1.0 second)
- `BATCH_SIZE`: Size of ID ranges to process (default: 1000)
- `POSTS_PER_PAGE`: Posts per API call (max 200, default: 200)

## Starting Over

To start fresh from the beginning:
```powershell
# Delete state file
del scraper_state.json

# Optionally delete the data file
del danbooru_posts.jsonl

# Optionally delete the log file
del scraper.log
```

## Troubleshooting

### Error: "No module named 'requests'"
Install dependencies: `pip install -r requirements.txt`

### Scraper seems slow
This is normal! The scraper includes delays to respect the server. Expected rate: ~12,000 posts per hour.

### Want to see what data looks like
Check the README.md or run `python analyze_posts.py` after collecting some data.

## Tips

- Let the scraper run in the background - it can take days to complete depending on total posts
- The JSONL format means you can start analyzing data even while scraping is ongoing
- Monitor disk space - the final file can be quite large depending on how many posts exist
- If you have a Danbooru account, add credentials to `config.py` for potentially higher rate limits
