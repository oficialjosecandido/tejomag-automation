import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import config from '../config';

const ArticleDetailPage = () => {
  const { slug } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showOriginalText, setShowOriginalText] = useState(false);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        // Try to fetch by slug first
        let response;
        try {
          response = await axios.get(`${config.API_BASE_URL}/api/news/slug/${slug}`);
          setArticle(response.data);
        } catch (slugError) {
          // If 404, article doesn't exist
          if (slugError.response && slugError.response.status === 404) {
            setError('Artigo não encontrado');
            setLoading(false);
            return;
          }
          
          // If slug fails with other error, try as ID (for backward compatibility)
          try {
            const allResponse = await axios.get(`${config.API_BASE_URL}/api/news`);
            const articles = allResponse.data.articles || [];
            const foundArticle = articles.find(a => a.id.toString() === slug);
            
            if (foundArticle) {
              setArticle(foundArticle);
            } else {
              setError('Artigo não encontrado');
            }
          } catch (idError) {
            setError('Erro ao carregar o artigo');
          }
        }
      } catch (err) {
        console.error('Error fetching article:', err);
        if (err.response && err.response.status === 404) {
          setError('Artigo não encontrado');
        } else {
          setError('Erro ao carregar o artigo');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [slug]);

  // SEO: Update document title and meta tags when article loads
  useEffect(() => {
    if (article) {
      const articleUrl = window.location.href;
      const articleTitle = article.title_pt || article.title;
      const articleContent = article.content_pt || article.content;
      
      // Create better meta description (first 155 characters, end at word boundary)
      let description = articleContent.substring(0, 155);
      const lastSpace = description.lastIndexOf(' ');
      if (lastSpace > 100) {
        description = description.substring(0, lastSpace);
      }
      description = description.trim() + '...';
      
      // Update page title
      document.title = `${articleTitle} | TejoMag`;
      
      // Update or create meta description
      updateMetaTag('description', description);
      
      // Add language tag
      updateMetaTag('language', 'pt-PT');
      
      // Add keywords
      const keywords = [
        article.category,
        article.source,
        'notícias',
        'internacional',
        'português',
        'atualidades'
      ].filter(Boolean).join(', ');
      updateMetaTag('keywords', keywords);
      
      // Add article meta tags
      updateMetaTag('article:published_time', article.published_date || article.scraped_at);
      updateMetaTag('article:modified_time', article.scraped_at);
      updateMetaTag('article:author', article.source);
      updateMetaTag('article:section', article.category);
      if (article.category) {
        updateMetaTag('article:tag', article.category);
      }

      // Add canonical URL
      let canonicalLink = document.querySelector('link[rel="canonical"]');
      if (!canonicalLink) {
        canonicalLink = document.createElement('link');
        canonicalLink.setAttribute('rel', 'canonical');
        document.head.appendChild(canonicalLink);
      }
      canonicalLink.setAttribute('href', articleUrl);

      // Add Open Graph tags for social sharing
      updateMetaTag('og:title', articleTitle);
      updateMetaTag('og:description', description);
      updateMetaTag('og:image', article.image_url || `${window.location.origin}/og-image.jpg`);
      updateMetaTag('og:url', articleUrl);
      updateMetaTag('og:type', 'article');
      updateMetaTag('og:site_name', 'TejoMag');
      updateMetaTag('og:locale', 'pt_PT');
      updateMetaTag('og:article:author', article.source);
      updateMetaTag('og:article:published_time', article.published_date || article.scraped_at);
      updateMetaTag('og:article:modified_time', article.scraped_at);
      updateMetaTag('og:article:section', article.category);
      if (article.category) {
        updateMetaTag('og:article:tag', article.category);
      }
      
      // Add Twitter Card tags
      updateMetaTag('twitter:card', 'summary_large_image');
      updateMetaTag('twitter:title', articleTitle);
      updateMetaTag('twitter:description', description);
      updateMetaTag('twitter:image', article.image_url || `${window.location.origin}/og-image.jpg`);
      updateMetaTag('twitter:site', '@tejomag');

      // Add JSON-LD structured data
      addStructuredData(article, articleUrl, description);
      
      // Add breadcrumb structured data
      addBreadcrumbStructuredData(article);
    }
  }, [article]);

  const updateMetaTag = (property, content) => {
    if (!content) return;
    
    let meta = document.querySelector(`meta[property="${property}"]`);
    if (!meta) {
      meta = document.querySelector(`meta[name="${property}"]`);
    }
    
    if (meta) {
      meta.setAttribute('content', content);
    } else {
      meta = document.createElement('meta');
      if (property.startsWith('og:') || property.startsWith('article:')) {
        meta.setAttribute('property', property);
      } else {
        meta.setAttribute('name', property);
      }
      meta.setAttribute('content', content);
      document.head.appendChild(meta);
    }
  };

  const addStructuredData = (article, articleUrl, description) => {
    // Remove existing article structured data
    const existingScripts = document.querySelectorAll('script[type="application/ld+json"]');
    existingScripts.forEach(script => {
      try {
        const data = JSON.parse(script.textContent);
        if (data['@type'] === 'NewsArticle' || data['@type'] === 'BreadcrumbList') {
          script.remove();
        }
      } catch (e) {
        // If not JSON, keep it
      }
    });

    // Format dates properly
    const publishedDate = article.published_date || article.scraped_at;
    const modifiedDate = article.scraped_at;
    
    // Create comprehensive NewsArticle structured data
    const structuredData = {
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      "headline": article.title_pt || article.title,
      "description": description,
      "image": article.image_url ? [article.image_url] : [],
      "author": {
        "@type": "Organization",
        "name": article.source,
        "url": article.url
      },
      "publisher": {
        "@type": "Organization",
        "name": "TejoMag",
        "logo": {
          "@type": "ImageObject",
          "url": `${window.location.origin}/logo.png`,
          "width": 600,
          "height": 60
        }
      },
      "datePublished": publishedDate,
      "dateModified": modifiedDate,
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": articleUrl
      },
      "articleSection": article.category || "Geral",
      "inLanguage": "pt-PT",
      "keywords": [
        article.category,
        article.source,
        "notícias",
        "internacional",
        "português"
      ].filter(Boolean).join(", "),
      "wordCount": (article.content_pt || article.content).split(/\s+/).length,
      "url": articleUrl
    };

    // Add images if available
    if (article.images && Array.isArray(article.images) && article.images.length > 0) {
      structuredData.image = [article.image_url, ...article.images.slice(0, 3)].filter(Boolean);
    }

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(structuredData);
    document.head.appendChild(script);
  };

  const addBreadcrumbStructuredData = (article) => {
    const breadcrumbData = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Início",
          "item": window.location.origin
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": article.category || "Artigo",
          "item": `${window.location.origin}/?category=${encodeURIComponent(article.category || 'Geral')}`
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": article.title_pt || article.title,
          "item": window.location.href
        }
      ]
    };

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(breadcrumbData);
    document.head.appendChild(script);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Data não disponível';
    const date = new Date(dateString);
    return date.toLocaleString('pt-PT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Política': '#dc2626',
      'Economia': '#059669',
      'Tecnologia': '#7c3aed',
      'Saúde': '#0891b2',
      'Desporto': '#ea580c',
      'Cultura': '#be185d',
      'Guerra e Conflitos': '#b91c1c',
      'Ambiente': '#16a34a',
      'Direitos Humanos': '#9333ea',
      'Ciência': '#0ea5e9',
      'Geral': '#6b7280'
    };
    return colors[category] || '#6b7280';
  };

  const styles = {
    container: {
      maxWidth: '800px',
      margin: '0 auto',
      padding: '0 1rem'
    },
    breadcrumb: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginBottom: '2rem',
      fontSize: '0.9rem',
      color: '#6b7280'
    },
    breadcrumbLink: {
      color: '#3b82f6',
      textDecoration: 'none'
    },
    loading: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '3rem',
      fontSize: '1.2rem',
      color: '#6b7280'
    },
    error: {
      backgroundColor: '#fef2f2',
      border: '1px solid #fecaca',
      color: '#dc2626',
      padding: '2rem',
      borderRadius: '8px',
      textAlign: 'center'
    },
    article: {
      background: 'white',
      borderRadius: '12px',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden'
    },
    articleImage: {
      width: '100%',
      height: '400px',
      objectFit: 'cover'
    },
    articleContent: {
      padding: '3rem'
    },
    sourceBadge: {
      background: '#1f6cac',
      color: 'white',
      padding: '6px 16px',
      borderRadius: '20px',
      fontSize: '0.9rem',
      fontWeight: '600',
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
      display: 'inline-block',
      marginBottom: '1.5rem',
      boxShadow: '0 2px 8px rgba(31, 108, 172, 0.3)'
    },
    categoryBadge: {
      color: 'white',
      padding: '4px 12px',
      borderRadius: '16px',
      fontSize: '0.8rem',
      fontWeight: '600',
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
      display: 'inline-block',
      marginBottom: '1.5rem',
      marginLeft: '0.5rem'
    },
    articleTitle: {
      fontSize: '2.5rem',
      fontWeight: '700',
      lineHeight: '1.2',
      marginBottom: '1.5rem',
      color: '#1e293b'
    },
    articleMeta: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '2rem',
      paddingBottom: '1rem',
      borderBottom: '1px solid #e2e8f0',
      fontSize: '0.9rem',
      color: '#6b7280'
    },
    originalLink: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      backgroundColor: '#f8fafc',
      color: '#3b82f6',
      textDecoration: 'none',
      padding: '8px 16px',
      borderRadius: '6px',
      fontSize: '0.9rem',
      fontWeight: '500',
      border: '1px solid #e2e8f0',
      transition: 'all 0.2s ease'
    },
    articleBody: {
      fontSize: '1.1rem',
      lineHeight: '1.8',
      color: '#374151',
      marginBottom: '2rem'
    },
    originalTextSection: {
      backgroundColor: '#f8fafc',
      borderLeft: '4px solid #e2e8f0',
      padding: '2rem',
      marginTop: '2rem',
      borderRadius: '0 8px 8px 0'
    },
    originalTextTitle: {
      fontSize: '1.2rem',
      fontWeight: '600',
      color: '#6b7280',
      marginBottom: '1rem',
      textTransform: 'uppercase',
      letterSpacing: '0.5px'
    },
    originalText: {
      fontSize: '1rem',
      lineHeight: '1.7',
      color: '#6b7280'
    },
    controls: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '2rem',
      flexWrap: 'wrap',
      gap: '1rem'
    },
    toggleButton: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '10px 20px',
      border: 'none',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      backgroundColor: showOriginalText ? '#6b7280' : '#10b981',
      color: 'white'
    },
    backButton: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      color: '#3b82f6',
      textDecoration: 'none',
      fontSize: '1rem',
      fontWeight: '500'
    },
    shareSection: {
      marginTop: '3rem',
      padding: '2rem',
      backgroundColor: '#f8fafc',
      borderRadius: '8px',
      textAlign: 'center'
    },
    shareTitle: {
      fontSize: '1.2rem',
      fontWeight: '600',
      marginBottom: '1rem',
      color: '#1e293b'
    },
    shareButtons: {
      display: 'flex',
      justifyContent: 'center',
      gap: '1rem',
      flexWrap: 'wrap'
    },
    shareButton: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 16px',
      backgroundColor: '#3b82f6',
      color: 'white',
      textDecoration: 'none',
      borderRadius: '6px',
      fontSize: '0.9rem',
      fontWeight: '500'
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>
          <span>🔄</span>
          <span>Carregando artigo...</span>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div style={styles.container}>
        <div style={styles.breadcrumb}>
          <Link to="/" style={styles.breadcrumbLink}>Início</Link>
          <span>→</span>
          <span>Artigo não encontrado</span>
        </div>
        <div style={styles.error}>
          <h2>Artigo não encontrado</h2>
          <p>O artigo que você está procurando não foi encontrado.</p>
          <Link to="/" style={styles.backButton}>
            ← Voltar ao início
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Breadcrumb */}
      <div style={styles.breadcrumb}>
        <Link to="/" style={styles.breadcrumbLink}>Início</Link>
        <span>→</span>
        <span>Artigo</span>
      </div>

      {/* Article */}
      <article style={styles.article}>
        {article.image_url && (
          <img 
            src={article.image_url} 
            alt={article.title_pt || article.title}
            style={styles.articleImage}
            loading="eager"
            fetchPriority="high"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        )}
        
        <div style={styles.articleContent}>
          <div>
            <span style={styles.sourceBadge}>{article.source}</span>
            {article.category && (
              <span style={{
                ...styles.categoryBadge,
                backgroundColor: getCategoryColor(article.category),
                boxShadow: `0 2px 6px ${getCategoryColor(article.category)}40`
              }}>
                {article.category}
              </span>
            )}
          </div>
          
          <h1 style={styles.articleTitle}>
            {article.title_pt || article.title}
          </h1>
          
          <div style={styles.articleMeta}>
            <time dateTime={article.published_date || article.scraped_at}>
              Publicado em: {formatDate(article.published_date || article.scraped_at)}
            </time>
            <a 
              href={article.url} 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.originalLink}
              aria-label={`Ver artigo original em ${article.source}`}
            >
              <span>🔗</span>
              <span>Conteúdo original: {article.source}</span>
            </a>
          </div>

          {/* Controls */}
          <div style={styles.controls}>
            <Link to="/" style={styles.backButton}>
              ← Voltar às notícias
            </Link>
            
            <button 
              style={styles.toggleButton}
              onClick={() => setShowOriginalText(!showOriginalText)}
            >
              <span>{showOriginalText ? '👁️' : '🙈'}</span>
              {showOriginalText ? 'Ocultar Original' : 'Mostrar Original'}
            </button>
          </div>

          <div style={styles.articleBody} itemProp="articleBody">
            {article.content_pt || article.content}
          </div>

          {/* Original Text */}
          {showOriginalText && article.title !== article.title_pt && (
            <div style={styles.originalTextSection}>
              <h3 style={styles.originalTextTitle}>Título Original</h3>
              <p style={styles.originalText}>{article.title}</p>
            </div>
          )}

          {showOriginalText && article.content !== article.content_pt && (
            <div style={styles.originalTextSection}>
              <h3 style={styles.originalTextTitle}>Texto Original</h3>
              <p style={styles.originalText}>{article.content}</p>
            </div>
          )}

          {/* Share Section */}
          <div style={styles.shareSection}>
            <h3 style={styles.shareTitle}>Compartilhar este artigo</h3>
            <div style={styles.shareButtons}>
              <a 
                href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(article.title_pt || article.title)}&url=${encodeURIComponent(window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                style={styles.shareButton}
              >
                <span>🐦</span>
                <span>Twitter</span>
              </a>
              <a 
                href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                style={styles.shareButton}
              >
                <span>📘</span>
                <span>Facebook</span>
              </a>
              <a 
                href={`https://wa.me/?text=${encodeURIComponent(article.title_pt || article.title + ' ' + window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                style={styles.shareButton}
              >
                <span>💬</span>
                <span>WhatsApp</span>
              </a>
            </div>
          </div>
        </div>
      </article>
    </div>
  );
};

export default ArticleDetailPage;
