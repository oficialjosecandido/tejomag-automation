from flask import Flask, jsonify, request, session
from flask_cors import CORS
from functools import wraps
import hashlib
import requests
from bs4 import BeautifulSoup
import deepl
import psycopg2
from psycopg2 import pool
from psycopg2 import IntegrityError
from contextlib import contextmanager
import os
from datetime import datetime
import time
import schedule
import threading
import atexit
import logging
import json

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'tejomag-secret-key-change-in-production-2024')
CORS(app, origins=[
    'https://tejomag.pt',
    'https://www.tejomag.pt', 
    'https://victorious-hill-04593eb03.2.azurestaticapps.net',
    'http://localhost:3000',
    'http://localhost:3001'
], supports_credentials=True)

# Global flag to track if app has been initialized
_app_initialized = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://tejomagadmin:TejoMag2024!Secure@tejomag-db.postgres.database.azure.com/tejomag_news?sslmode=require')

# Connection pool for PostgreSQL
db_pool = None

def get_db_connection():
    """Get a connection from the pool"""
    global db_pool
    if db_pool is None:
        try:
            db_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,  # minconn, maxconn
                DATABASE_URL
            )
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to create connection pool: {e}")
            # Fallback to direct connection
            return psycopg2.connect(DATABASE_URL)
    
    try:
        return db_pool.getconn()
    except psycopg2.pool.PoolError:
        logger.warning("⚠️ Connection pool exhausted, creating direct connection")
        return psycopg2.connect(DATABASE_URL)

def release_db_connection(conn):
    """Release a connection back to the pool"""
    if conn and db_pool:
        try:
            db_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error releasing connection: {e}")
            try:
                conn.close()
            except:
                pass
    elif conn:
        try:
            conn.close()
        except:
            pass

