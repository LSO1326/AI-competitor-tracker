import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
import hashlib

from .web_scraper import WebScraper

class GoogleResearchScraper(WebScraper):
    """
    Specialized scraper for Google Research Blog with enhanced capabilities
    for handling their specific structure and pagination
    """

    def __init__(self, rate_limit: float = 3.0):
        super().__init__(rate_limit)
        self.base_url = "https://research.google"
        self.blog_url = "https://research.google/blog/"
        self.logger = logging.getLogger(__name__)

    def extract_google_articles(self, max_pages: int = 3) -> List[Dict]:
        """
        Extract articles from Google Research blog with pagination support
        """
        all_articles = []

        for page in range(1, max_pages + 1):
            page_url = f"{self.blog_url}?page={page}" if page > 1 else self.blog_url

            self.logger.info(f"Scraping Google Research blog page {page}")

            response = self._make_request(page_url)
            if not response:
                self.logger.warning(f"Failed to fetch page {page}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self._extract_articles_from_page(soup)

            if not articles:
                self.logger.info(f"No articles found on page {page}, stopping pagination")
                break

            all_articles.extend(articles)

            # Be respectful with pagination requests
            if page < max_pages:
                time.sleep(self.rate_limit + 1)

        self.logger.info(f"Extracted {len(all_articles)} articles from Google Research blog")
        return all_articles

    def _extract_articles_from_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract articles from a single page"""
        articles = []

        # Look for article containers - Google Research uses various patterns
        article_selectors = [
            'article',
            '.blog-post',
            '[href*="/blog/"]',
            'a[href^="/blog/"]'
        ]

        article_links = set()

        # Find all article links
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                if element.name == 'a':
                    href = element.get('href')
                    if href and '/blog/' in href and href != '/blog/':
                        full_url = urljoin(self.base_url, href)
                        article_links.add(full_url)
                else:
                    # Look for links within the element
                    links = element.select('a[href*="/blog/"]')
                    for link in links:
                        href = link.get('href')
                        if href and href != '/blog/':
                            full_url = urljoin(self.base_url, href)
                            article_links.add(full_url)

        # Also try to extract article data directly from the listing page
        self._extract_listing_data(soup, articles)

        # Extract individual articles
        for article_url in list(article_links)[:10]:  # Limit to 10 per page
            if self._is_valid_article_url(article_url):
                article_data = self._scrape_google_article(article_url)
                if article_data:
                    articles.append(article_data)

        return articles

    def _extract_listing_data(self, soup: BeautifulSoup, articles: List[Dict]):
        """Extract article data directly from listing page"""
        # Try to find article previews on the main page
        preview_selectors = [
            '.blog-preview',
            '.post-preview',
            '.article-preview'
        ]

        for selector in preview_selectors:
            previews = soup.select(selector)
            for preview in previews:
                title_elem = preview.select_one('h2, h3, .title, a')
                link_elem = preview.select_one('a[href*="/blog/"]')
                date_elem = preview.select_one('time, .date, .published')

                if title_elem and link_elem:
                    article_data = {
                        'title': title_elem.get_text().strip(),
                        'url': urljoin(self.base_url, link_elem.get('href')),
                        'date': date_elem.get_text().strip() if date_elem else '',
                        'content': '',
                        'source': 'research.google',
                        'preview_extracted': True
                    }

                    # Generate hash
                    content_hash = hashlib.md5(f"{article_data['title']}{article_data['url']}".encode()).hexdigest()
                    article_data['hash'] = content_hash

                    articles.append(article_data)

    def _scrape_google_article(self, url: str) -> Optional[Dict]:
        """Scrape individual Google Research article"""
        response = self._make_request(url)
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title with multiple fallbacks
        title = self._extract_title(soup)
        if not title:
            return None

        # Extract content
        content = self._extract_content(soup)

        # Extract date
        date = self._extract_date(soup)

        # Extract research areas/tags
        tags = self._extract_research_tags(soup)

        # Generate content hash
        content_hash = hashlib.md5(f"{title}{content}".encode()).hexdigest()

        return {
            'title': title.strip(),
            'content': self._clean_content(content),
            'url': url,
            'date': date,
            'tags': tags,
            'hash': content_hash,
            'source': 'research.google'
        }

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title with Google-specific selectors"""
        title_selectors = [
            'h1',
            '.blog-post-title',
            '.post-title',
            '.article-title',
            'title'
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 5:  # Reasonable title length
                    return title

        return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content"""
        content_selectors = [
            'article',
            '.blog-post-content',
            '.post-content',
            '.article-content',
            '.content',
            'main'
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove navigation and other non-content elements
                for unwanted in element.select('nav, .nav, .navigation, .sidebar, .related'):
                    unwanted.decompose()

                content = element.get_text()
                if content and len(content) > 100:
                    return content

        # Fallback to meta description
        meta_desc = soup.select_one('meta[name="description"]')
        if meta_desc:
            return meta_desc.get('content', '')

        return ""

    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publication date"""
        date_selectors = [
            'time[datetime]',
            '.published',
            '.blog-post-date',
            '.post-date',
            '.date'
        ]

        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                # Try datetime attribute first
                datetime_attr = element.get('datetime')
                if datetime_attr:
                    return datetime_attr

                # Fall back to text content
                date_text = element.get_text().strip()
                if date_text:
                    return date_text

        return str(datetime.now())

    def _extract_research_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract research area tags"""
        tags = []

        tag_selectors = [
            '.research-areas',
            '.tags',
            '.categories',
            '.topics',
            '[class*="tag"]'
        ]

        for selector in tag_selectors:
            elements = soup.select(selector)
            for element in elements:
                tag_text = element.get_text().strip()
                if tag_text and '·' in tag_text:
                    # Google often separates tags with ·
                    tags.extend([tag.strip() for tag in tag_text.split('·')])
                elif tag_text:
                    tags.append(tag_text)

        return list(set(tags))  # Remove duplicates

    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid Google Research article"""
        if not url or '/blog/' not in url:
            return False

        # Skip pagination and category pages
        skip_patterns = [
            '?page=',
            '/blog/?',
            '/blog/category/',
            '/blog/tag/',
            '/blog/author/'
        ]

        return not any(pattern in url for pattern in skip_patterns)

    def get_latest_articles(self, max_articles: int = 20) -> List[Dict]:
        """
        Main method to get latest Google Research articles
        """
        self.logger.info("Starting Google Research blog scraping")

        try:
            # First try RSS feed
            rss_articles = self.scrape_rss_feed("https://research.google/blog/rss/")

            if rss_articles:
                self.logger.info(f"Got {len(rss_articles)} articles from RSS")
                return rss_articles[:max_articles]

            # Fallback to web scraping
            self.logger.info("RSS failed, falling back to web scraping")
            articles = self.extract_google_articles(max_pages=2)

            return articles[:max_articles]

        except Exception as e:
            self.logger.error(f"Error scraping Google Research blog: {e}")
            return []