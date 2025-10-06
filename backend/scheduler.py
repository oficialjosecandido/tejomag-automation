#!/usr/bin/env python3
"""
TejoMag News Scheduler
Runs the news fetching job every hour without the Flask web server.
Useful for production environments or when running the scheduler separately.
"""

import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import deepl
import time
import schedule
import threading
import atexit
import os

# Initialize DeepL translator
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY', '')
translator = None

if DEEPL_API_KEY:
    try:
        translator = deepl.Translator(DEEPL_API_KEY)
        print("✅ DeepL translator initialized")
    except Exception as e:
        print(f"⚠️  DeepL initialization failed: {e}")
else:
    print("⚠️  No DEEPL_API_KEY found. Translation will not work.")

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            title_pt TEXT NOT NULL,
            content TEXT NOT NULL,
            content_pt TEXT NOT NULL,
            image_url TEXT,
            images TEXT,
            slug TEXT UNIQUE,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            category TEXT DEFAULT 'Geral',
            published_date TEXT,
            scraped_at TEXT,
            UNIQUE(url)
        )
    ''')
    
    # Add slug column to existing tables if it doesn't exist
    try:
        cursor.execute('ALTER TABLE articles ADD COLUMN slug TEXT')
    except:
        pass
    
    # Add images column to existing tables if it doesn't exist
    try:
        cursor.execute('ALTER TABLE articles ADD COLUMN images TEXT')
    except:
        pass
    
    conn.commit()
    conn.close()

def generate_slug(title):
    """Generate a URL-friendly slug from article title"""
    import re
    import unicodedata
    
    # Normalize unicode characters
    slug = unicodedata.normalize('NFKD', title)
    slug = slug.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase and replace spaces with hyphens
    slug = slug.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    
    # Limit length
    slug = slug[:100]
    
    return slug

def scrape_bbc_news():
    """Scrape latest news from BBC"""
    try:
        url = 'https://www.bbc.com/news'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Multiple selectors to find article links
        selectors = [
            'a[data-testid="internal-link"]',
            'a[href*="/news/"]',
            '.gs-c-promo a',
            '.gs-o-media__body a',
            '.nw-c-top-stories__item a',
            'div[data-testid="topic-promos"] a',
            '.ssrcss-1ocoo3l-Wrap a'
        ]
        
        articles = []
        seen_urls = set()
        
        for selector in selectors:
            links = soup.select(selector)
            print(f"Found {len(links)} links with selector: {selector}")
            
            for link in links[:10]:  # Limit to first 10 per selector
                href = link.get('href')
                if not href:
                    continue
                    
                # Make URL absolute
                if href.startswith('/'):
                    href = f'https://www.bbc.com{href}'
                elif not href.startswith('http'):
                    continue
                
                # Skip if we've already seen this URL
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Skip non-news URLs
                if '/news/' not in href or href.endswith('/news'):
                    continue
                
                # Scrape article content
                article = scrape_article_content(href)
                if article:
                    articles.append(article)
                    print(f"Successfully scraped article: {article['title'][:50]}...")
                    
                    if len(articles) >= 3:  # Limit to 3 articles
                        break
            
            if len(articles) >= 3:
                break
        
        print(f"Total articles found: {len(articles)}")
        return articles[:3]  # Return only first 3
        
    except Exception as e:
        print(f"Error scraping BBC news: {e}")
        return []

def scrape_article_content(url):
    """Scrape individual article content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_selectors = [
            'h1[data-testid="headline"]',
            'h1.story-headline',
            'h1.article__title',
            'h1'
        ]
        
        title = None
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                title = title_elem.get_text().strip()
                break
        
        if not title:
            return None
        
        # Extract content
        content_selectors = [
            '[data-testid="story-body"] p',
            '.story-body p',
            '.article__body p',
            'article p'
        ]
        
        content_paragraphs = []
        for selector in content_selectors:
            paragraphs = soup.select(selector)
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 50:  # Filter out short paragraphs
                    content_paragraphs.append(text)
            if content_paragraphs:
                break
        
        if not content_paragraphs:
            return None
        
        # Get more content - increase from 8 to 20 paragraphs for full text
        content = ' '.join(content_paragraphs[:20])
        
        # Extract ALL images
        image_selectors = [
            '[data-testid="story-image"] img',
            '.story-image img',
            '.media img',
            '[data-component="image"] img',
            'article img',
            '.story-body img',
            'img[src*="ichef.bbci.co.uk"]',
            'img[data-src*="ichef.bbci.co.uk"]'
        ]
        
        image_url = None
        all_images = []
        
        for selector in image_selectors:
            imgs = soup.select(selector)
            for img in imgs:
                src = img.get('src') or img.get('data-src')
                if src and 'grey-placeholder' not in src and 'placeholder' not in src.lower():
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = f'https://www.bbc.com{src}'
                    
                    # Avoid duplicates
                    if src not in all_images:
                        all_images.append(src)
                        
                        # Set the first image as the main image
                        if image_url is None:
                            image_url = src
        
        if title and content and len(content) > 100:
            return {
                'title': title,
                'content': content,
                'image_url': image_url,
                'images': all_images,
                'url': url,
                'source': 'BBC'
            }
        
    except Exception as e:
        print(f"Error scraping article {url}: {e}")
    
    return None

def translate_to_portuguese(text, source_lang='en'):
    """Translate text to Portuguese using DeepL"""
    try:
        if not text or len(text.strip()) == 0:
            return text
        
        if not translator:
            print("⚠️  Translator not initialized, returning original text")
            return text
        
        text = text.strip()
        text = ' '.join(text.split())
        
        source_lang_map = {
            'en': 'EN',
            'fr': 'FR'
        }
        source = source_lang_map.get(source_lang.lower(), 'EN')
        
        if len(text) > 5000:
            chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
            translated_chunks = []
            for chunk in chunks:
                try:
                    result = translator.translate_text(
                        chunk, 
                        source_lang=source,
                        target_lang='PT-PT'
                    )
                    translated_chunks.append(result.text)
                    time.sleep(0.3)
                except Exception as chunk_error:
                    print(f"Chunk translation error: {chunk_error}")
                    translated_chunks.append(chunk)
            return ' '.join(translated_chunks)
        else:
            result = translator.translate_text(
                text,
                source_lang=source,
                target_lang='PT-PT'
            )
            return result.text
            
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def detect_category(title, content):
    """Detect article category based on keywords"""
    text = f"{title} {content}".lower()
    
    # Define category keywords - more specific and relevant categories
    categories = {
        'Política': ['politics', 'election', 'president', 'government', 'minister', 'parliament', 'vote', 'democracy', 'party', 'campaign', 'candidate', 'parliament', 'congress', 'senate'],
        'Economia': ['economy', 'economic', 'market', 'stock', 'inflation', 'recession', 'unemployment', 'business', 'financial', 'bank', 'currency', 'trade', 'gdp', 'budget'],
        'Tecnologia': ['technology', 'tech', 'science', 'research', 'digital', 'artificial intelligence', 'computer', 'software', 'innovation', 'data', 'cyber', 'internet', 'mobile', 'app'],
        'Saúde': ['health', 'medical', 'hospital', 'disease', 'vaccine', 'treatment', 'covid', 'pandemic', 'doctor', 'medicine', 'clinical', 'patient', 'healthcare'],
        'Desporto': ['sport', 'sports', 'football', 'soccer', 'olympics', 'competition', 'athlete', 'team', 'championship', 'tournament', 'match', 'game', 'player'],
        'Cultura': ['culture', 'art', 'music', 'film', 'movie', 'book', 'theatre', 'festival', 'exhibition', 'entertainment', 'celebrity', 'actor', 'artist'],
        'Guerra e Conflitos': ['war', 'conflict', 'military', 'army', 'navy', 'air force', 'soldier', 'battle', 'attack', 'defense', 'peace', 'ceasefire', 'treaty', 'nato'],
        'Ambiente': ['climate', 'environment', 'global warming', 'pollution', 'sustainability', 'energy', 'nature', 'green', 'carbon', 'emission', 'renewable', 'ecosystem'],
        'Direitos Humanos': ['human rights', 'justice', 'court', 'law', 'legal', 'trial', 'judge', 'crime', 'police', 'prison', 'freedom', 'equality', 'discrimination'],
        'Ciência': ['science', 'research', 'study', 'discovery', 'experiment', 'scientist', 'laboratory', 'space', 'earth', 'universe', 'physics', 'chemistry', 'biology']
    }
    
    # Count keyword matches for each category
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            category_scores[category] = score
    
    # Return category with highest score, or 'Geral' if no matches
    if category_scores:
        return max(category_scores, key=category_scores.get)
    return 'Geral'

def run_news_job():
    """Background job to fetch and save latest news"""
    try:
        print(f"\n🔄 Running scheduled news job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Scrape BBC news
        articles = scrape_bbc_news()
        
        if not articles:
            print("❌ No articles found in scheduled job")
            return
        
        print(f"📰 Found {len(articles)} articles")
        
        # Process and save articles
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        processed_count = 0
        for article in articles:
            # Check if article already exists
            cursor.execute('SELECT id FROM articles WHERE url = ?', (article['url'],))
            existing = cursor.fetchone()
            
            if not existing:
                # Determine source language for better translation
                source_lang = 'fr' if article['source'] == 'Le Monde' else 'en'
                
                # Translate and store new article
                title_pt = translate_to_portuguese(article['title'], source_lang)
                content_pt = translate_to_portuguese(article['content'], source_lang)
                
                # Detect category
                category = detect_category(article['title'], article['content'])
                
                # Generate slug from Portuguese title (better for SEO)
                slug = generate_slug(title_pt)
                
                # Ensure slug is unique
                counter = 1
                original_slug = slug
                while True:
                    cursor.execute('SELECT id FROM articles WHERE slug = ?', (slug,))
                    if not cursor.fetchone():
                        break
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                
                # Convert images list to JSON
                import json
                images_json = json.dumps(article.get('images', []))
                
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO articles (title, title_pt, content, content_pt, image_url, images, slug, url, source, category, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (article['title'], title_pt, article['content'], content_pt, 
                      article.get('image_url'), images_json, slug, article['url'], article['source'], category, now))
                
                processed_count += 1
                print(f"✅ Added: {article['title'][:50]}... (slug: {slug})")
            else:
                print(f"⏭️  Skipped (already exists): {article['title'][:50]}...")
        
        conn.commit()
        conn.close()
        
        print(f"🎉 Scheduled job completed: {processed_count} new articles added")
        
    except Exception as e:
        print(f"❌ Error in scheduled job: {e}")

def run_scheduler():
    """Run the scheduler in a separate thread"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def setup_scheduler():
    """Setup the scheduled jobs"""
    # Schedule news job to run every hour
    schedule.every().hour.do(run_news_job)
    
    # Also run immediately on startup
    print("🚀 Running initial news fetch...")
    run_news_job()
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("⏰ Scheduler started - news will be fetched every hour")

def main():
    """Main function"""
    print("🌍 TejoMag News Scheduler")
    print("=========================")
    print("This scheduler runs independently to fetch news every hour.")
    print("Press Ctrl+C to stop.")
    print()
    
    # Initialize database
    init_db()
    
    # Setup and start scheduler
    setup_scheduler()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down TejoMag Scheduler...")
        print("Goodbye! 👋")

if __name__ == '__main__':
    main()
