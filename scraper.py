"""
Danbooru API Scraper
Scrapes all posts from Danbooru API with resume capability and memory-efficient streaming.
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any
import logging

class DanbooruScraper:
    def __init__(self, 
                 output_file: str = "danbooru_posts.jsonl",
                 state_file: str = "scraper_state.json",
                 api_base_url: str = "https://danbooru.donmai.us",
                 posts_per_page: int = 200,
                 delay_between_requests: float = 1.0,
                 batch_size: int = 1000):
        """
        Initialize the Danbooru scraper.
        
        Args:
            output_file: Path to output JSONL file (streaming)
            state_file: Path to state file for resume capability
            api_base_url: Base URL for Danbooru API
            posts_per_page: Number of posts to fetch per API call (max 200)
            delay_between_requests: Delay in seconds between API requests
            batch_size: ID range batch size for scanning
        """
        self.output_file = output_file
        self.state_file = state_file
        self.api_base_url = api_base_url
        self.posts_per_page = min(posts_per_page, 200)  # Danbooru max is 200
        self.delay = delay_between_requests
        self.batch_size = batch_size
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load or initialize state
        self.state = self._load_state()
        
    def _load_state(self) -> Dict[str, Any]:
        """Load scraper state from file or create new state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.logger.info(f"Resuming from last saved state: {state}")
                    return state
            except Exception as e:
                self.logger.error(f"Error loading state file: {e}")
        
        # Default state - start from ID 1
        return {
            'last_processed_id': 0,
            'total_posts_scraped': 0,
            'last_update': None,
            'current_batch_start': 1
        }
    
    def _save_state(self):
        """Save current scraper state to file."""
        self.state['last_update'] = datetime.now().isoformat()
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
    
    def _get_highest_post_id(self) -> Optional[int]:
        """Get the highest post ID available on Danbooru."""
        try:
            url = f"{self.api_base_url}/posts.json"
            params = {'limit': 1, 'page': 1}
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            posts = response.json()
            if posts and len(posts) > 0:
                highest_id = posts[0]['id']
                self.logger.info(f"Highest post ID found: {highest_id}")
                return highest_id
            return None
        except Exception as e:
            self.logger.error(f"Error getting highest post ID: {e}")
            return None
    
    def _fetch_posts_by_id_range(self, min_id: int, max_id: int, page: int = 1) -> list:
        """
        Fetch posts within a specific ID range.
        
        Args:
            min_id: Minimum post ID
            max_id: Maximum post ID
            page: Page number (1-indexed)
            
        Returns:
            List of post dictionaries
        """
        try:
            url = f"{self.api_base_url}/posts.json"
            # Use tags parameter to filter by ID range: id:min..max
            params = {
                'tags': f"id:{min_id}..{max_id}",
                'limit': self.posts_per_page,
                'page': page
            }
            
            self.logger.info(f"Fetching: ID range {min_id}-{max_id}, page {page}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            posts = response.json()
            self.logger.info(f"Retrieved {len(posts)} posts")
            return posts
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return []
    
    def _append_posts_to_file(self, posts: list):
        """
        Append posts to output file in JSONL format (one JSON object per line).
        This ensures we never load all data into memory.
        """
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                for post in posts:
                    json_line = json.dumps(post, ensure_ascii=False)
                    f.write(json_line + '\n')
        except Exception as e:
            self.logger.error(f"Error writing to output file: {e}")
    
    def _scrape_id_range(self, min_id: int, max_id: int) -> int:
        """
        Scrape all posts within an ID range.
        
        Args:
            min_id: Minimum post ID
            max_id: Maximum post ID
            
        Returns:
            Number of posts scraped in this range
        """
        posts_scraped = 0
        page = 1
        max_pages = 1000  # Danbooru limit
        
        while page <= max_pages:
            # Fetch posts for current page
            posts = self._fetch_posts_by_id_range(min_id, max_id, page)
            
            if not posts:
                # No more posts in this range
                self.logger.info(f"No more posts in range {min_id}-{max_id} at page {page}")
                break
            
            # Append to file (streaming - never load all into memory)
            self._append_posts_to_file(posts)
            
            posts_scraped += len(posts)
            self.state['total_posts_scraped'] += len(posts)
            
            # Update last processed ID
            max_post_id = max(post['id'] for post in posts)
            if max_post_id > self.state['last_processed_id']:
                self.state['last_processed_id'] = max_post_id
            
            # Save state periodically
            self._save_state()
            
            self.logger.info(
                f"Progress: {posts_scraped} posts in current range, "
                f"{self.state['total_posts_scraped']} total"
            )
            
            # Check if we got fewer posts than requested (indicates end of range)
            if len(posts) < self.posts_per_page:
                self.logger.info(f"Received {len(posts)} posts (less than limit), end of range")
                break
            
            page += 1
            
            # Rate limiting - wait between requests
            time.sleep(self.delay)
        
        return posts_scraped
    
    def scrape_all(self):
        """
        Main method to scrape all posts from Danbooru.
        Uses ID-based batching to work around the 1000-page limit.
        """
        self.logger.info("=" * 50)
        self.logger.info("Starting Danbooru scraping session")
        self.logger.info("=" * 50)
        
        # Get the highest post ID to know our target
        highest_id = self._get_highest_post_id()
        if highest_id is None:
            self.logger.error("Could not determine highest post ID. Aborting.")
            return
        
        self.logger.info(f"Target highest ID: {highest_id}")
        
        # Start from where we left off
        current_min_id = self.state.get('current_batch_start', 1)
        
        # Process in batches
        while current_min_id <= highest_id:
            current_max_id = min(current_min_id + self.batch_size - 1, highest_id)
            
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Processing batch: IDs {current_min_id} to {current_max_id}")
            self.logger.info(f"{'='*50}")
            
            # Scrape this ID range
            batch_posts = self._scrape_id_range(current_min_id, current_max_id)
            
            self.logger.info(f"Batch complete: {batch_posts} posts scraped")
            
            # Move to next batch
            current_min_id = current_max_id + 1
            self.state['current_batch_start'] = current_min_id
            self._save_state()
            
            # Brief pause between batches
            time.sleep(self.delay)
        
        self.logger.info("\n" + "=" * 50)
        self.logger.info("SCRAPING COMPLETE!")
        self.logger.info(f"Total posts scraped: {self.state['total_posts_scraped']}")
        self.logger.info(f"Output file: {self.output_file}")
        self.logger.info("=" * 50)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current scraping statistics."""
        stats = {
            'total_posts_scraped': self.state['total_posts_scraped'],
            'last_processed_id': self.state['last_processed_id'],
            'last_update': self.state['last_update'],
            'output_file': self.output_file,
            'output_file_size_mb': 0
        }
        
        if os.path.exists(self.output_file):
            stats['output_file_size_mb'] = os.path.getsize(self.output_file) / (1024 * 1024)
        
        return stats


def main():
    """Main entry point for the scraper."""
    # Configuration
    scraper = DanbooruScraper(
        output_file="danbooru_posts.jsonl",
        state_file="scraper_state.json",
        api_base_url="https://danbooru.donmai.us",
        posts_per_page=200,  # Max allowed by Danbooru
        delay_between_requests=1.0,  # 1 second between requests (be respectful)
        batch_size=1000  # Process 1000 IDs at a time
    )
    
    # Start scraping
    try:
        scraper.scrape_all()
        
        # Print final statistics
        stats = scraper.get_statistics()
        print("\n" + "=" * 50)
        print("FINAL STATISTICS")
        print("=" * 50)
        for key, value in stats.items():
            print(f"{key}: {value}")
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        print("Progress has been saved. Run again to resume.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("Progress has been saved. Run again to resume.")


if __name__ == "__main__":
    main()
