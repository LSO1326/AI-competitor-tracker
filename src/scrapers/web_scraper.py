import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Dict, List, Optional, Tuple
import logging
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import hashlib
from datetime import datetime
import feedparser

class WebScraper:
    def __init__(self, rate_limit: float = 2.0):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.rate_limit = rate_limit
        self.last_request_time = {}
        self.logger = logging.getLogger(__name__)

        # Set default headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.8,application/signed-exchange;v=b3;q=0.9'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-US,en;q=0.8',
                'en-US,en;q=0.7,es;q=0.3'
            ])
        }

    def _respect_rate_limit(self, domain: str):
        """Implement rate limiting per domain"""
        current_time = time.time()

        if domain in self.last_request_time:
            time_diff = current_time - self.last_request_time[domain]
            if time_diff < self.rate_limit:
                sleep_time = self.rate_limit - time_diff + random.uniform(0.5, 1.5)
                time.sleep(sleep_time)

        self.last_request_time[domain] = time.time()

    def _make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retries and error handling"""
        domain = urlparse(url).netloc

        for attempt in range(max_retries):
            try:
                self._respect_rate_limit(domain)

                # Update headers for each request
                self.session.headers.update(self._get_random_headers())

                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt + random.uniform(1, 3)
                    self.logger.warning(f"Rate limited on {url}, waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")

            except requests.RequestException as e:
                self.logger.error(f"Request failed for {url}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)

        return None

    def scrape_rss_feed(self, rss_url: str) -> List[Dict]:
        """Scrape RSS feed as fallback method"""
        try:
            feed = feedparser.parse(rss_url)
            articles = []

            for entry in feed.entries[:10]:  # Get latest 10 articles
                article = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'content': entry.get('summary', ''),
                    'date': entry.get('published', ''),
                    'source': 'RSS'
                }
                articles.append(article)

            self.logger.info(f"Successfully scraped {len(articles)} articles from RSS")
            return articles

        except Exception as e:
            self.logger.error(f"RSS feed scraping failed: {e}")
            return []

    def extract_articles(self, url: str, selectors: Dict[str, str], rss_url: str = None) -> List[Dict]:
        """Extract articles from a webpage"""
        response = self._make_request(url)

        if not response:
            # Try RSS feed as fallback
            if rss_url:
                self.logger.info(f"Falling back to RSS for {url}")
                return self.scrape_rss_feed(rss_url)
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []

        # Find article links
        article_links = soup.select('a[href]')
        article_urls = set()

        for link in article_links[:20]:  # Limit to first 20 links
            href = link.get('href')
            if href and self._is_article_url(href, url):
                full_url = urljoin(url, href)
                article_urls.add(full_url)

        # Extract content from each article
        for article_url in list(article_urls)[:10]:  # Process max 10 articles
            article_data = self.scrape_article(article_url, selectors)
            if article_data:
                articles.append(article_data)

        return articles

    def scrape_article(self, url: str, selectors: Dict[str, str]) -> Optional[Dict]:
        """Scrape individual article content"""
        response = self._make_request(url)
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try multiple selectors for each field
        title = self._extract_with_fallback(soup, selectors.get('title', '').split(','))
        content = self._extract_with_fallback(soup, selectors.get('content', '').split(','))
        date = self._extract_with_fallback(soup, selectors.get('date', '').split(','))

        if not title:
            return None

        # Generate content hash for deduplication
        content_hash = hashlib.md5(f"{title}{content}".encode()).hexdigest()

        return {
            'title': title.strip() if title else '',
            'content': self._clean_content(content) if content else '',
            'url': url,
            'date': date.strip() if date else str(datetime.now()),
            'hash': content_hash,
            'source': urlparse(url).netloc
        }

    def _extract_with_fallback(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Try multiple CSS selectors until one works"""
        for selector in selectors:
            selector = selector.strip()
            if not selector:
                continue

            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text() if hasattr(element, 'get_text') else str(element)
            except Exception as e:
                self.logger.debug(f"Selector failed: {selector} - {e}")
                continue

        return None

    def _clean_content(self, content: str) -> str:
        """Clean and summarize content"""
        if not content:
            return ""

        # Remove extra whitespace
        content = ' '.join(content.split())

        # Truncate to first 500 words
        words = content.split()
        if len(words) > 500:
            content = ' '.join(words[:500]) + "..."

        return content

    def _is_article_url(self, href: str, base_url: str) -> bool:
        """Determine if URL likely points to an article"""
        if not href:
            return False

        # Skip non-relevant URLs
        skip_patterns = [
            'javascript:', 'mailto:', 'tel:', '#',
            '/tag/', '/category/', '/author/',
            '/search/', '/login/', '/register/'
        ]

        for pattern in skip_patterns:
            if pattern in href.lower():
                return False

        # Look for article indicators
        article_indicators = [
            '/blog/', '/news/', '/article/', '/post/',
            '/2024/', '/2023/', '/ai/', '/artificial-intelligence'
        ]

        return any(indicator in href.lower() for indicator in article_indicators)