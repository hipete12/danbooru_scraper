"""
Configuration file for Danbooru scraper.
Modify these settings according to your needs.
"""

# API Configuration
API_BASE_URL = "https://danbooru.donmai.us"

# Scraping Parameters
POSTS_PER_PAGE = 200  # Maximum allowed by Danbooru API
DELAY_BETWEEN_REQUESTS = 1.0  # Seconds to wait between API requests (be respectful!)
BATCH_SIZE = 1000  # Number of IDs to process in each batch

# File Configuration
OUTPUT_FILE = "danbooru_posts.jsonl"  # Output file in JSON Lines format
STATE_FILE = "scraper_state.json"  # State file for resume capability
LOG_FILE = "scraper.log"  # Log file for detailed logging

# Optional: Add authentication if you have a Danbooru account
# Having an account typically gives you higher rate limits
DANBOORU_USERNAME = None  # Set to your username or None
DANBOORU_API_KEY = None  # Set to your API key or None

# Advanced Settings
REQUEST_TIMEOUT = 30  # Timeout for API requests in seconds
MAX_RETRIES = 3  # Number of retries for failed requests
RETRY_DELAY = 5  # Seconds to wait before retrying a failed request
