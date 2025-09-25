#!/usr/bin/env python3
"""
AI Competitor Intelligence System
Professional-grade web scraper for monitoring AI industry developments
"""

import yaml
import logging
import sys
from pathlib import Path
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from scrapers.web_scraper import WebScraper
from processors.content_processor import ContentProcessor
from reports.report_generator import ReportGenerator

class AICompetitorIntelligence:
    def __init__(self, config_path: str = "config/sources.yaml"):
        self.config_path = Path(config_path)
        self.setup_logging()
        self.load_configuration()

        # Initialize components
        self.scraper = WebScraper()
        self.processor = ContentProcessor()
        self.report_generator = ReportGenerator()

        self.logger = logging.getLogger(__name__)

    def setup_logging(self):
        """Configure logging for the application"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def load_configuration(self):
        """Load source configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ Loaded configuration with {len(self._get_all_sources())} sources")
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML configuration: {e}")
            sys.exit(1)

    def _get_all_sources(self) -> List[Dict]:
        """Get all sources from all tiers"""
        all_sources = []
        for tier_name, sources in self.config.get('sources', {}).items():
            for source in sources:
                source['tier'] = tier_name
                all_sources.append(source)
        return all_sources

    def scrape_source(self, source: Dict) -> Tuple[str, List[Dict]]:
        """Scrape a single source and return results"""
        source_name = source.get('name', 'Unknown')
        source_url = source.get('url', '')
        rss_url = source.get('rss_url')
        selectors = source.get('selectors', {})
        rate_limit = source.get('rate_limit', 2)

        print(f"🔍 Scraping {source_name}...")

        try:
            # Set rate limit for this source
            self.scraper.rate_limit = rate_limit

            # Try scraping the source
            articles = self.scraper.extract_articles(source_url, selectors, rss_url)

            if articles:
                print(f"✅ {source_name}: Found {len(articles)} articles")
            else:
                print(f"⚠️  {source_name}: No articles found")

            return source_name, articles

        except Exception as e:
            print(f"❌ {source_name}: Error - {str(e)}")
            self.logger.error(f"Error scraping {source_name}: {e}")
            return source_name, []

    def execute_intelligence_gathering(self, max_workers: int = 3) -> Dict:
        """Execute the complete intelligence gathering process"""
        print(f"\n🤖 AI Competitor Intelligence System Starting...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        start_time = time.time()
        all_articles = []
        sources_data = {}

        # Get all sources
        all_sources = self._get_all_sources()

        # Scrape sources concurrently
        print(f"\n📡 Scraping {len(all_sources)} sources with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(self.scrape_source, source): source
                for source in all_sources
            }

            for future in as_completed(future_to_source):
                source_name, articles = future.result()
                sources_data[source_name] = articles
                all_articles.extend(articles)

        print(f"\n📊 Scraping completed in {time.time() - start_time:.2f} seconds")
        print(f"📰 Total articles collected: {len(all_articles)}")

        if not all_articles:
            print("⚠️  No articles found. Check source configurations and network connectivity.")
            return {"articles": [], "reports": {}, "trending_topics": {}}

        # Process articles
        print("\n🔄 Processing articles...")
        processed_articles = self.processor.process_articles(all_articles)
        processed_articles = self.processor.filter_by_date(processed_articles, days_back=7)
        processed_articles = self.processor.deduplicate_articles(processed_articles)

        # Get trending topics
        trending_topics = self.processor.get_trending_topics(processed_articles)

        print(f"✅ Processing completed:")
        print(f"   📝 {len(processed_articles)} relevant articles after filtering")
        print(f"   🔥 {len(trending_topics)} trending topics identified")

        # Generate reports
        print("\n📋 Generating reports...")
        reports = self.report_generator.generate_all_reports(processed_articles, trending_topics)

        print("✅ Reports generated:")
        for report_type, file_path in reports.items():
            if file_path:
                print(f"   📄 {report_type.upper()}: {file_path}")

        # Print summary statistics
        priority_counts = {}
        for article in processed_articles:
            priority = article.get('priority', 'unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        print(f"\n📈 Intelligence Summary:")
        print(f"   🚨 Critical: {priority_counts.get('critical', 0)}")
        print(f"   ⚡ High: {priority_counts.get('high', 0)}")
        print(f"   📌 Medium: {priority_counts.get('medium', 0)}")
        print(f"   📋 Low: {priority_counts.get('low', 0)}")

        if trending_topics:
            print(f"\n🔥 Top Trending Topics:")
            for topic, count in list(trending_topics.items())[:5]:
                print(f"   • {topic}: {count} mentions")

        total_time = time.time() - start_time
        print(f"\n⏱️  Total execution time: {total_time:.2f} seconds")
        print("=" * 60)
        print("🎉 Intelligence gathering complete!")

        return {
            "articles": processed_articles,
            "reports": reports,
            "trending_topics": trending_topics,
            "sources_data": sources_data,
            "execution_time": total_time
        }

    def run_health_check(self):
        """Run health check on all configured sources"""
        print("🏥 Running health check on all sources...")

        all_sources = self._get_all_sources()
        healthy_sources = []
        problematic_sources = []

        for source in all_sources[:5]:  # Test first 5 sources
            source_name = source.get('name', 'Unknown')
            source_url = source.get('url', '')

            try:
                response = self.scraper._make_request(source_url)
                if response and response.status_code == 200:
                    print(f"✅ {source_name}: Healthy")
                    healthy_sources.append(source_name)
                else:
                    print(f"⚠️  {source_name}: Problematic (HTTP {response.status_code if response else 'No Response'})")
                    problematic_sources.append(source_name)
            except Exception as e:
                print(f"❌ {source_name}: Error - {str(e)}")
                problematic_sources.append(source_name)

        print(f"\n📊 Health Check Summary:")
        print(f"   ✅ Healthy sources: {len(healthy_sources)}")
        print(f"   ⚠️  Problematic sources: {len(problematic_sources)}")

        return {
            "healthy": healthy_sources,
            "problematic": problematic_sources
        }

def main():
    """Main entry point"""
    try:
        intel_system = AICompetitorIntelligence()

        # Check if health check is requested
        if len(sys.argv) > 1 and sys.argv[1] == "--health-check":
            intel_system.run_health_check()
            return

        # Run intelligence gathering
        results = intel_system.execute_intelligence_gathering()

        # Open HTML dashboard if available
        html_report = results['reports'].get('html')
        if html_report:
            print(f"\n🌐 Opening dashboard: file://{Path(html_report).absolute()}")
            import webbrowser
            webbrowser.open(f"file://{Path(html_report).absolute()}")

    except KeyboardInterrupt:
        print("\n\n🛑 Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()