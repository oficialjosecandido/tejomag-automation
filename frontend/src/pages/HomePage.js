import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const HomePage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/news');
      setArticles(response.data.articles || []);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('Erro ao carregar as notícias. Verifique se o servidor está rodando.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

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
    hero: {
      background: '#1f6cac',
      color: 'white',
      padding: '4rem 0',
      textAlign: 'center',
      marginBottom: '3rem',
      borderRadius: '12px'
    },
    heroTitle: {
      fontSize: '3rem',
      fontWeight: '700',
      marginBottom: '1rem',
      margin: '0 0 1rem 0',
      fontFamily: 'Arial, sans-serif',
      letterSpacing: '-0.5px'
    },
    heroSubtitle: {
      fontSize: '1.5rem',
      opacity: '0.95',
      marginBottom: '3rem',
      maxWidth: '700px',
      margin: '0 auto 3rem auto',
      fontWeight: '300',
      letterSpacing: '0.5px'
    },
    heroFeatures: {
      display: 'flex',
      justifyContent: 'center',
      gap: '3rem',
      flexWrap: 'wrap',
      marginTop: '2rem',
      padding: '0 2rem'
    },
    feature: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      fontSize: '1.1rem',
      opacity: '0.95',
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
      padding: '1rem 1.5rem',
      borderRadius: '8px',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      transition: 'all 0.3s ease'
    },
    error: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '1rem',
      backgroundColor: '#fef2f2',
      border: '1px solid #fecaca',
      color: '#dc2626',
      padding: '16px',
      borderRadius: '8px'
    },
    loading: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px',
      fontSize: '18px',
      color: '#6b7280'
    },
    noArticles: {
      textAlign: 'center',
      padding: '3rem',
      color: '#6b7280',
      fontSize: '1.1rem'
    },
    articlesGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
      gap: '2rem',
      marginTop: '2rem'
    },
    articleCard: {
      background: 'white',
      borderRadius: '16px',
      boxShadow: '0 8px 25px -8px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden',
      transition: 'all 0.3s ease',
      textDecoration: 'none',
      color: 'inherit',
      display: 'block',
      border: '1px solid rgba(31, 108, 172, 0.1)'
    },
    articleImage: {
      width: '100%',
      height: '200px',
      objectFit: 'cover'
    },
    articleContent: {
      padding: '1.5rem'
    },
    sourceBadge: {
      background: '#1f6cac',
      color: 'white',
      padding: '6px 16px',
      borderRadius: '20px',
      fontSize: '0.8rem',
      fontWeight: '700',
      textTransform: 'uppercase',
      letterSpacing: '0.8px',
      display: 'inline-block',
      marginBottom: '1rem',
      boxShadow: '0 2px 8px rgba(31, 108, 172, 0.3)'
    },
    categoryBadge: {
      padding: '4px 12px',
      borderRadius: '16px',
      fontSize: '0.7rem',
      fontWeight: '600',
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
      display: 'inline-block',
      marginBottom: '1rem',
      marginLeft: '0.5rem',
      color: 'white'
    },
    articleTitle: {
      fontSize: '1.3rem',
      fontWeight: '700',
      lineHeight: '1.3',
      marginBottom: '1rem',
      color: '#1e293b'
    },
    articleExcerpt: {
      color: '#4b5563',
      lineHeight: '1.6',
      fontSize: '0.95rem',
      marginBottom: '1rem',
      display: '-webkit-box',
      WebkitLineClamp: '3',
      WebkitBoxOrient: 'vertical',
      overflow: 'hidden'
    },
    articleMeta: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: '0.8rem',
      color: '#9ca3af'
    },
    readMore: {
      color: '#1f6cac',
      fontWeight: '700',
      textDecoration: 'none',
      fontSize: '0.9rem'
    },
  };

  return (
    <div>
      {/* Hero Section */}
      <div style={styles.hero}>
        <h1 style={styles.heroTitle}>TejoMag</h1>
        <p style={styles.heroSubtitle}>
          Informação além das margens
        </p>
        <div style={styles.heroFeatures}>
          <div style={styles.feature}>
            <span>🌍</span>
            <span>Notícias Internacionais</span>
          </div>
          <div style={styles.feature}>
            <span>🇵🇹</span>
            <span>Traduzido para Português</span>
          </div>
          <div style={styles.feature}>
            <span>⚡</span>
            <span>Atualizações em Tempo Real</span>
          </div>
        </div>
      </div>



      {/* Error Message */}
      {error && (
        <div style={styles.error}>
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading && articles.length === 0 && (
        <div style={styles.loading}>
          <span>🔄</span>
          <span>Carregando notícias...</span>
        </div>
      )}

      {/* No Articles */}
      {!loading && !error && articles.length === 0 && (
        <div style={styles.noArticles}>
          <p>Nenhuma notícia encontrada. Tente atualizar a página.</p>
        </div>
      )}

      {/* Articles Grid */}
      <div style={styles.articlesGrid}>
        {articles.map((article) => (
          <Link 
            key={article.id} 
            to={`/article/${article.id}`}
            style={styles.articleCard}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-8px)';
              e.target.style.boxShadow = '0 20px 40px -12px rgba(31, 108, 172, 0.15)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 8px 25px -8px rgba(0, 0, 0, 0.1)';
            }}
          >
            {article.image_url && (
              <img 
                src={article.image_url} 
                alt={article.title_pt || article.title}
                style={styles.articleImage}
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
              
              <h2 style={styles.articleTitle}>
                {article.title_pt || article.title}
              </h2>
              
              <p style={styles.articleExcerpt}>
                {article.content_pt || article.content}
              </p>
              
              <div style={styles.articleMeta}>
                <span>{formatDate(article.scraped_at)}</span>
                <span style={styles.readMore}>Ler mais →</span>
              </div>
            </div>
          </Link>
        ))}
      </div>

    </div>
  );
};

export default HomePage;
