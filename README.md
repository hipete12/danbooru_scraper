# Danbooru API Scraper

A robust, memory-efficient Python scraper for downloading all posts from the Danbooru API with built-in resume capability and rate limiting.

## Features

✅ **Complete Data Collection**: Scrapes all available post information from Danbooru  
✅ **Memory Efficient**: Streams data to disk using JSONL format - never loads all data into memory  
✅ **Resume Capability**: Automatically saves progress and resumes from where it left off  
✅ **ID-Based Batching**: Works around the 1000-page API limit by using ID ranges  
✅ **Rate Limiting**: Built-in delays to respect server resources  
✅ **Comprehensive Logging**: Detailed logs of scraping progress  
✅ **Error Handling**: Gracefully handles network errors and interruptions  

## Requirements

- Python 3.7 or higher
- requests library

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Simply run the scraper:
```bash
python scraper.py
```

The scraper will:
1. Start from post ID 1 (or resume from the last saved state)
2. Fetch posts in batches of 1000 IDs at a time
3. Save all post data to `danbooru_posts.jsonl`
4. Save progress to `scraper_state.json`
5. Log all activity to `scraper.log` and console

### Resume After Interruption

If the scraper is interrupted (Ctrl+C, network error, etc.), simply run it again:
```bash
python scraper.py
```

It will automatically resume from where it left off using the saved state.

### Configuration

You can modify scraping parameters in [config.py](config.py):

- `POSTS_PER_PAGE`: Number of posts per API call (max 200)
- `DELAY_BETWEEN_REQUESTS`: Delay between requests in seconds (default: 1.0)
- `BATCH_SIZE`: ID range size for batching (default: 1000)
- `OUTPUT_FILE`: Output filename (default: "danbooru_posts.jsonl")

## Output Format

The scraper saves data in **JSONL** (JSON Lines) format, where each line is a complete JSON object representing one post. This format:
- Never requires loading the entire dataset into memory
- Can be processed line-by-line
- Is easy to parse and filter

Example output file structure:
```jsonl
{"id": 1, "created_at": "...", "tags": "...", ...}
{"id": 2, "created_at": "...", "tags": "...", ...}
{"id": 3, "created_at": "...", "tags": "...", ...}
```

### Reading the Output

To read and process the scraped data:

```python
import json

# Process line by line (memory efficient)
with open('danbooru_posts.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        post = json.loads(line)
        # Process each post
        print(f"Post ID: {post['id']}")
```

## How It Works

### ID-Based Batching Strategy

Danbooru's API has a 1000-page limit per query. To work around this, the scraper:

1. Uses the `tags` parameter with ID ranges: `id:1..1000`, `id:1001..2000`, etc.
2. Processes each batch completely (up to 1000 pages per batch)
3. Moves to the next ID range automatically
4. Continues until all posts are scraped

### State Management

Progress is saved in `scraper_state.json`:
```json
{
  "last_processed_id": 5000,
  "total_posts_scraped": 4850,
  "current_batch_start": 5001,
  "last_update": "2026-02-16T10:30:00"
}
```

### Rate Limiting

The scraper includes built-in delays to be respectful to Danbooru's servers:
- 1 second delay between API requests (configurable)
- Additional delay between ID batches
- Timeout handling for slow responses

## API Reference

The scraper uses Danbooru's public JSON API:
- Base URL: `https://danbooru.donmai.us`
- Endpoint: `/posts.json`
- Parameters:
  - `tags`: Filter by tags (including ID ranges)
  - `limit`: Posts per page (max 200)
  - `page`: Page number (max 1000)

## Monitoring Progress

### Check Logs
```bash
# View real-time progress
tail -f scraper.log  # Linux/Mac
Get-Content scraper.log -Wait  # Windows PowerShell
```

### Check Statistics
The scraper displays progress in the console and logs:
- Current ID range being processed
- Posts scraped in current batch
- Total posts scraped
- Output file size

### Check Output File Size
```bash
# Linux/Mac
ls -lh danbooru_posts.jsonl

# Windows PowerShell
Get-Item danbooru_posts.jsonl | Select-Object Name, @{Name="Size (MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

## Troubleshooting

### "Connection Error" or "Timeout"
- Check your internet connection
- The scraper will automatically retry
- If persistent, increase `REQUEST_TIMEOUT` in the code

### "Too Many Requests" (429 Error)
- Increase `DELAY_BETWEEN_REQUESTS` in [config.py](config.py)
- Consider getting a Danbooru account for higher rate limits

### Scraper Seems Stuck
- Check `scraper.log` for detailed status
- Some ID ranges may have few or no posts
- The scraper will automatically skip empty ranges

### Want to Start Over
Delete the state file to start fresh:
```bash
rm scraper_state.json  # Linux/Mac
del scraper_state.json  # Windows
```

## Performance Estimates

Based on Danbooru's API limits and rate limiting:
- ~200 posts per request
- ~1 second delay between requests
- ~12,000 posts per hour (at 200 posts/request * 60 requests/minute)
- ~288,000 posts per day

Actual performance may vary based on:
- Network speed
- Server response time
- Number of posts returned per request

## Advanced Usage

### Custom ID Range
To scrape a specific ID range, modify the scraper:

```python
scraper = DanbooruScraper(...)
scraper.state['current_batch_start'] = 10000  # Start from ID 10000
scraper.scrape_all()
```

### Filter by Tags
To scrape posts with specific tags, combine ID ranges with tag filters in the code.

### Add Authentication
If you have a Danbooru account, add your credentials to [config.py](config.py) for higher rate limits.

## License

This scraper is provided as-is for educational purposes. Please respect Danbooru's Terms of Service and API usage guidelines.

## Contributing

Feel free to submit issues or pull requests to improve the scraper!

## Notes

- Always respect Danbooru's Terms of Service
- Be considerate with rate limiting
- The scraper is designed for complete archival purposes
- Large downloads may take several days depending on the total number of posts