@contextmanager
def get_db_cursor():
    """Context manager for database connections"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

# Initialize DeepL translators (primary + fallback)
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY', '')
DEEPL_API_KEY_2 = os.getenv('DEEPL_API_KEY_2', '')
translator = None  # Primary translator
translator_backup = None  # Secondary translator

if DEEPL_API_KEY:
    try:
        translator = deepl.Translator(DEEPL_API_KEY)
        logger.info("✅ DeepL primary translator initialized")
    except Exception as e:
        logger.error(f"DeepL primary initialization failed: {e}")
else:
    logger.warning("⚠️  No DEEPL_API_KEY found. Primary translation disabled.")

if DEEPL_API_KEY_2:
    try:
        translator_backup = deepl.Translator(DEEPL_API_KEY_2)
        logger.info("✅ DeepL backup translator initialized")
    except Exception as e:
        logger.error(f"DeepL backup initialization failed: {e}")
elif not translator:
    logger.warning("⚠️  No DEEPL_API_KEY_2 found. Backup translation disabled.")

# LinkedIn API configuration
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
LINKEDIN_PERSON_URN = os.getenv('LINKEDIN_PERSON_URN', '')  # Your LinkedIn person URN
LINKEDIN_ENABLED = bool(LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET and LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN)

# Instagram API configuration (via Facebook Graph API)
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')  # Facebook Page Access Token
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')  # Instagram Business Account ID
INSTAGRAM_ENABLED = bool(INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID)

# Admin authentication configuration
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')  # Set via environment variable for security

def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def ensure_app_initialized():
    """Ensure the app is initialized before handling requests"""
    global _app_initialized
    if not _app_initialized:
        logger.info("🚀 Initializing application...")
        init_db()
        setup_scheduler()
        _app_initialized = True
        logger.info("✅ Application initialized successfully")

@app.before_request
def before_request():
    """Initialize app on first request"""
    ensure_app_initialized()

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Database setup
def init_db():
    conn = None
    try:
        logger.info("📊 Initializing database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            title_pt TEXT NOT NULL,
            content TEXT NOT NULL,
            content_pt TEXT NOT NULL,
            image_url TEXT,
                images TEXT,
                slug TEXT UNIQUE,
                url TEXT NOT NULL UNIQUE,
            source TEXT NOT NULL,
            category TEXT DEFAULT 'Geral',
                published_date TIMESTAMP,
                scraped_at TIMESTAMP
        )
        ''')
        
        # Create index on slug for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_scraped_at ON articles(scraped_at DESC)')
        
        conn.commit()
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            release_db_connection(conn)

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
    """Scrape the latest 3 news articles from BBC"""
    # print("Scraping BBC news")
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
                    logger.info(f"Scraping article: {href}")
                    article_content = scrape_article_content(href)
                    if article_content:
                        articles.append(article_content)
                        logger.info(f"Successfully scraped article: {article_content['title'][:50]}...")
                        if len(articles) >= 3:
                            break
            
            if len(articles) >= 3:
                break
        
        logger.info(f"Total BBC articles found: {len(articles)}")
        return articles[:3]
        
    except Exception as e:
        logger.error(f"Error scraping BBC: {e}", exc_info=True)
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
        
        # Get more content - increase from 8 to 20 paragraphs for full text
        content = ' '.join(unique_content[:20])
        
        # Extract ALL article images (not just the main one)
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
        
        # Try to find all article images (not placeholders)
        for selector in image_selectors:
            img_elems = soup.select(selector)
            for img_elem in img_elems:
                src = img_elem.get('src') or img_elem.get('data-src')
                if src and 'placeholder' not in src.lower() and 'grey-placeholder' not in src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://www.bbc.com' + src
                    
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
                'images': all_images,  # Store all images
                'url': url,
                'source': 'BBC'
            }
        
    except Exception as e:
        logger.error(f"Error scraping article {url}: {e}")
    
    return None

def scrape_le_monde_news():
    """Scrape latest news from Le Monde"""
    try:
        url = 'https://www.lemonde.fr'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Multiple selectors to find article links
        selectors = [
            'a[data-testid="internal-link"]',
            'a[href*="/article/"]',
            '.article__link',
            '.teaser__link',
            'article a[href*="/article/"]',
            '.river__teaser a',
            '.m-teaser a'
        ]
        
        articles = []
        seen_urls = set()
        
        for selector in selectors:
            links = soup.select(selector)
            print(f"Le Monde: Found {len(links)} links with selector: {selector}")
            
            for link in links[:10]:  # Limit to first 10 per selector
                href = link.get('href')
                if not href:
                    continue
                    
                # Make URL absolute
                if href.startswith('/'):
                    href = f'https://www.lemonde.fr{href}'
                elif not href.startswith('http'):
                    continue
                
                # Skip if we've already seen this URL
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Skip non-article URLs
                if '/article/' not in href or href.endswith('/lemonde.fr'):
                    continue
                
                # Scrape article content
                article = scrape_le_monde_article_content(href)
                if article:
                    articles.append(article)
                    print(f"Successfully scraped Le Monde article: {article['title'][:50]}...")
                    
                    if len(articles) >= 2:  # Limit to 2 articles
                        break
            
            if len(articles) >= 2:
                break
        
        logger.info(f"Le Monde total articles found: {len(articles)}")
        return articles[:2]  # Return only first 2
        
    except Exception as e:
        logger.error(f"Error scraping Le Monde news: {e}")
        return []

def scrape_le_monde_article_content(url):
    """Scrape individual Le Monde article content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_selectors = [
            'h1.article__title',
            'h1[data-testid="headline"]',
            'h1.article-title',
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
            '.article__content p',
            '.article__paragraph p',
            'article p',
            '.article-body p'
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
        
        # Extract images with better filtering
        image_selectors = [
            '.article__img img',
            '.article__media img',
            'article img',
            '.article-image img',
            'img[src*="lemonde.fr"]'
        ]
        
        image_url = None
        all_images = []
        
        for selector in image_selectors:
            imgs = soup.select(selector)
            for img in imgs:
                src = img.get('src') or img.get('data-src')
                if src and 'placeholder' not in src.lower():
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = f'https://www.lemonde.fr{src}'
                    
                    # Filter out generic/default images
                    generic_patterns = [
                        'default',
                        'logo',
                        'header',
                        'footer',
                        'avatar',
                        'icon',
                        'placeholder',
                        'lemonde.fr/static/',
                        'sprite'
                    ]
                    
                    is_generic = any(pattern in src.lower() for pattern in generic_patterns)
                    
                    # Only include meaningful images
                    if not is_generic and src not in all_images:
                        all_images.append(src)
                        
                        # Set the first meaningful image as the main image
                        if image_url is None:
                            image_url = src
        
        # If no meaningful image found, try to extract from article metadata
        if not image_url:
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                image_url = meta_image.get('content')
                if image_url not in all_images:
                    all_images.append(image_url)
        
        if title and content and len(content) > 100:
            return {
                'title': title,
                'content': content,
                'image_url': image_url,
                'images': all_images,  # Store all images
                'url': url,
                'source': 'Le Monde'
            }
        
    except Exception as e:
        logger.error(f"Error scraping Le Monde article {url}: {e}")
    
    return None

def scrape_el_pais_news():
    """Scrape latest news from El Pais"""
    try:
        url = 'https://elpais.com'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Multiple selectors to find article links
        selectors = [
            'a[href*="/articulo/"]',
            'a[href*="/internacional/"]',
            'a[href*="/politica/"]',
            'a[href*="/economia/"]',
            'a[href*="/sociedad/"]',
            '.c_t a',
            '.headline a',
            'article a'
        ]
        
        articles = []
        seen_urls = set()
        
        for selector in selectors:
            links = soup.select(selector)
            print(f"El Pais: Found {len(links)} links with selector: {selector}")
            
            for link in links[:10]:  # Limit to first 10 per selector
                href = link.get('href')
                if not href:
                    continue
                    
                # Make URL absolute
                if href.startswith('/'):
                    href = f'https://elpais.com{href}'
                elif not href.startswith('http'):
                    continue
                
                # Skip if we've already seen this URL
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Skip non-article URLs
                if not any(pattern in href for pattern in ['/articulo/', '/internacional/', '/politica/', '/economia/', '/sociedad/']):
                    continue
                
                # Scrape article content
                article = scrape_el_pais_article_content(href)
                if article:
                    articles.append(article)
                    print(f"Successfully scraped El Pais article: {article['title'][:50]}...")
                    
                    if len(articles) >= 1:  # Limit to 1 article
                        break
            
            if len(articles) >= 1:
                break
        
        logger.info(f"El Pais total articles found: {len(articles)}")
        return articles[:1]  # Return only first 1
        
    except Exception as e:
        logger.error(f"Error scraping El Pais news: {e}")
        return []

def scrape_el_pais_article_content(url):
    """Scrape individual El Pais article content"""
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
            'h1.headline',
            'h1.article-title',
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
            '.article_body p',
            '.article-content p',
            'article p',
            '.entry-content p'
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
        
        # Extract images with better filtering - prioritize article content images
        image_selectors = [
            '.article_body img',  # Article content images first
            '.article-content img',
            'article img',
            '.entry-content img',
            '.media img',  # Media section images
            '.figure img'  # Figure images
        ]
        
        image_url = None
        all_images = []
        
        for selector in image_selectors:
            imgs = soup.select(selector)
            for img in imgs:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and 'placeholder' not in src.lower():
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = f'https://elpais.com{src}'
                    
                    # Filter out generic/default images
                    generic_patterns = [
                        'default',
                        'logo',
                        'header',
                        'footer',
                        'avatar',
                        'icon',
                        'placeholder',
                        'elpais.com/static/',
                        'sprite',
                        'social',
                        'share',
                        'advertisement',
                        'ad_',
                        'banner'
                    ]
                    
                    is_generic = any(pattern in src.lower() for pattern in generic_patterns)
                    
                    # Check if image has meaningful dimensions (not tiny icons)
                    width = img.get('width')
                    height = img.get('height')
                    is_small = False
                    if width and height:
                        try:
                            if int(width) < 200 or int(height) < 150:
                                is_small = True
                        except:
                            pass
                    
                    # Only include meaningful, non-generic images
                    if not is_generic and not is_small and src not in all_images:
                        all_images.append(src)
                        
                        # Set the first meaningful image as the main image
                        if image_url is None:
                            image_url = src
        
        # If no meaningful image found, try to extract from article metadata
        if not image_url:
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                image_url = meta_image.get('content')
                if image_url not in all_images:
                    all_images.append(image_url)
        
        if title and content and len(content) > 100:
            return {
                'title': title,
                'content': content,
                'image_url': image_url,
                'images': all_images,  # Store all images
                'url': url,
                'source': 'El Pais'
            }
        
    except Exception as e:
        logger.error(f"Error scraping El Pais article {url}: {e}")
    
    return None

def translate_to_portuguese(text, source_lang='en'):
    """Translate text to Portuguese using DeepL"""
    def _translate_with_engine(clean_text, translator_engine, engine_label):
        if not translator_engine:
            return None
        try:
            # DeepL can handle longer texts (max 5000 chars per call)
            if len(clean_text) > 5000:
                chunks = [clean_text[i:i+5000] for i in range(0, len(clean_text), 5000)]
                translated_chunks = []
                for chunk in chunks:
                    try:
                        result = translator_engine.translate_text(
                            chunk,
                            source_lang=source,
                            target_lang='PT-PT'  # European Portuguese
                        )
                        translated_chunks.append(result.text)
                        time.sleep(0.3)
                    except Exception as chunk_error:
                        logger.error(f"{engine_label} chunk error: {chunk_error}")
                        translated_chunks.append(chunk)
                return ' '.join(translated_chunks)
            else:
                result = translator_engine.translate_text(
                    clean_text,
                    source_lang=source,
                    target_lang='PT-PT'  # European Portuguese
                )
                return result.text
        except Exception as e:
            logger.error(f"{engine_label} translation error: {e}")
            return None

    try:
        if not text or len(text.strip()) == 0:
            return text
        
        # Clean and prepare text for translation
        text = text.strip()
        text = ' '.join(text.split())
        
        # Map source language codes for DeepL
        source_lang_map = {
            'en': 'EN',
            'fr': 'FR',
            'es': 'ES'
        }
        source = source_lang_map.get(source_lang.lower(), 'EN')
        
        # Try primary translator first
        primary_translation = _translate_with_engine(text, translator, "Primary DeepL")
        if primary_translation and primary_translation != text:
            logger.info(f"✅ Translation successful (Primary DeepL): {source_lang} → PT-PT")
            logger.info(f"   Original sample: {text[:100]}...")
            logger.info(f"   Translated sample: {primary_translation[:100]}...")
            return primary_translation
        elif primary_translation == text:
            logger.warning(f"⚠️ Translation returned original text (Primary DeepL) - may not have translated")
        
        # Fallback to backup translator if available
        if translator_backup:
            logger.warning("⚠️ Primary DeepL failed or returned original, attempting backup key")
            backup_translation = _translate_with_engine(text, translator_backup, "Backup DeepL")
            if backup_translation and backup_translation != text:
                logger.info(f"✅ Translation successful (Backup DeepL): {source_lang} → PT-PT")
                logger.info(f"   Original sample: {text[:100]}...")
                logger.info(f"   Translated sample: {backup_translation[:100]}...")
                return backup_translation
            elif backup_translation == text:
                logger.warning(f"⚠️ Translation returned original text (Backup DeepL) - may not have translated")
        
        logger.warning(f"⚠️ All DeepL translators failed, returning original text (source: {source_lang})")
        logger.warning(f"   Text length: {len(text)} chars")
        return text
            
    except Exception as e:
        logger.error(f"Translation error (all engines): {e}")
        return text

def post_process_translation(text):
    """Post-process translated text for better quality"""
    try:
        # Common corrections for better Portuguese
        corrections = {
            # Common mistranslations
            'Estados Unidos': 'Estados Unidos',
            'Reino Unido': 'Reino Unido',
            'França': 'França',
            'Alemanha': 'Alemanha',
            'Rússia': 'Rússia',
            'China': 'China',
            'Japão': 'Japão',
            
            # Fix common Google Translate issues
            'Sr.': 'Sr.',
            'Sra.': 'Sra.',
            'Dr.': 'Dr.',
            'Dra.': 'Dra.',
            'Prof.': 'Prof.',
            'Prof.ª': 'Prof.ª',
            
            # Fix currency and numbers
            '€': '€',
            '$': '$',
            '£': '£',
            '¥': '¥',
            
            # Fix common abbreviations
            'UE': 'UE',
            'EUA': 'EUA',
            'ONU': 'ONU',
            'OTAN': 'OTAN',
            'PIB': 'PIB',
            'FMI': 'FMI',
            'OMS': 'OMS',
        }
        
        # Apply corrections
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        # Capitalize first letter of sentences
        sentences = text.split('. ')
        corrected_sentences = []
        for sentence in sentences:
            if sentence.strip():
                corrected_sentences.append(sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper())
            else:
                corrected_sentences.append(sentence)
        
        return '. '.join(corrected_sentences)
        
    except Exception as e:
        print(f"Post-processing error: {e}")
        return text

def format_linkedin_post(article):
    """Format article for LinkedIn posting"""
    try:
        # Create an engaging post with hashtags
        title = article.get('title_pt', article.get('title', ''))
        content = article.get('content_pt', article.get('content', ''))
        source = article.get('source', '')
        category = article.get('category', 'Geral')
        url = article.get('url', '')
        
        # Truncate content for LinkedIn (max ~1300 chars recommended)
        max_content_length = 800
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        # Create engaging post text
        post_text = f"📰 {title}\n\n{content}\n\n"
        
        # Add source and category
        post_text += f"Fonte: {source}\n"
        post_text += f"Categoria: {category}\n\n"
        
        # Add relevant hashtags
        hashtags = {
            'Política': '#Política #Notícias #Portugal',
            'Economia': '#Economia #Mercados #Finanças',
            'Tecnologia': '#Tecnologia #Inovação #Digital',
            'Saúde': '#Saúde #BemEstar #Medicina',
            'Desporto': '#Desporto #Futebol #Competição',
            'Cultura': '#Cultura #Arte #Entretenimento',
            'Guerra e Conflitos': '#Guerra #Conflitos #Geopolítica',
            'Ambiente': '#Ambiente #Sustentabilidade #Clima',
            'Direitos Humanos': '#DireitosHumanos #Justiça #Igualdade',
            'Ciência': '#Ciência #Investigação #Descobertas',
            'Geral': '#Notícias #Informação #Portugal'
        }
        
        post_text += hashtags.get(category, '#Notícias #Informação #Portugal')
        post_text += "\n\n#TejoMag #InformaçãoAlémDasMargens"
        
        # Add link to TejoMag article (prefer slug-based URL)
        if article.get('slug'):
            tejomag_url = f"https://tejomag.pt/article/{article['slug']}"
            post_text += f"\n\n🔗 Leia mais: {tejomag_url}"
        elif url:
            post_text += f"\n\n🔗 Leia mais: {url}"
        
        return post_text
        
    except Exception as e:
        logger.error(f"Error formatting LinkedIn post: {e}")
        return None

def post_to_linkedin(article):
    """Post article to LinkedIn using LinkedIn API"""
    try:
        logger.info(f"📱 Starting LinkedIn post for: {article.get('title_pt', 'Unknown')[:50]}...")
        
        if not LINKEDIN_ENABLED:
            logger.warning("⚠️ LinkedIn posting disabled - missing credentials")
            logger.warning(f"   Client ID: {'set' if LINKEDIN_CLIENT_ID else 'missing'}, "
                         f"Client Secret: {'set' if LINKEDIN_CLIENT_SECRET else 'missing'}, "
                         f"Access Token: {'set' if LINKEDIN_ACCESS_TOKEN else 'missing'}, "
                         f"Person URN: {'set' if LINKEDIN_PERSON_URN else 'missing'}")
            return False
        
        post_text = format_linkedin_post(article)
        if not post_text:
            logger.error("Failed to format LinkedIn post")
            return False
        
        # LinkedIn API endpoint for posting
        linkedin_api_url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Prepare the post data
        post_data = {
            "author": f"urn:li:member:{LINKEDIN_PERSON_URN}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Make the API request
        response = requests.post(
            linkedin_api_url,
            headers=headers,
            data=json.dumps(post_data),
            timeout=30
        )
        
        if response.status_code == 201:
            post_id = response.headers.get('X-RestLi-Id', 'unknown')
            logger.info(f"✅ Successfully posted to LinkedIn!")
            logger.info(f"   Article: {article.get('title_pt', 'Unknown title')[:50]}...")
            logger.info(f"   Post ID: {post_id}")
            logger.info(f"   URL: {article.get('url', 'N/A')}")
            return True
        else:
            error_details = response.text[:200] if response.text else "No error details"
            logger.error(f"❌ LinkedIn posting failed!")
            logger.error(f"   Status Code: {response.status_code}")
            logger.error(f"   Article: {article.get('title_pt', 'Unknown title')[:50]}...")
            logger.error(f"   Error: {error_details}")
            return False
            
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {e}", exc_info=True)
        return False

def format_instagram_post(article):
    """Format article for Instagram posting"""
    try:
        title = article.get('title_pt', article.get('title', ''))
        content = article.get('content_pt', article.get('content', ''))
        source = article.get('source', '')
        category = article.get('category', 'Geral')
        url = article.get('url', '')
        image_url = article.get('image_url', '')
        
        # Instagram caption limit is 2200 characters
        # Truncate content for Instagram
        max_content_length = 1000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        # Create engaging caption
        caption = f"📰 {title}\n\n{content}\n\n"
        
        # Add source and category
        caption += f"Fonte: {source}\n"
        caption += f"Categoria: {category}\n\n"
        
        # Add relevant hashtags (Instagram allows up to 30 hashtags)
        hashtags = {
            'Política': '#Política #Notícias #Portugal #Atualidades',
            'Economia': '#Economia #Mercados #Finanças #Negócios',
            'Tecnologia': '#Tecnologia #Inovação #Digital #Tech',
            'Saúde': '#Saúde #BemEstar #Medicina #Cuidados',
            'Desporto': '#Desporto #Futebol #Competição #Atletismo',
            'Cultura': '#Cultura #Arte #Entretenimento #Artes',
            'Guerra e Conflitos': '#Guerra #Conflitos #Geopolítica #Mundo',
            'Ambiente': '#Ambiente #Sustentabilidade #Clima #Natureza',
            'Direitos Humanos': '#DireitosHumanos #Justiça #Igualdade #Direitos',
            'Ciência': '#Ciência #Investigação #Descobertas #Pesquisa',
            'Geral': '#Notícias #Informação #Portugal #Mundo'
        }
        
        caption += hashtags.get(category, '#Notícias #Informação #Portugal')
        caption += "\n\n#TejoMag #InformaçãoAlémDasMargens"
        
        # Add link to TejoMag article (Instagram doesn't support clickable links in captions, but we include it)
        if article.get('slug'):
            tejomag_url = f"https://tejomag.pt/article/{article['slug']}"
            caption += f"\n\n🔗 Link na bio: {tejomag_url}"
        elif url:
            caption += f"\n\n🔗 Link na bio: {url}"
        
        return {
            'caption': caption,
            'image_url': image_url
        }
        
    except Exception as e:
        logger.error(f"Error formatting Instagram post: {e}")
        return None

def post_to_instagram(article):
    """Post article to Instagram using Instagram Graph API"""
    try:
        logger.info(f"📸 Starting Instagram post for: {article.get('title_pt', 'Unknown')[:50]}...")
        
        if not INSTAGRAM_ENABLED:
            logger.warning("⚠️ Instagram posting disabled - missing credentials")
            logger.warning(f"   Access Token: {'set' if INSTAGRAM_ACCESS_TOKEN else 'missing'}, "
                         f"Business Account ID: {'set' if INSTAGRAM_BUSINESS_ACCOUNT_ID else 'missing'}")
            return False
        
        post_data = format_instagram_post(article)
        if not post_data:
            logger.error("Failed to format Instagram post")
            return False
        
        caption = post_data['caption']
        image_url = post_data['image_url']
        
        if not image_url:
            logger.warning("⚠️ No image URL available for Instagram post - Instagram requires an image")
            return False
        
        # Step 1: Create media container
        create_media_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
        
        create_media_params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': INSTAGRAM_ACCESS_TOKEN
        }
        
        create_response = requests.post(create_media_url, params=create_media_params, timeout=30)
        
        if create_response.status_code != 200:
            logger.error(f"❌ Instagram media creation failed: {create_response.status_code} - {create_response.text}")
            return False
        
        creation_id = create_response.json().get('id')
        if not creation_id:
            logger.error(f"❌ Instagram media creation failed: No creation ID returned - {create_response.text}")
            return False
        
        logger.info(f"📸 Instagram media container created: {creation_id}")
        
        # Step 2: Publish the media container
        # Wait a moment for the container to be ready
        time.sleep(2)
        
        publish_media_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
        
        publish_media_params = {
            'creation_id': creation_id,
            'access_token': INSTAGRAM_ACCESS_TOKEN
        }
        
        publish_response = requests.post(publish_media_url, params=publish_media_params, timeout=30)
        
        if publish_response.status_code == 200:
            logger.info(f"✅ Successfully posted to Instagram: {article.get('title_pt', 'Unknown title')[:50]}...")
            return True
        else:
            logger.error(f"❌ Instagram publishing failed: {publish_response.status_code} - {publish_response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}", exc_info=True)
        return False

def detect_category(title, content):
    """Detect article category based on keywords - focused on specific topics"""
    text = f"{title} {content}".lower()
    
    # French keywords for Le Monde articles
    french_keywords = {
        'Política': ['président', 'gouvernement', 'ministre', 'élection', 'politique', 'parlement', 'assemblée', 'sénat', 'vote', 'candidat', 'parti', 'campagne', 'municipal', 'régional', 'national'],
        'Economia': ['économie', 'économique', 'finance', 'financier', 'bourse', 'entreprise', 'emploi', 'chômage', 'croissance', 'crise', 'investissement', 'bancaire', 'fiscal', 'budget', 'déficit'],
        'Tecnologia': ['technologie', 'technologique', 'numérique', 'digital', 'internet', 'réseaux sociaux', 'application', 'logiciel', 'intelligence artificielle', 'robot', 'innovation', 'start-up'],
        'Saúde': ['santé', 'médical', 'hôpital', 'médecin', 'maladie', 'virus', 'épidémie', 'vaccin', 'traitement', 'thérapie', 'pharmaceutique'],
        'Desporto': ['sport', 'sportif', 'football', 'rugby', 'tennis', 'cyclisme', 'jeux olympiques', 'championnat', 'équipe', 'joueur', 'match', 'compétition'],
        'Cultura': ['culture', 'culturel', 'art', 'artistique', 'musée', 'théâtre', 'cinéma', 'livre', 'littérature', 'musique', 'festival', 'exposition'],
        'Guerra e Conflitos': ['guerre', 'conflit', 'militaire', 'armée', 'soldat', 'bataille', 'combat', 'terrorisme', 'attentat', 'sécurité', 'défense'],
        'Ambiente': ['environnement', 'environnemental', 'climat', 'écologie', 'pollution', 'énergie', 'recyclage', 'biodiversité', 'nature', 'vert'],
        'Direitos Humanos': ['droits', 'humain', 'liberté', 'égalité', 'discrimination', 'refugié', 'migrant', 'asile', 'justice', 'tribunal'],
        'Ciência': ['science', 'scientifique', 'recherche', 'étude', 'découverte', 'laboratoire', 'université', 'recherche', 'innovation', 'expérimentation']
    }
    
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
    
    # Count keyword matches for each category (English)
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            category_scores[category] = score
    
    # Count keyword matches for each category (French)
    for category, keywords in french_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            # Add to existing score if category already exists
            if category in category_scores:
                category_scores[category] += score
            else:
                category_scores[category] = score
    
    # Return category with highest score, or 'Geral' if no matches
    if category_scores:
        return max(category_scores, key=category_scores.get)
    return 'Geral'

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get latest news articles from database with pagination"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        with get_db_cursor() as cursor:
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM articles')
            total_count = cursor.fetchone()[0]
            
            # Get paginated articles
            cursor.execute('''
                SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
                FROM articles 
                ORDER BY scraped_at DESC
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            
            articles = cursor.fetchall()
            
            # Convert to list of dictionaries
            import json
            article_list = []
            for article in articles:
                images = []
                try:
                    if article[6]:  # images column
                        images = json.loads(article[6])
                except:
                    pass
                
                article_list.append({
                    'id': article[0],
                    'title': article[1],
                    'title_pt': article[2],
                    'content': article[3],
                    'content_pt': article[4],
                    'image_url': article[5],
                    'images': images,
                    'slug': article[7],
                    'url': article[8],
                    'source': article[9],
                    'category': article[10],
                    'published_date': article[11],
                    'scraped_at': article[12]
                })
            
            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit
            has_next = page < total_pages
            has_prev = page > 1
        
        return jsonify({
            'articles': article_list,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'limit': limit,
                'has_next': has_next,
                'has_prev': has_prev
            }
        })
        
    except ValueError as e:
        logger.error(f"Invalid pagination parameters: {e}")
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    except Exception as e:
        logger.error(f"Error fetching news: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch news articles'}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'TejoMag API is running!',
        'version': '1.0.0',
        'frontend': 'https://tejomag.pt',
        'endpoints': {
            'news': '/api/news',
            'health': '/api/health',
            'categories': '/api/news/categories',
            'search': '/api/news/search?q=query',
            'linkedin_post': '/api/linkedin/post/{article_id}'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM articles')
            article_count = cursor.fetchone()[0]
            
            return jsonify({
                'status': 'healthy', 
                'message': 'News API is running',
                'database': 'connected',
                'database_type': 'PostgreSQL',
                'articles_count': article_count,
                'linkedin_enabled': LINKEDIN_ENABLED,
                'instagram_enabled': INSTAGRAM_ENABLED,
                'deepl_enabled': bool(translator or translator_backup)
            })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy', 
            'message': 'Database connection failed',
            'error': str(e)
        }), 500

@app.route('/api/linkedin/post/<int:article_id>', methods=['POST'])
def post_article_to_linkedin(article_id):
    """Manually post a specific article to LinkedIn"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('''
                SELECT title, title_pt, content, content_pt, source, category, url
                FROM articles WHERE id = %s
            ''', (article_id,))
            
            article = cursor.fetchone()
            if not article:
                return jsonify({'error': 'Article not found'}), 404
            
            # Prepare article data
            article_data = {
                'title_pt': article[1],
                'content_pt': article[3],
                'source': article[4],
                'category': article[5],
                'url': article[6]
            }
            
            # Post to LinkedIn
            success = post_to_linkedin(article_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Article posted to LinkedIn successfully',
                    'article_id': article_id,
                    'title': article_data['title_pt']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to post to LinkedIn',
                    'article_id': article_id
                }), 500
                
    except Exception as e:
        logger.error(f"Error posting article {article_id} to LinkedIn: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    categories = ['Política', 'Economia', 'Tecnologia', 'Saúde', 'Desporto', 'Cultura', 'Guerra e Conflitos', 'Ambiente', 'Direitos Humanos', 'Ciência', 'Geral']
    return jsonify({'categories': categories})

@app.route('/api/news/search', methods=['GET'])
def search_news():
    """Search news articles by query"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        with get_db_cursor() as cursor:
            # Search in both title and content using PostgreSQL ILIKE for case-insensitive search
            search_term = f'%{query}%'
            cursor.execute('''
                SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
                FROM articles 
                WHERE title_pt ILIKE %s OR content_pt ILIKE %s OR title ILIKE %s OR content ILIKE %s
                ORDER BY scraped_at DESC
                LIMIT 50
            ''', (search_term, search_term, search_term, search_term))
            
            articles = []
            for row in cursor.fetchall():
                import json
                images = []
                try:
                    if row[6]:  # images column
                        images = json.loads(row[6])
                except:
                    pass
                
                articles.append({
                    'id': row[0],
                    'title': row[1],
                    'title_pt': row[2],
                    'content': row[3],
                    'content_pt': row[4],
                    'image_url': row[5],
                    'images': images,
                    'slug': row[7],
                    'url': row[8],
                    'source': row[9],
                    'category': row[10],
                    'published_date': row[11],
                    'scraped_at': row[12]
                })
            
            return jsonify({'articles': articles, 'query': query, 'count': len(articles)})
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate XML sitemap for all articles"""
    from flask import Response
    from datetime import datetime
    
    try:
        with get_db_cursor() as cursor:
            # Get all articles with slugs
            cursor.execute('''
                SELECT slug, scraped_at
                FROM articles
                WHERE slug IS NOT NULL
                ORDER BY scraped_at DESC
            ''')
            
            articles = cursor.fetchall()
            
            # Start building XML sitemap
            xml = ['<?xml version="1.0" encoding="UTF-8"?>']
            xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
            
            # Add homepage
            xml.append('  <url>')
            xml.append('    <loc>https://tejomag.pt/</loc>')
            xml.append('    <lastmod>' + datetime.now().strftime('%Y-%m-%d') + '</lastmod>')
            xml.append('    <changefreq>hourly</changefreq>')
            xml.append('    <priority>1.0</priority>')
            xml.append('  </url>')
            
            # Add all article pages
            for article in articles:
                slug = article[0]
                scraped_at = article[1]
                
                # Format date
                if scraped_at:
                    lastmod = scraped_at.strftime('%Y-%m-%d') if isinstance(scraped_at, datetime) else datetime.fromisoformat(str(scraped_at)).strftime('%Y-%m-%d')
                else:
                    lastmod = datetime.now().strftime('%Y-%m-%d')
                
                xml.append('  <url>')
                xml.append(f'    <loc>https://tejomag.pt/article/{slug}</loc>')
                xml.append(f'    <lastmod>{lastmod}</lastmod>')
                xml.append('    <changefreq>weekly</changefreq>')
                xml.append('    <priority>0.8</priority>')
                xml.append('  </url>')
            
            xml.append('</urlset>')
            
            # Return XML response with proper headers
            response = Response('\n'.join(xml), mimetype='application/xml')
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Content-Type'] = 'application/xml; charset=utf-8'
            return response
            
    except Exception as e:
        logger.error(f"Sitemap generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/category/<category>', methods=['GET'])
def get_news_by_category(category):
    """Get news articles by category"""
    try:
        with get_db_cursor() as cursor:
            # Get articles from the specified category
            cursor.execute('''
                SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
                FROM articles 
                WHERE category = %s 
                ORDER BY scraped_at DESC
            ''', (category,))
            
            articles = cursor.fetchall()
            
            # Convert to list of dictionaries
            import json
            article_list = []
            for article in articles:
                images = []
                try:
                    if article[6]:  # images column
                        images = json.loads(article[6])
                except:
                    pass
                    
                article_list.append({
                    'id': article[0],
                    'title': article[1],
                    'title_pt': article[2],
                    'content': article[3],
                    'content_pt': article[4],
                    'image_url': article[5],
                    'images': images,
                    'slug': article[7],
                    'url': article[8],
                    'source': article[9],
                    'category': article[10],
                    'published_date': article[11],
                    'scraped_at': article[12]
                })
            
            return jsonify({
                'articles': article_list,
                'category': category,
                'count': len(article_list)
            })
        
    except Exception as e:
        logger.error(f"Error fetching category {category}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/slug/<slug>', methods=['GET'])
def get_news_by_slug(slug):
    """Get a single article by slug"""
    try:
        with get_db_cursor() as cursor:
            # Get article by slug
            cursor.execute('''
                SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
                FROM articles 
                WHERE slug = %s
            ''', (slug,))
            
            article = cursor.fetchone()
            
            if not article:
                return jsonify({'error': 'Article not found'}), 404
            
            import json
            images = []
            try:
                if article[6]:  # images column
                    images = json.loads(article[6])
            except:
                pass
            
            article_dict = {
                'id': article[0],
                'title': article[1],
                'title_pt': article[2],
                'content': article[3],
                'content_pt': article[4],
                'image_url': article[5],
                'images': images,
                'slug': article[7],
                'url': article[8],
                'source': article[9],
                'category': article[10],
                'published_date': article[11],
                'scraped_at': article[12]
            }
            
            return jsonify(article_dict)
        
    except Exception as e:
        logger.error(f"Error fetching article by slug {slug}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch article'}), 500

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
        logger.error(f"Error refreshing news: {e}", exc_info=True)
        return jsonify({'error': 'Failed to refresh news'}), 500

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
        logger.error(f"Error fetching scheduler status: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch scheduler status'}), 500

# Admin authentication endpoints
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not ADMIN_PASSWORD:
            logger.warning("⚠️ ADMIN_PASSWORD not set in environment variables")
            return jsonify({'error': 'Admin authentication not configured'}), 500
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            logger.info(f"✅ Admin login successful: {username}")
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'username': username
            })
        else:
            logger.warning(f"❌ Admin login failed: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Error during admin login: {e}", exc_info=True)
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout endpoint"""
    session.clear()
    logger.info("✅ Admin logout successful")
    return jsonify({'success': True, 'message': 'Logout successful'})

@app.route('/api/admin/status', methods=['GET'])
def admin_status():
    """Check admin authentication status"""
    is_authenticated = session.get('admin_logged_in', False)
    return jsonify({
        'authenticated': is_authenticated,
        'username': session.get('admin_username') if is_authenticated else None
    })

# Admin article management endpoints
@app.route('/api/admin/articles', methods=['GET'])
@require_admin
def admin_list_articles():
    """Get all articles for admin (with pagination)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        with get_db_cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM articles')
            total_count = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
                FROM articles 
                ORDER BY scraped_at DESC
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            
            articles = []
            for article in cursor.fetchall():
                images = []
                try:
                    if article[6]:  # images column
                        images = json.loads(article[6])
                except:
                    pass
                
                articles.append({
                    'id': article[0],
                    'title': article[1],
                    'title_pt': article[2],
                    'content': article[3],
                    'content_pt': article[4],
                    'image_url': article[5],
                    'images': images,
                    'slug': article[7],
                    'url': article[8],
                    'source': article[9],
                    'category': article[10],
                    'published_date': article[11].isoformat() if article[11] else None,
                    'scraped_at': article[12].isoformat() if article[12] else None
                })
            
            total_pages = (total_count + limit - 1) // limit
            
            return jsonify({
                'articles': articles,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'limit': limit
                }
            })
            
    except Exception as e:
        logger.error(f"Error fetching articles for admin: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch articles'}), 500

@app.route('/api/admin/articles', methods=['POST'])
@require_admin
def admin_create_article():
    """Create a new article (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title_pt', 'content_pt', 'source']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        title_pt = data.get('title_pt', '')
        content_pt = data.get('content_pt', '')
        title = data.get('title', title_pt)  # Use Portuguese title as fallback
        content = data.get('content', content_pt)  # Use Portuguese content as fallback
        source = data.get('source', 'Manual')
        category = data.get('category', 'Geral')
        image_url = data.get('image_url', '')
        images = data.get('images', [])
        url = data.get('url', '')
        
        # Generate slug from Portuguese title
        slug = generate_slug(title_pt)
        
        with get_db_cursor() as cursor:
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while True:
                cursor.execute('SELECT id FROM articles WHERE slug = %s', (slug,))
                if not cursor.fetchone():
                    break
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            # Convert images list to JSON
            images_json = json.dumps(images)
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO articles (title, title_pt, content, content_pt, image_url, images, slug, url, source, category, scraped_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (title, title_pt, content, content_pt, image_url, images_json, slug, url, source, category, now))
            
            result = cursor.fetchone()
            if result:
                article_id = result[0]
                logger.info(f"✅ Admin created article: {title_pt[:50]}... (id: {article_id}, slug: {slug})")
                
                # Post to LinkedIn if enabled
                if LINKEDIN_ENABLED:
                    try:
                        tejomag_url = f"https://tejomag.pt/article/{slug}"
                        linkedin_article = {
                            'title_pt': title_pt,
                            'content_pt': content_pt,
                            'source': source,
                            'category': category,
                            'url': tejomag_url,
                            'slug': slug
                        }
                        linkedin_thread = threading.Thread(
                            target=post_to_linkedin,
                            args=(linkedin_article,),
                            daemon=True
                        )
                        linkedin_thread.start()
                        logger.info(f"📱 LinkedIn posting queued for admin-created article: {title_pt[:50]}...")
                    except Exception as e:
                        logger.error(f"❌ Error queuing LinkedIn post: {e}", exc_info=True)
                
                # Post to Instagram if enabled
                if INSTAGRAM_ENABLED:
                    try:
                        tejomag_url = f"https://tejomag.pt/article/{slug}"
                        instagram_article = {
                            'title_pt': title_pt,
                            'content_pt': content_pt,
                            'source': source,
                            'category': category,
                            'url': tejomag_url,
                            'slug': slug,
                            'image_url': image_url
                        }
                        instagram_thread = threading.Thread(
                            target=post_to_instagram,
                            args=(instagram_article,),
                            daemon=True
                        )
                        instagram_thread.start()
                        logger.info(f"📸 Instagram posting queued for admin-created article: {title_pt[:50]}...")
                    except Exception as e:
                        logger.error(f"❌ Error queuing Instagram post: {e}", exc_info=True)
                
                return jsonify({
                    'success': True,
                    'message': 'Article created successfully',
                    'article': {
                        'id': article_id,
                        'slug': slug,
                        'title_pt': title_pt
                    }
                }), 201
            else:
                return jsonify({'error': 'Failed to create article'}), 500
                
    except IntegrityError as e:
        logger.error(f"Integrity error creating article: {e}", exc_info=True)
        return jsonify({'error': 'Article with this slug or URL already exists'}), 409
    except Exception as e:
        logger.error(f"Error creating article: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create article'}), 500

@app.route('/api/admin/articles/<int:article_id>', methods=['PUT'])
@require_admin
def admin_update_article(article_id):
    """Update an existing article (admin only)"""
    try:
        data = request.get_json()
        
        with get_db_cursor() as cursor:
            # Check if article exists
            cursor.execute('SELECT id FROM articles WHERE id = %s', (article_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Article not found'}), 404
            
            # Build update query dynamically based on provided fields
            updates = []
            values = []
            
            if 'title_pt' in data:
                updates.append('title_pt = %s')
                values.append(data['title_pt'])
            if 'content_pt' in data:
                updates.append('content_pt = %s')
                values.append(data['content_pt'])
            if 'title' in data:
                updates.append('title = %s')
                values.append(data['title'])
            if 'content' in data:
                updates.append('content = %s')
                values.append(data['content'])
            if 'category' in data:
                updates.append('category = %s')
                values.append(data['category'])
            if 'image_url' in data:
                updates.append('image_url = %s')
                values.append(data['image_url'])
            if 'images' in data:
                updates.append('images = %s')
                values.append(json.dumps(data['images']))
            if 'url' in data:
                updates.append('url = %s')
                values.append(data['url'])
            
            if not updates:
                return jsonify({'error': 'No fields to update'}), 400
            
            # If title_pt changed, regenerate slug
            if 'title_pt' in data:
                new_slug = generate_slug(data['title_pt'])
                # Check if new slug is unique (excluding current article)
                counter = 1
                original_slug = new_slug
                while True:
                    cursor.execute('SELECT id FROM articles WHERE slug = %s AND id != %s', (new_slug, article_id))
                    if not cursor.fetchone():
                        break
                    new_slug = f"{original_slug}-{counter}"
                    counter += 1
                updates.append('slug = %s')
                values.append(new_slug)
            
            values.append(article_id)
            query = f"UPDATE articles SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, values)
            
            logger.info(f"✅ Admin updated article: {article_id}")
            return jsonify({
                'success': True,
                'message': 'Article updated successfully'
            })
            
    except IntegrityError as e:
        logger.error(f"Integrity error updating article: {e}", exc_info=True)
        return jsonify({'error': 'Update would violate unique constraint'}), 409
    except Exception as e:
        logger.error(f"Error updating article: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update article'}), 500

@app.route('/api/admin/articles/<int:article_id>', methods=['DELETE'])
@require_admin
def admin_delete_article(article_id):
    """Delete an article (admin only)"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('SELECT id, title_pt FROM articles WHERE id = %s', (article_id,))
            article = cursor.fetchone()
            
            if not article:
                return jsonify({'error': 'Article not found'}), 404
            
            cursor.execute('DELETE FROM articles WHERE id = %s', (article_id,))
            logger.info(f"✅ Admin deleted article: {article_id} - {article[1][:50]}...")
            
            return jsonify({
                'success': True,
                'message': 'Article deleted successfully'
            })
            
    except Exception as e:
        logger.error(f"Error deleting article: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete article'}), 500

def run_news_job():
    """Background job to fetch and save latest news from multiple sources"""
    try:
        logger.info(f"🔄 Running scheduled news job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_articles = []
        
        # Scrape BBC news
        print("📰 Scraping BBC News...")
        bbc_articles = scrape_bbc_news()
        if bbc_articles:
            all_articles.extend(bbc_articles)
            print(f"✅ Found {len(bbc_articles)} BBC articles")
        else:
            print("❌ No BBC articles found")
        
        # Scrape Le Monde news
        print("📰 Scraping Le Monde...")
        lemonde_articles = scrape_le_monde_news()
        if lemonde_articles:
            all_articles.extend(lemonde_articles)
            print(f"✅ Found {len(lemonde_articles)} Le Monde articles")
        else:
            print("❌ No Le Monde articles found")
        
        # Scrape El Pais news
        print("📰 Scraping El Pais...")
        elpais_articles = scrape_el_pais_news()
        if elpais_articles:
            all_articles.extend(elpais_articles)
            print(f"✅ Found {len(elpais_articles)} El Pais articles")
        else:
            print("❌ No El Pais articles found")
        
        if not all_articles:
            logger.warning("❌ No articles found from any source")
            print("❌ No articles found from any source")
            return
        
        logger.info(f"📰 Total articles found: {len(all_articles)}")
        print(f"📰 Total articles found: {len(all_articles)}")
        logger.info(f"🔗 LinkedIn posting enabled: {LINKEDIN_ENABLED}")
        
        # Process and save articles
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            processed_count = 0
            skipped_count = 0
            for article in all_articles:
                # Check if article already exists
                cursor.execute('SELECT id FROM articles WHERE url = %s', (article['url'],))
                existing = cursor.fetchone()
                
                if not existing:
                    # Use a savepoint for each article insert so failures don't affect others
                    savepoint_name = f"sp_{processed_count + skipped_count}"
                    try:
                        cursor.execute(f"SAVEPOINT {savepoint_name}")
                        
                        # Determine source language for better translation
                        if article['source'] == 'Le Monde':
                            source_lang = 'fr'
                        elif article['source'] == 'El Pais':
                            source_lang = 'es'
                        else:
                            source_lang = 'en'  # Default to English for BBC
                        
                        # Translate and store new article
                        logger.info(f"🌐 Translating article from {source_lang.upper()}: {article['title'][:50]}...")
                        title_pt = translate_to_portuguese(article['title'], source_lang)
                        content_pt = translate_to_portuguese(article['content'], source_lang)
                        
                        # Log translation status
                        title_translated = title_pt != article['title']
                        content_translated = content_pt != article['content']
                        if title_translated and content_translated:
                            logger.info(f"✅ Article fully translated to Portuguese")
                        elif title_translated or content_translated:
                            logger.warning(f"⚠️ Article partially translated (title: {title_translated}, content: {content_translated})")
                        else:
                            logger.error(f"❌ Article NOT translated - both title and content are original")
                        
                        # Detect category
                        category = detect_category(article['title'], article['content'])
                        
                        # Generate slug from Portuguese title
                        slug = generate_slug(title_pt)
                        
                        # Ensure slug is unique
                        counter = 1
                        original_slug = slug
                        while True:
                            cursor.execute('SELECT id FROM articles WHERE slug = %s', (slug,))
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
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        ''', (article['title'], title_pt, article['content'], content_pt, 
                              article.get('image_url'), images_json, slug, article['url'], article['source'], category, now))
                        
                        result = cursor.fetchone()
                        if result is None:
                            logger.warning(f"⚠️ INSERT succeeded but no ID returned for: {article['title'][:50]}...")
                            cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                            skipped_count += 1
                            continue
                        
                        article_id = result[0]
                        processed_count += 1
                        logger.info(f"✅ Added {article['source']}: {article['title'][:50]}... (slug: {slug}, id: {article_id})")
                        logger.info(f"   Translation status: Title={'✅' if title_translated else '❌'}, Content={'✅' if content_translated else '❌'}")
                        logger.info(f"   Portuguese title: {title_pt[:60]}...")
                        print(f"✅ Added {article['source']}: {article['title'][:50]}... (slug: {slug}, id: {article_id})")
                        
                        # Release savepoint on success
                        cursor.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                        
                        # Post to LinkedIn if enabled (only after successful insert)
                        if LINKEDIN_ENABLED:
                            try:
                                # Create article data for LinkedIn posting with TejoMag URL
                                tejomag_url = f"https://tejomag.pt/article/{slug}"
                                linkedin_article = {
                                    'title_pt': title_pt,
                                    'content_pt': content_pt,
                                    'source': article['source'],
                                    'category': category,
                                    'url': tejomag_url,  # Use TejoMag article URL, not original
                                    'slug': slug
                                }
                                
                                # Post to LinkedIn in a separate thread to avoid blocking
                                linkedin_thread = threading.Thread(
                                    target=post_to_linkedin,
                                    args=(linkedin_article,),
                                    daemon=True
                                )
                                linkedin_thread.start()
                                logger.info(f"📱 LinkedIn posting queued for: {title_pt[:50]}... (URL: {tejomag_url})")
                                print(f"📱 LinkedIn posting queued for: {title_pt[:50]}...")
                                
                            except Exception as e:
                                logger.error(f"❌ Error queuing LinkedIn post: {e}", exc_info=True)
                                print(f"❌ Error queuing LinkedIn post: {e}")
                        else:
                            logger.warning("⚠️ LinkedIn posting is disabled - missing credentials")
                        
                        # Post to Instagram if enabled
                        if INSTAGRAM_ENABLED:
                            try:
                                # Create article data for Instagram posting
                                instagram_article = {
                                    'title_pt': title_pt,
                                    'content_pt': content_pt,
                                    'source': article['source'],
                                    'category': category,
                                    'url': tejomag_url,
                                    'slug': slug,
                                    'image_url': article.get('image_url', '')
                                }
                                
                                # Post to Instagram in a separate thread to avoid blocking
                                instagram_thread = threading.Thread(
                                    target=post_to_instagram,
                                    args=(instagram_article,),
                                    daemon=True
                                )
                                instagram_thread.start()
                                logger.info(f"📸 Instagram posting queued for: {title_pt[:50]}... (URL: {tejomag_url})")
                                print(f"📸 Instagram posting queued for: {title_pt[:50]}...")
                                
                            except Exception as e:
                                logger.error(f"❌ Error queuing Instagram post: {e}", exc_info=True)
                                print(f"❌ Error queuing Instagram post: {e}")
                        else:
                            logger.warning("⚠️ Instagram posting is disabled - missing credentials")
                        
                    except IntegrityError as e:
                        # Article was inserted between check and INSERT (race condition) or constraint violation
                        cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                        skipped_count += 1
                        logger.info(f"⏭️  Skipped (constraint violation/race condition): {article['title'][:50]}... - {str(e)[:100]}")
                        print(f"⏭️  Skipped (constraint violation/race condition): {article['title'][:50]}...")
                        continue
                    except Exception as e:
                        # Catch any other unexpected errors during insert
                        cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                        logger.error(f"❌ Error inserting article {article['title'][:50]}...: {e}", exc_info=True)
                        skipped_count += 1
                        continue
            else:
                skipped_count += 1
                logger.info(f"⏭️  Skipped (already exists): {article['title'][:50]}...")
                print(f"⏭️  Skipped (already exists): {article['title'][:50]}...")
            
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                release_db_connection(conn)
        
        logger.info(f"🎉 Scheduled job completed: {processed_count} new articles added, {skipped_count} skipped (already exist) from {len(set(article['source'] for article in all_articles))} sources")
        logger.info(f"📊 Job Summary:")
        logger.info(f"   - Articles processed: {len(all_articles)}")
        logger.info(f"   - New articles added: {processed_count}")
        logger.info(f"   - Articles skipped: {skipped_count}")
        logger.info(f"   - Sources: {', '.join(set(article['source'] for article in all_articles))}")
        logger.info(f"   - LinkedIn enabled: {LINKEDIN_ENABLED}")
        logger.info(f"   - Instagram enabled: {INSTAGRAM_ENABLED}")
        logger.info(f"   - DeepL enabled: {bool(translator or translator_backup)}")
        print(f"🎉 Scheduled job completed: {processed_count} new articles added, {skipped_count} skipped (already exist) from {len(set(article['source'] for article in all_articles))} sources")
        
    except Exception as e:
        logger.error(f"❌ Error in scheduled job: {e}", exc_info=True)
        print(f"❌ Error in scheduled job: {e}")

def run_scheduler():
    """Run the scheduler in a separate thread"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def setup_scheduler():
    """Setup the scheduled jobs"""
    # Schedule news job to run every 30 minutes
    schedule.every(30).minutes.do(run_news_job)
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("⏰ Scheduler started - news will be fetched every 30 minutes")
    
    # Run initial news fetch in background (non-blocking)
    initial_fetch_thread = threading.Thread(target=run_news_job, daemon=True)
    initial_fetch_thread.start()
    print("🚀 Initial news fetch started in background...")

if __name__ == '__main__':
    init_db()
    print("Starting News Translation API...")
    print("API will be available at: http://localhost:5002")
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
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down TejoMag...")
        print("Goodbye! 👋")
