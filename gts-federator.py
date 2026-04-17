#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
import requests
import feedparser
from datetime import timedelta, datetime

class GTSHolMirDas:
    def __init__(self):
        self.config = {
            "server_url": os.getenv("GTS_SERVER_URL", "").rstrip('/'),
            "access_token": os.getenv("GTS_ACCESS_TOKEN", ""),
            "max_posts_per_run": int(os.getenv("MAX_POSTS_PER_RUN", "25")),
            "delay_between_requests": int(os.getenv("DELAY_BETWEEN_REQUESTS", "2")),
            "fetch_interval": os.getenv("FETCH_INTERVAL", "30m"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "rss_urls_file": os.getenv("RSS_URLS_FILE", "/app/rss_feeds.txt"),
            "user_agent": os.getenv("USER_AGENT", "GTS-Federation-Bot/1.0 (+https://social.ztfr.eu)")
        }
        
        logging.basicConfig(
            level=getattr(logging, self.config["log_level"]),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.db_path = os.getenv("DATABASE_PATH", "/app/data/processed_urls.json")
        
        self.processed_urls, self.previous_instances = self.load_state()
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config['access_token']}",
            "User-Agent": self.config['user_agent']
        })

    def parse_interval(self, interval_str):
        unit = interval_str[-1].lower()
        try:
            val = int(interval_str[:-1])
            return val * {'s': 1, 'm': 60, 'h': 3600}.get(unit, 60)
        except:
            return 1800

    def load_state(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed_urls', [])), data.get('previous_instances', 0)
            except Exception as e:
                self.logger.warning(f"Unable to load database: {e}")
        return set(), 0

    def save_state(self, current_instances):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            url_list = list(self.processed_urls)[-5000:]
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump({'processed_urls': url_list, 'previous_instances': current_instances}, f, indent=2)
        except Exception as e:
            self.logger.error(f"Save error: {e}")

    def process_feeds(self):
        self.logger.info(f"📂 Start Fetching. Database: {self.db_path}")

        if not os.path.exists(self.config["rss_urls_file"]):
            self.logger.error("RSS_URLS_FILE missing!")
            return

        with open(self.config["rss_urls_file"], 'r', encoding='utf-8') as f:
            rss_urls = [l.split('#')[0].strip() for l in f if l.strip() and not l.strip().startswith('#')]

        total_new = 0
        start_time = time.time()

        for i, rss_url in enumerate(rss_urls, 1):
            self.logger.info(f"[{i}/{len(rss_urls)}] 📡 {rss_url}")
            try:
                resp = requests.get(rss_url, timeout=15, headers={"User-Agent": self.config['user_agent']})
                feed = feedparser.parse(resp.content)
                
                if not feed.entries:
                    continue

                new_links = [e.link for e in feed.entries if hasattr(e, 'link') and e.link not in self.processed_urls]
                
                if new_links:
                    for url in new_links[:self.config["max_posts_per_run"]]:
                        try:
                            r = self.session.get(
                                f"{self.config['server_url']}/api/v2/search", 
                                params={'q': url, 'resolve': 'true', 'limit': 1}, 
                                timeout=30 
                            )
                            if r.status_code == 200:
                                self.processed_urls.add(url)
                                total_new += 1
                            elif r.status_code == 429:
                                self.logger.warning("Rate limit hit! Waiting 10s...")
                                time.sleep(10)
                            
                            time.sleep(self.config["delay_between_requests"])
                        except Exception as e:
                            self.logger.error(f"Error processing post {url}: {e}")
                    
                    self.save_state(self.previous_instances)

            except Exception as e:
                self.logger.error(f"Error fetching feed {rss_url}: {e}")

        try:
            ri = self.session.get(f"{self.config['server_url']}/api/v1/instance", timeout=10)
            curr = ri.json().get('stats', {}).get('domain_count', 0)
            diff = max(0, curr - self.previous_instances) if self.previous_instances else 0
        except:
            curr, diff = self.previous_instances, 0

        runtime = str(timedelta(seconds=int(time.time() - start_time)))
        print(f"\n✅ Run Completed | Time: {runtime} | New Posts: {total_new} | Instances: {curr} (+{diff})")
        self.save_state(curr)

    def run_forever(self):
        wait_seconds = self.parse_interval(self.config["fetch_interval"])
        self.logger.info(f"GTS-Federator Active. Interval: {self.config['fetch_interval']}")
        while True:
            self.process_feeds()
            
            next_run = datetime.now() + timedelta(seconds=wait_seconds)
            self.logger.info(f"💤 Run completed. Pausing for {self.config['fetch_interval']}.")
            self.logger.info(f"⏰ Next scheduled run: {next_run.strftime('%H:%M:%S')}")
            
            time.sleep(wait_seconds)

if __name__ == "__main__":
    bot = GTSHolMirDas()
    if not bot.config["access_token"]:
        sys.exit("Error: GTS_ACCESS_TOKEN missing!")
    bot.run_forever()