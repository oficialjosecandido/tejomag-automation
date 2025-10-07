from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import deepl
import sqlite3
import os
from datetime import datetime
import time
import schedule
import threading
import atexit
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize DeepL translator
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY', '')
translator = None

if DEEPL_API_KEY:
    try:
        translator = deepl.Translator(DEEPL_API_KEY)
        logger.info("✅ DeepL translator initialized")
    except Exception as e:
        logger.error(f"DeepL initialization failed: {e}")
else:
    logger.warning("⚠️  No DEEPL_API_KEY found. Translation disabled.")

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
                    
                    if len(articles) >= 3:  # Limit to 3 articles
                        break
            
            if len(articles) >= 3:
                break
        
        logger.info(f"Le Monde total articles found: {len(articles)}")
        return articles[:3]  # Return only first 3
        
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
        
        # Extract ALL images
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
                'source': 'Le Monde'
            }
        
    except Exception as e:
        logger.error(f"Error scraping Le Monde article {url}: {e}")
    
    return None

def translate_to_portuguese(text, source_lang='en'):
    """Translate text to Portuguese using DeepL"""
    try:
        if not text or len(text.strip()) == 0:
            return text
        
        if not translator:
            logger.warning("Translator not initialized, returning original text")
            return text
        
        # Clean and prepare text for translation
        text = text.strip()
        text = ' '.join(text.split())
        
        # Map source language codes for DeepL
        source_lang_map = {
            'en': 'EN',
            'fr': 'FR'
        }
        source = source_lang_map.get(source_lang.lower(), 'EN')
        
        # DeepL can handle longer texts
        if len(text) > 5000:
            chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
            translated_chunks = []
            for chunk in chunks:
                try:
                    result = translator.translate_text(
                        chunk, 
                        source_lang=source,
                        target_lang='PT-PT'  # European Portuguese
                    )
                    translated_chunks.append(result.text)
                    time.sleep(0.3)
                except Exception as chunk_error:
                    logger.error(f"Chunk translation error: {chunk_error}")
                    translated_chunks.append(chunk)
            return ' '.join(translated_chunks)
        else:
            result = translator.translate_text(
                text,
                source_lang=source,
                target_lang='PT-PT'  # European Portuguese
            )
            return result.text
            
    except Exception as e:
        logger.error(f"Translation error: {e}")
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
    """Get latest news articles from database"""
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        # Get all articles from database, ordered by most recent first
        cursor.execute('''
            SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
            FROM articles 
            ORDER BY scraped_at DESC
        ''')
        
        articles = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        article_list = []
        for article in articles:
            import json
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
            'count': len(article_list)
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
            SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
            FROM articles 
            WHERE category = ? 
            ORDER BY scraped_at DESC
        ''', (category,))
        
        articles = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        article_list = []
        for article in articles:
            import json
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/slug/<slug>', methods=['GET'])
def get_news_by_slug(slug):
    """Get a single article by slug"""
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        # Get article by slug
        cursor.execute('''
            SELECT id, title, title_pt, content, content_pt, image_url, images, slug, url, source, category, published_date, scraped_at
            FROM articles 
            WHERE slug = ?
        ''', (slug,))
        
        article = cursor.fetchone()
        conn.close()
        
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
        
        if not all_articles:
            print("❌ No articles found from any source")
            return
        
        print(f"📰 Total articles found: {len(all_articles)}")
        
        # Process and save articles
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        
        processed_count = 0
        for article in all_articles:
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
                
                # Generate slug from title
                slug = generate_slug(article['title'])
                
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
                print(f"✅ Added {article['source']}: {article['title'][:50]}... (slug: {slug})")
            else:
                print(f"⏭️  Skipped (already exists): {article['title'][:50]}...")
        
        conn.commit()
        conn.close()
        
        print(f"🎉 Scheduled job completed: {processed_count} new articles added from {len(set(article['source'] for article in all_articles))} sources")
        
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
        app.run(debug=True, host='0.0.0.0', port=5002)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down TejoMag...")
        print("Goodbye! 👋")
