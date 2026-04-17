#!/usr/bin/env python3
"""
GTS-HolMirDas: RSS-based content discovery for GoToSocial

Inspired by HolMirDas by @aliceif:
- GitHub: https://github.com/aliceif/HolMirDas
- Fediverse: @aliceif@mkultra.x27.one

This GoToSocial adaptation extends the original RSS-to-ActivityPub concept
with Docker deployment, multi-instance processing, and comprehensive monitoring.
"""

import os
import sys
import time
import json
import logging
import requests
import feedparser
from datetime import timedelta
from urllib.parse import quote_plus

class GTSHolMirDas:
    def __init__(self):
        """Initialize the RSS fetcher with configuration"""
        self.config = {
            "server_url": os.getenv("GTS_SERVER_URL", "https://your-gts-instance"),
            "access_token": os.getenv("GTS_ACCESS_TOKEN", ""),
            "max_posts_per_run": int(os.getenv("MAX_POSTS_PER_RUN", "25")),
            "delay_between_requests": int(os.getenv("DELAY_BETWEEN_REQUESTS", "2")),
            "healthcheck_url": os.getenv("HEALTHCHECK_URL", ""),
            "log_level": os.getenv("LOG_LEVEL", "INFO")
        }
        
        # Setup logging FIRST
        logging.basicConfig(
            level=getattr(logging, self.config["log_level"]),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load RSS URLs from file or environment
        rss_urls_file = os.getenv("RSS_URLS_FILE")
        if rss_urls_file and os.path.exists(rss_urls_file):
            # Load from file
            try:
                with open(rss_urls_file, 'r') as f:
                    self.config["rss_urls"] = [
                        line.split('#', 1)[0].strip() for line in f
                        if line.strip() and not line.strip().startswith('#')
                    ]
                self.logger.info(f"Loaded {len(self.config['rss_urls'])} RSS URLs from file: {rss_urls_file}")
            except Exception as e:
                self.logger.error(f"Could not load RSS URLs from file {rss_urls_file}: {e}")
                self.config["rss_urls"] = []
        else:
            # Fallback to environment variable
            self.config["rss_urls"] = [
                url.strip() for url in os.getenv("RSS_URLS", "").split(",") 
                if url.strip()
            ]
            if self.config["rss_urls"]:
                self.logger.info(f"Loaded {len(self.config['rss_urls'])} RSS URLs from environment")
        
        # Load processed URLs from persistent storage
        self.processed_urls_file = "/app/data/processed_urls.json"
        self.processed_urls = self.load_processed_urls()
        
        # Statistics tracking
        self.previous_instances = getattr(self, 'previous_instances', 0)

    def load_processed_urls(self):
        """Load previously processed URLs and instance count from file"""
        try:
            if os.path.exists(self.processed_urls_file):
                with open(self.processed_urls_file, 'r') as f:
                    data = json.load(f)
                    # Load previous instance count for statistics
                    self.previous_instances = data.get('previous_instances', 0)
                    return set(data.get('processed_urls', []))
        except Exception as e:
            self.logger.warning(f"Could not load processed URLs: {e}")
        
        return set()

    def save_processed_urls(self, current_instances=None):
        """Save processed URLs and current instance count to file"""
        try:
            os.makedirs(os.path.dirname(self.processed_urls_file), exist_ok=True)
            data = {
                'processed_urls': list(self.processed_urls),
                'last_updated': time.time()
            }
            # Save current instance count for next run
            if current_instances is not None and current_instances != 'unknown':
                data['previous_instances'] = current_instances
            
            with open(self.processed_urls_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save processed URLs: {e}")

    def fetch_rss_urls(self, rss_url):
        """Fetch URLs from RSS feed"""
        try:
            self.logger.info(f"Fetching RSS feed: {rss_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                self.logger.warning(f"RSS feed may have issues: {rss_url}")
            
            # Extract URLs from entries
            urls = []
            for entry in feed.entries:
                if hasattr(entry, 'link'):
                    urls.append(entry.link)
            
            self.logger.info(f"Found {len(urls)} URLs in RSS feed")
            return urls
            
        except Exception as e:
            self.logger.error(f"Error fetching RSS feed {rss_url}: {e}")
            return []

    def lookup_post(self, post_url):
        """Look up a post URL using GTS search API"""
        try:
            # Prepare search API call
            search_url = f"{self.config['server_url']}/api/v2/search"
            params = {
                'q': post_url,
                'type': 'statuses',
                'resolve': 'true',
                'limit': 1
            }
            headers = {
                'Authorization': f'Bearer {self.config["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            # Make API call
            response = requests.get(
                search_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                if results.get('statuses') or results.get('accounts'):
                    self.logger.info(f"Successfully looked up: {post_url}")
                    return True
                else:
                    self.logger.warning(f"No results for: {post_url}")
                    return False
            else:
                self.logger.error(f"API error {response.status_code} for {post_url}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error looking up {post_url}: {e}")
            return False

    def process_feeds(self):
        """Process all configured RSS feeds"""
        total_processed = 0

        # Record start time for statistics
        self.start_time = time.time()

        # Ping healthcheck start
        self.ping_healthcheck("/start")

        try:
            for rss_url in self.config["rss_urls"]:
                if not rss_url.strip():
                    continue

                self.logger.info(f"Processing feed: {rss_url}")

                # Get URLs from RSS
                urls = self.fetch_rss_urls(rss_url)

                # Filter out already processed URLs
                new_urls = [url for url in urls if url not in self.processed_urls]

                if not new_urls:
                    self.logger.info("No new URLs to process")
                    continue

                # Rate limiting: max posts per run
                urls_to_process = new_urls[:self.config["max_posts_per_run"]]

                self.logger.info(f"Processing {len(urls_to_process)} new URLs")

                for url in urls_to_process:
                    if self.lookup_post(url):
                        self.processed_urls.add(url)
                        total_processed += 1

                    # Rate limiting: delay between requests
                    time.sleep(self.config["delay_between_requests"])

            # Calculate runtime
            end_time = time.time()
            runtime_seconds = end_time - self.start_time
            runtime_formatted = str(timedelta(seconds=int(runtime_seconds)))
            
            # Get current instance count
            try:
                instance_info = requests.get(f"{self.config['server_url']}/api/v1/instance", 
                                           headers={'Authorization': f'Bearer {self.config["access_token"]}'}, 
                                           timeout=10)
                if instance_info.status_code == 200:
                    current_instances = instance_info.json().get('stats', {}).get('domain_count', 'unknown')
                else:
                    current_instances = 'unknown'
            except Exception as e:
                self.logger.error(f"Failed to get instance count: {e}")
                current_instances = 'unknown'
            
            # Calculate new instances (if we have previous data)
            new_instances = 'unknown'
            if self.previous_instances > 0 and current_instances != 'unknown':
                new_instances = current_instances - self.previous_instances
            
            # Print comprehensive statistics
            print(f"\n📊 GTS-HolMirDas Run Statistics:")
            print(f"   ⏱️  Runtime: {runtime_formatted}")
            print(f"   📄 Total posts processed: {total_processed}")
            print(f"   🌐 Current known instances: {current_instances}")
            if new_instances != 'unknown' and new_instances > 0:
                print(f"   ➕ New instances discovered: +{new_instances}")
            elif new_instances == 0:
                print(f"   ➕ New instances discovered: +0")
            print(f"   📡 RSS feeds processed: {len(self.config['rss_urls'])}")
            if runtime_seconds > 60:
                print(f"   ⚡ Posts per minute: {total_processed / (runtime_seconds / 60):.1f}")

            self.save_processed_urls(current_instances)

            # Ping healthcheck success
            self.ping_healthcheck("")

        except Exception as e:
            self.logger.error(f"Error during processing: {e}")
            # Ping healthcheck failure
            self.ping_healthcheck("/fail")
            raise

    def ping_healthcheck(self, endpoint=""):
        """Ping healthchecks.io for monitoring"""
        if not self.config.get("healthcheck_url"):
            return

        try:
            url = self.config["healthcheck_url"] + endpoint
            requests.get(url, timeout=10)
        except Exception as e:
            self.logger.warning(f"Failed to ping healthcheck: {e}")

def main():
    """Main entry point"""
    try:
        fetcher = GTSHolMirDas()

        # Validate required config
        if not fetcher.config["access_token"]:
            raise ValueError("GTS_ACCESS_TOKEN environment variable is required")

        fetcher.process_feeds()

    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
