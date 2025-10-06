from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import sqlite3
import os
from datetime import datetime
import time
import schedule
import threading
import atexit

app = Flask(__name__)
CORS(app)

# Initialize translator
translator = Translator()

# Database setup
def init_db():
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
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            category TEXT DEFAULT 'Geral',
            published_date TEXT,
            scraped_at TEXT,
            UNIQUE(url)
        )
    ''')
    conn.commit()
    conn.close()

def scrape_bbc_news():
    """Scrape the latest 3 news articles from BBC"""
    try:
        # BBC News homepage
        url = "https://www.bbc.com/news"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find news articles - BBC uses various selectors
        articles = []
        
        # Try multiple selectors for BBC articles
        selectors = [
            'a[data-testid="internal-link"]',
            'a[href*="/news/"]',
            '.gs-c-promo a',
            '.gs-o-media__body a',
            '.nw-c-top-stories__item a',
            'div[data-testid="topic-promos"] a',
            '.ssrcss-1ocoo3l-Wrap a'
        ]
        
        found_links = set()  # To avoid duplicates
        
        for selector in selectors:
            links = soup.select(selector)
            print(f"Found {len(links)} links with selector: {selector}")
            
            for link in links:
                href = link.get('href')
                if href and '/news/' in href and href not in found_links:
                    if not href.startswith('http'):
                        href = 'https://www.bbc.com' + href
                    
                    found_links.add(href)
                    
                    # Get article content
                    print(f"Scraping article: {href}")
                    article_content = scrape_article_content(href)
                    if article_content:
                        articles.append(article_content)
                        print(f"Successfully scraped article: {article_content['title'][:50]}...")
                        if len(articles) >= 3:
                            break
            
            if len(articles) >= 3:
                break
        
        print(f"Total articles found: {len(articles)}")
        return articles[:3]
        
    except Exception as e:
        print(f"Error scraping BBC: {e}")
        import traceback
        traceback.print_exc()
        return []

def scrape_article_content(url):
    """Scrape individual article content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title with multiple selectors
        title_selectors = [
            'h1[data-testid="headline"]',
            'h1[data-testid="story-headline"]',
            '.story-headline',
            'h1.story-headline',
            'h1[class*="headline"]',
            'h1[class*="Story"]',
            '.ssrcss-1f3bvyz-Headline',
            'h1'
        ]
        
        title = None
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title and len(title) > 10:  # Ensure it's a meaningful title
                    break
        
        # Extract content with multiple selectors
        content_selectors = [
            '[data-testid="story-body"] p',
            '[data-testid="story-body"] div',
            '.story-body p',
            '.story-body__inner p',
            '[data-component="text-block"] p',
            '.ssrcss-11r1m41-RichTextComponentWrapper p',
            'article p',
            '.content p'
        ]
        
        content_parts = []
        for selector in content_selectors:
            content_elems = soup.select(selector)
            for elem in content_elems:
                text = elem.get_text().strip()
                if text and len(text) > 30:  # Filter out short paragraphs
                    content_parts.append(text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_content = []
        for part in content_parts:
            if part not in seen:
                seen.add(part)
                unique_content.append(part)
        
        content = ' '.join(unique_content[:8])  # Limit to first 8 paragraphs
        
        # Extract article image
        image_url = None
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
        
        # Try to find the main article image (not placeholder)
        for selector in image_selectors:
            img_elems = soup.select(selector)
            for img_elem in img_elems:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src and 'placeholder' not in src.lower() and 'grey-placeholder' not in src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.bbc.com' + src
                    image_url = src
                    break
            if image_url:
                break
        
        if title and content and len(content) > 100:
            return {
                'title': title,
                'content': content,
                'image_url': image_url,
                'url': url,
                'source': 'BBC'
            }
        
    except Exception as e:
        print(f"Error scraping article {url}: {e}")
    
    return None

def translate_to_portuguese(text):
    """Translate text to Portuguese with improved quality"""
    try:
        if not text or len(text.strip()) == 0:
            return text
        
        # Clean and prepare text for translation
        text = text.strip()
        
        # Split long text into chunks for translation
        if len(text) > 4500:  # Reduced chunk size for better quality
            chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
            translated_chunks = []
            for chunk in chunks:
                try:
                    # Use Brazilian Portuguese for more natural translations
                    result = translator.translate(chunk, dest='pt', src='en')
                    translated_chunks.append(result.text)
                    time.sleep(0.3)  # Reduced delay
                except Exception as chunk_error:
                    print(f"Chunk translation error: {chunk_error}")
                    translated_chunks.append(chunk)
            return ' '.join(translated_chunks)
        else:
            # Use Brazilian Portuguese for more natural translations
            result = translator.translate(text, dest='pt', src='en')
            return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def detect_category(title, content):
    """Detect article category based on keywords - focused on specific topics"""
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

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get latest news articles"""
    try:
        # Scrape BBC news
        articles = scrape_bbc_news()
        
        if not articles:
            return jsonify({'error': 'No articles found'}), 500
        
        # Process and store articles
        processed_articles = []
        
        for article in articles:
            # Check if article already exists
            conn = sqlite3.connect('news.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM articles WHERE url = ?', (article['url'],))
            existing = cursor.fetchone()
            
            if existing:
                # Return existing article - handle schema versions
                if len(existing) >= 10:  # New schema with category
                    article_data = {
                        'id': existing[0],
                        'title': existing[1],
                        'title_pt': existing[2],
                        'content': existing[3],
                        'content_pt': existing[4],
                        'image_url': existing[5],
                        'url': existing[6],
                        'source': existing[7],
                        'category': existing[8],
                        'published_date': existing[9],
                        'scraped_at': existing[10]
                    }
                elif len(existing) >= 9:  # Schema with image_url but no category
                    article_data = {
                        'id': existing[0],
                        'title': existing[1],
                        'title_pt': existing[2],
                        'content': existing[3],
                        'content_pt': existing[4],
                        'image_url': existing[5],
                        'url': existing[6],
                        'source': existing[7],
                        'category': 'Geral',  # Default category
                        'published_date': existing[8],
                        'scraped_at': existing[9]
                    }
                else:  # Old schema without image_url and category
                    article_data = {
                        'id': existing[0],
                        'title': existing[1],
                        'title_pt': existing[2],
                        'content': existing[3],
                        'content_pt': existing[4],
                        'image_url': None,
                        'url': existing[5],
                        'source': existing[6],
                        'category': 'Geral',  # Default category
                        'published_date': existing[7],
                        'scraped_at': existing[8]
                    }
                
                processed_articles.append(article_data)
            else:
                # Translate and store new article
                title_pt = translate_to_portuguese(article['title'])
                content_pt = translate_to_portuguese(article['content'])
                
                # Detect category
                category = detect_category(article['title'], article['content'])
                
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO articles (title, title_pt, content, content_pt, image_url, url, source, category, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (article['title'], title_pt, article['content'], content_pt, 
                      article.get('image_url'), article['url'], article['source'], category, now))
                
                conn.commit()
                article_id = cursor.lastrowid
                
                processed_articles.append({
                    'id': article_id,
                    'title': article['title'],
                    'title_pt': title_pt,
                    'content': article['content'],
                    'content_pt': content_pt,
                    'image_url': article.get('image_url'),
                    'url': article['url'],
                    'source': article['source'],
                    'category': category,
                    'published_date': None,
                    'scraped_at': now
                })
            
            conn.close()
        
        return jsonify({
            'articles': processed_articles,
            'count': len(processed_articles)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'News API is running'})

@app.route('/api/news/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    categories = ['Política', 'Economia', 'Tecnologia', 'Saúde', 'Desporto', 'Cultura', 'Guerra e Conflitos', 'Ambiente', 'Direitos Humanos', 'Ciência', 'Geral']
    return jsonify({'categories': categories})

@app.route('/api/news/category/<category>', methods=['GET'])
def get_news_by_category(category):
    """Get news articles by category"""
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        # Get articles from the specified category
        cursor.execute('''
            SELECT id, title, title_pt, content, content_pt, image_url, url, source, category, published_date, scraped_at
            FROM articles 
            WHERE category = ? 
            ORDER BY scraped_at DESC
        ''', (category,))
        
        articles = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        article_list = []
        for article in articles:
            article_list.append({
                'id': article[0],
                'title': article[1],
                'title_pt': article[2],
                'content': article[3],
                'content_pt': article[4],
                'image_url': article[5],
                'url': article[6],
                'source': article[7],
                'category': article[8],
                'published_date': article[9],
                'scraped_at': article[10]
            })
        
        return jsonify({
            'articles': article_list,
            'category': category,
            'count': len(article_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/refresh', methods=['POST'])
def refresh_news():
    """Manually trigger news refresh"""
    try:
        print("🔄 Manual news refresh requested")
        run_news_job()
        return jsonify({
            'message': 'News refresh completed',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get scheduler status and next run time"""
    try:
        jobs = schedule.get_jobs()
        job_info = []
        for job in jobs:
            job_info.append({
                'job': str(job.job_func),
                'next_run': job.next_run.isoformat() if job.next_run else None,
                'interval': str(job.interval)
            })
        
        return jsonify({
            'status': 'running',
            'jobs': job_info,
            'total_jobs': len(jobs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
                # Translate and store new article
                title_pt = translate_to_portuguese(article['title'])
                content_pt = translate_to_portuguese(article['content'])
                
                # Detect category
                category = detect_category(article['title'], article['content'])
                
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO articles (title, title_pt, content, content_pt, image_url, url, source, category, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (article['title'], title_pt, article['content'], content_pt, 
                      article.get('image_url'), article['url'], article['source'], category, now))
                
                processed_count += 1
                print(f"✅ Added: {article['title'][:50]}...")
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

if __name__ == '__main__':
    init_db()
    print("Starting News Translation API...")
    print("API will be available at: http://localhost:5001")
    print("Endpoints:")
    print("  GET /api/health - Health check")
    print("  GET /api/news - Get latest translated news")
    print("  GET /api/news/categories - Get available categories")
    print("  GET /api/news/category/<category> - Get news by category")
    print("  POST /api/news/refresh - Manually refresh news")
    print("  GET /api/scheduler/status - Check scheduler status")
    print()
    
    # Setup the scheduler for automatic news fetching
    setup_scheduler()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down TejoMag...")
        print("Goodbye! 👋")
