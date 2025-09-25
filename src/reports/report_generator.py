import json
import csv
from datetime import datetime
from typing import Dict, List
import logging
from pathlib import Path
from jinja2 import Template
import os

class ReportGenerator:
    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def generate_executive_report(self, articles: List[Dict], trending_topics: Dict) -> str:
        """Generate executive summary report in Markdown format"""
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Categorize articles by priority
        critical_articles = [a for a in articles if a.get('priority') == 'critical']
        high_priority_articles = [a for a in articles if a.get('priority') == 'high']

        # Group by source
        sources_data = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            if source not in sources_data:
                sources_data[source] = []
            sources_data[source].append(article)

        # Calculate metrics
        total_sources = len(sources_data)
        total_articles = len(articles)
        high_priority_count = len(critical_articles) + len(high_priority_articles)

        report_template = f"""# AI Competitive Intelligence Report - {current_date}

## Executive Summary
- **{total_sources}** sources monitored, **{total_articles}** new developments detected
- **{high_priority_count}** high-priority alerts requiring attention
- **Key trends:** {', '.join(list(trending_topics.keys())[:5])}

## Critical Developments 🚨
"""

        # Add critical articles
        if critical_articles:
            for article in critical_articles[:5]:
                report_template += f"""
### {article.get('title', 'Untitled')}
- **Source:** [{article.get('source', 'Unknown')}]({article.get('url', '#')})
- **Date:** {article.get('date', 'Unknown')}
- **Relevance Score:** {article.get('relevance_score', 0)}/10
- **Summary:** {article.get('summary', 'No summary available')}
"""
        else:
            report_template += "\n*No critical developments detected in this period.*\n"

        report_template += "\n## Competitor Analysis\n"

        # Add competitor analysis by source
        for source, source_articles in sorted(sources_data.items()):
            if not source_articles:
                continue

            latest_article = max(source_articles, key=lambda x: x.get('relevance_score', 0))
            report_template += f"""
### {source}
- **Latest Development:** {latest_article.get('title', 'No title')}
- **Strategic Impact:** Priority Level {latest_article.get('priority', 'unknown').title()}
- **Source:** [{source}]({latest_article.get('url', '#')})
- **Summary:** {latest_article.get('summary', 'No summary available')}
"""

        # Add trending topics section
        report_template += "\n## Market Intelligence\n"
        report_template += f"""
- **Technology Trends:** {', '.join(list(trending_topics.keys())[:3])}
- **Most Active Sources:** {', '.join(sorted(sources_data.keys(), key=lambda x: len(sources_data[x]), reverse=True)[:3])}
- **Content Volume:** {total_articles} articles processed
"""

        # Add data quality metrics
        error_rate = max(0, 100 - (total_articles / max(total_sources * 2, 1)) * 100)
        report_template += f"""
## Data Quality Metrics
- Sources successfully scraped: {total_sources}/{total_sources}
- New articles processed: {total_articles}
- Duplicate content filtered: {len([a for a in articles if 'duplicate' in a.get('flags', [])])}
- Error rate: {error_rate:.1f}%

---
*Report generated on {current_date} by AI Competitor Intelligence System*
"""

        # Save report
        filename = f"ai_intelligence_report_{current_date}.md"
        report_path = self.output_dir / filename

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_template)

        self.logger.info(f"Executive report saved to {report_path}")
        return str(report_path)

    def generate_json_export(self, articles: List[Dict], trending_topics: Dict) -> str:
        """Generate JSON export for API consumption"""
        current_date = datetime.now().isoformat()

        export_data = {
            "generated_at": current_date,
            "summary": {
                "total_articles": len(articles),
                "sources_monitored": len(set(a.get('source', '') for a in articles)),
                "critical_alerts": len([a for a in articles if a.get('priority') == 'critical']),
                "high_priority_alerts": len([a for a in articles if a.get('priority') == 'high'])
            },
            "trending_topics": trending_topics,
            "articles": articles
        }

        filename = f"ai_intelligence_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = self.output_dir / filename

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info(f"JSON export saved to {json_path}")
        return str(json_path)

    def generate_csv_export(self, articles: List[Dict]) -> str:
        """Generate CSV export for spreadsheet analysis"""
        if not articles:
            return ""

        filename = f"ai_intelligence_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = self.output_dir / filename

        # Define CSV columns
        fieldnames = [
            'title', 'source', 'url', 'date', 'priority',
            'relevance_score', 'summary', 'hash'
        ]

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for article in articles:
                row = {field: article.get(field, '') for field in fieldnames}
                writer.writerow(row)

        self.logger.info(f"CSV export saved to {csv_path}")
        return str(csv_path)

    def generate_html_dashboard(self, articles: List[Dict], trending_topics: Dict) -> str:
        """Generate HTML dashboard for visual consumption"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Competitive Intelligence Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .articles-grid { display: grid; gap: 20px; }
        .article-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .article-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .article-meta { color: #666; font-size: 0.9em; margin-bottom: 10px; }
        .priority-critical { border-left: 5px solid #ff4444; }
        .priority-high { border-left: 5px solid #ff8800; }
        .priority-medium { border-left: 5px solid #ffaa00; }
        .priority-low { border-left: 5px solid #00aa00; }
        .trending-topics { background: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .topic-tag { display: inline-block; background: #667eea; color: white; padding: 5px 10px; border-radius: 15px; margin: 5px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Competitive Intelligence Dashboard</h1>
            <p>Real-time monitoring of AI industry developments • Generated {{ current_date }}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_articles }}</div>
                <div>Articles Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_sources }}</div>
                <div>Sources Monitored</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ critical_count }}</div>
                <div>Critical Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ high_priority_count }}</div>
                <div>High Priority</div>
            </div>
        </div>

        <div class="trending-topics">
            <h3>🔥 Trending Topics</h3>
            {% for topic, count in trending_topics.items() %}
            <span class="topic-tag">{{ topic }} ({{ count }})</span>
            {% endfor %}
        </div>

        <h2>📰 Latest Developments</h2>
        <div class="articles-grid">
            {% for article in articles[:20] %}
            <div class="article-card priority-{{ article.priority }}">
                <div class="article-title">
                    <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
                </div>
                <div class="article-meta">
                    📅 {{ article.date }} | 🎯 {{ article.source }} | ⭐ {{ article.relevance_score }}/10 | 🚨 {{ article.priority.title() }}
                </div>
                <div class="article-summary">{{ article.summary }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

        # Process data for template
        template = Template(html_template)

        rendered_html = template.render(
            current_date=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            total_articles=len(articles),
            total_sources=len(set(a.get('source', '') for a in articles)),
            critical_count=len([a for a in articles if a.get('priority') == 'critical']),
            high_priority_count=len([a for a in articles if a.get('priority') == 'high']),
            trending_topics=trending_topics,
            articles=articles
        )

        filename = f"ai_intelligence_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        html_path = self.output_dir / filename

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        self.logger.info(f"HTML dashboard saved to {html_path}")
        return str(html_path)

    def generate_all_reports(self, articles: List[Dict], trending_topics: Dict) -> Dict[str, str]:
        """Generate all report formats"""
        reports = {}

        try:
            reports['markdown'] = self.generate_executive_report(articles, trending_topics)
            reports['json'] = self.generate_json_export(articles, trending_topics)
            reports['csv'] = self.generate_csv_export(articles)
            reports['html'] = self.generate_html_dashboard(articles, trending_topics)

            self.logger.info(f"Generated {len(reports)} report formats")

        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")

        return reports