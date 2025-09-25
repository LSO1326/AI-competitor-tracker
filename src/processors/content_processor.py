import re
from typing import Dict, List, Set
from datetime import datetime, timedelta
import logging
import hashlib
from collections import defaultdict

class ContentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seen_hashes = set()

        # AI-related keywords for relevance filtering
        self.ai_keywords = {
            'high_priority': [
                'artificial intelligence', 'machine learning', 'deep learning',
                'neural network', 'large language model', 'llm', 'gpt',
                'transformer', 'generative ai', 'chatbot', 'openai',
                'anthropic', 'google ai', 'microsoft ai', 'meta ai',
                'deepmind', 'hugging face', 'stability ai'
            ],
            'medium_priority': [
                'automation', 'computer vision', 'natural language',
                'nlp', 'ai model', 'algorithm', 'data science',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn',
                'ai startup', 'ai funding', 'ai ethics', 'ai regulation'
            ],
            'tech_context': [
                'tech', 'technology', 'software', 'startup',
                'funding', 'vc', 'venture capital', 'investment',
                'api', 'platform', 'cloud', 'saas'
            ]
        }

    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process and filter articles for relevance and quality"""
        processed_articles = []

        for article in articles:
            if self._is_duplicate(article):
                continue

            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(article)

            if relevance_score >= 2:  # Minimum threshold for AI relevance
                article['relevance_score'] = relevance_score
                article['processed_date'] = datetime.now().isoformat()
                article['summary'] = self._generate_summary(article.get('content', ''))
                article['priority'] = self._determine_priority(article, relevance_score)

                processed_articles.append(article)
                self.seen_hashes.add(article['hash'])

        # Sort by relevance score and date
        processed_articles.sort(
            key=lambda x: (x['relevance_score'], x.get('date', '')),
            reverse=True
        )

        return processed_articles

    def _is_duplicate(self, article: Dict) -> bool:
        """Check if article is duplicate based on content hash"""
        article_hash = article.get('hash')
        if not article_hash:
            # Generate hash if not present
            content = f"{article.get('title', '')}{article.get('content', '')}"
            article_hash = hashlib.md5(content.encode()).hexdigest()
            article['hash'] = article_hash

        return article_hash in self.seen_hashes

    def _calculate_relevance_score(self, article: Dict) -> int:
        """Calculate relevance score based on AI-related keywords"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        combined_text = f"{title} {content}"

        score = 0

        # High priority keywords (3 points each)
        for keyword in self.ai_keywords['high_priority']:
            if keyword in combined_text:
                score += 3
                # Bonus for title mentions
                if keyword in title:
                    score += 2

        # Medium priority keywords (2 points each)
        for keyword in self.ai_keywords['medium_priority']:
            if keyword in combined_text:
                score += 2
                if keyword in title:
                    score += 1

        # Tech context keywords (1 point each, max 3)
        tech_score = 0
        for keyword in self.ai_keywords['tech_context']:
            if keyword in combined_text and tech_score < 3:
                tech_score += 1

        score += tech_score

        return score

    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary of the article content"""
        if not content:
            return ""

        # Clean the content
        content = re.sub(r'\s+', ' ', content).strip()

        # Extract first 2-3 sentences or 200 characters, whichever is shorter
        sentences = re.split(r'[.!?]+', content)

        summary = ""
        char_count = 0
        sentence_count = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if char_count + len(sentence) > 200 or sentence_count >= 3:
                break

            summary += sentence + ". "
            char_count += len(sentence)
            sentence_count += 1

        return summary.strip()

    def _determine_priority(self, article: Dict, relevance_score: int) -> str:
        """Determine article priority based on relevance score and content"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        combined_text = f"{title} {content}"

        # Critical indicators
        critical_terms = [
            'breakthrough', 'major announcement', 'new model',
            'gpt-5', 'gpt-4', 'claude', 'gemini', 'llama',
            'acquisition', 'merger', 'funding round', 'ipo',
            'partnership', 'collaboration', 'investment'
        ]

        # High priority indicators
        high_priority_terms = [
            'launch', 'release', 'unveil', 'introduce',
            'upgrade', 'improvement', 'feature', 'update',
            'research', 'study', 'paper', 'findings'
        ]

        if relevance_score >= 10:
            return 'critical'

        if any(term in combined_text for term in critical_terms):
            return 'critical'

        if relevance_score >= 6 or any(term in combined_text for term in high_priority_terms):
            return 'high'

        if relevance_score >= 4:
            return 'medium'

        return 'low'

    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on similarity"""
        unique_articles = []
        seen_titles = set()

        for article in articles:
            title = article.get('title', '').lower()
            # Simple deduplication based on title similarity
            title_words = set(re.findall(r'\b\w+\b', title))

            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(re.findall(r'\b\w+\b', seen_title))
                # If 80% of words overlap, consider it duplicate
                if len(title_words & seen_words) / max(len(title_words), 1) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(title)

        return unique_articles

    def filter_by_date(self, articles: List[Dict], days_back: int = 7) -> List[Dict]:
        """Filter articles to only include recent ones"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_articles = []

        for article in articles:
            article_date_str = article.get('date', '')
            try:
                # Try to parse various date formats
                for date_format in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%a, %d %b %Y %H:%M:%S %Z']:
                    try:
                        article_date = datetime.strptime(article_date_str.split('T')[0], date_format.split('T')[0])
                        if article_date >= cutoff_date:
                            filtered_articles.append(article)
                        break
                    except ValueError:
                        continue
                else:
                    # If date parsing fails, include the article anyway
                    filtered_articles.append(article)
            except Exception as e:
                self.logger.warning(f"Date parsing failed for article: {e}")
                filtered_articles.append(article)

        return filtered_articles

    def get_trending_topics(self, articles: List[Dict]) -> Dict[str, int]:
        """Extract trending topics from articles"""
        topic_counts = defaultdict(int)

        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            combined_text = f"{title} {content}"

            # Count occurrences of key terms
            for keyword_list in self.ai_keywords.values():
                for keyword in keyword_list:
                    if keyword in combined_text:
                        topic_counts[keyword] += 1

        # Return top 10 trending topics
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10])