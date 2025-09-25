## Expert Engineering Brief
  You are an expert software engineer specializing in enterprise-grade web scraping applications. You have built
  dozens of production scraping systems for Fortune 500 companies, handling complex anti-bot protection, dynamic
  content, and large-scale data extraction. You understand the nuances of respectful scraping, legal compliance, and
  building resilient systems that handle failures gracefully.

  ## Project Specification
  Build a professional-grade competitive intelligence system that monitors the AI industry landscape. This system
  will be deployed in a business environment where reliability, data quality, and comprehensive reporting are
  critical for strategic decision-making.

  ## Technical Architecture

  ### Core Scraping Engine
  - **Multi-threaded scraping** with concurrent request handling
  - **Intelligent rate limiting** with per-domain configurations
  - **User-agent rotation** and session management
  - **Retry logic** with exponential backoff (3 attempts per URL)
  - **Content fingerprinting** to avoid processing duplicate content
  - **Respectful crawling** that honors robots.txt and implements delays

  ### Anti-Detection & Resilience Strategy
  **Primary Defense Mechanisms:**
  - Randomized request delays (2-5 seconds between requests)
  - Multiple User-Agent strings from real browsers
  - Session persistence with cookie handling
  - Request header randomization (Accept, Accept-Language, etc.)

  **Fallback Strategies When Blocked:**
  - Switch to RSS feeds when available (OpenAI, Google AI have RSS)
  - Use alternative endpoints (mobile versions, API endpoints)
  - Implement headless browser fallback with Playwright for dynamic content
  - Graceful degradation - skip problematic sources, continue with others

  **Error Recovery Patterns:**
  - HTTP status code handling (404, 403, 429, 500+ responses)
  - Network timeout management with progressive backoff
  - HTML structure change detection with multiple CSS selector fallbacks
  - Content validation to ensure scraped data meets quality standards

  ### Data Processing Pipeline
  **Content Extraction:**
  - Multi-selector CSS targeting (primary, secondary, tertiary selectors)
  - Content sanitization removing ads, navigation, and boilerplate
  - Intelligent date parsing handling multiple date formats
  - Text summarization for lengthy articles (first 200 words + key phrases)

  **Data Quality Assurance:**
  - Duplicate detection using content hashing
  - Relevance filtering using AI/tech keyword matching
  - Content validation ensuring minimum quality thresholds
  - Source attribution and link verification

  ### Professional Reporting System
  **Executive Dashboard Format:**
  ```markdown
  # AI Competitive Intelligence - [Date]
  ## Executive Summary
  - [X] sources monitored, [Y] new developments detected
  - [Z] high-priority alerts requiring immediate attention
  - Key trends: [AI model releases, pricing changes, partnerships]

  ## Critical Developments 🚨
  [Priority-ranked list of most important developments]

  ## Competitor Analysis
  ### [Company Name]
  - **Latest Development:** [Title with date]
  - **Strategic Impact:** [Business implications]
  - **Source:** [Direct link to original content]
  - **Summary:** [2-3 sentence key takeaway]

  ## Market Intelligence
  - **Pricing Movements:** [Comparative analysis]
  - **Technology Trends:** [Common themes across competitors]
  - **Strategic Patterns:** [M&A, partnerships, market positioning]

  ## Data Quality Metrics
  - Sources successfully scraped: X/Y
  - New articles processed: Z
  - Duplicate content filtered: A
  - Error rate: B%

  Multi-Format Output:
  - Markdown reports for human readability and version control
  - JSON data export for integration with business intelligence tools
  - HTML dashboard with interactive charts and filtering
  - CSV export for analysis in Excel/Google Sheets
  - API endpoints for real-time data access

  Target Intelligence Sources

  Tier 1 - Primary Competitors (Critical Monitoring)

  - OpenAI Blog (https://openai.com/blog) + RSS feed
  - Google AI Blog (https://ai.googleblog.com) + Research papers
  - Microsoft AI (https://blogs.microsoft.com/ai/) + Azure updates
  - Anthropic (https://www.anthropic.com/news) + Safety research

  Tier 2 - Market Players (Regular Monitoring)

  - Meta AI (https://ai.meta.com/blog/) + Research releases
  - DeepMind (https://deepmind.com/blog) + Nature publications
  - Hugging Face (https://huggingface.co/blog) + Model releases
  - Cohere, Stability AI, Runway (Product announcements)

  Tier 3 - Industry Intelligence (Weekly Monitoring)

  - TechCrunch AI (https://techcrunch.com/category/artificial-intelligence/)
  - VentureBeat AI (https://venturebeat.com/ai/)
  - The Information (Premium industry coverage)
  - ArXiv AI papers (cs.AI, cs.LG categories)

  Implementation Strategy

  Phase 1: Core Infrastructure (Build First)

  # Professional-grade scraper architecture
  class CompetitorIntelligence:
      def __init__(self):
          self.session_manager = SessionManager()
          self.rate_limiter = RateLimiter()
          self.content_processor = ContentProcessor()
          self.report_generator = ReportGenerator()

      def execute_intelligence_gathering(self):
          # Multi-threaded scraping with error isolation
          # Content processing and deduplication
          # Professional report generation

  Phase 2: Anti-Detection Systems

  - Implement sophisticated request patterns
  - Add browser automation fallbacks
  - Create monitoring for blocked sources
  - Build automatic failover mechanisms

  Phase 3: Intelligence Processing

  - Deploy NLP processing for content categorization
  - Implement trend detection algorithms
  - Add sentiment analysis for market positioning
  - Create competitive comparison matrices

  Professional Deliverables

  Code Architecture

  - Modular design with separation of concerns
  - Configuration-driven behavior via JSON/YAML
  - Comprehensive logging with structured output
  - Unit tests for critical scraping functions
  - Documentation with API references and usage examples

  Monitoring & Alerting

  - Health checks for all monitored sources
  - Performance metrics (success rates, response times)
  - Alert thresholds for critical competitive developments
  - Dashboard visualization of scraping status and data quality

  Business Integration

  - Scheduled execution via cron jobs or cloud schedulers
  - Email notifications for high-priority developments
  - Slack integration for team alerts
  - Export capabilities to existing business intelligence tools

  Success Metrics

  - Reliability: 95%+ uptime across all monitored sources
  - Coverage: Successfully monitor 8+ competitor sources daily
  - Speed: Complete intelligence gathering cycle in under 15 minutes
  - Quality: Zero false positives in high-priority alerts
  - Usability: Reports require minimal manual review before distribution

  Build this system with enterprise-grade reliability, comprehensive error handling, and professional presentation
  suitable for executive consumption. The system should demonstrate advanced web scraping techniques while being
  accessible to developers learning the fundamentals.

When deploying - Do this in a local host env so the user can see the output visually
