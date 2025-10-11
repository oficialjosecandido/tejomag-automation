import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import config from '../config';

const HomePage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [pagination, setPagination] = useState(null);
  const location = useLocation();

  const fetchNews = async (page = 1, append = false) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }
    setError(null);
    
    try {
      const response = await axios.get(`${config.API_BASE_URL}/api/news?page=${page}&limit=50`);
      const newArticles = response.data.articles || [];
      
      if (append) {
        setArticles(prev => [...prev, ...newArticles]);
      } else {
        setArticles(newArticles);
        setSearchQuery('');
      }
      
      setPagination(response.data.pagination);
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('Erro ao carregar as notícias. Verifique se o servidor está rodando.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const loadMore = () => {
    if (pagination && pagination.has_next) {
      fetchNews(pagination.current_page + 1, true);
    }
  };

  const searchNews = async (query) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${config.API_BASE_URL}/api/news/search?q=${encodeURIComponent(query)}`);
      setArticles(response.data.articles || []);
      setSearchQuery(query);
    } catch (err) {
      console.error('Error searching news:', err);
      setError('Erro ao pesquisar notícias.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Check if there's a search query in URL
    const params = new URLSearchParams(location.search);
    const query = params.get('search');
    
    if (query) {
      searchNews(query);
    } else {
      fetchNews();
    }
  }, [location.search]);

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
      gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 350px), 1fr))',
      gap: 'clamp(1rem, 3vw, 2rem)',
      marginTop: '2rem'
    },
    searchHeader: {
      marginBottom: '2rem',
      padding: '1rem',
      backgroundColor: '#e0f2fe',
      borderRadius: '8px',
      borderLeft: '4px solid #1f6cac'
    },
    searchHeaderText: {
      margin: 0,
      color: '#1e293b',
      fontSize: 'clamp(1rem, 2.5vw, 1.2rem)'
    },
    clearSearchButton: {
      marginTop: '0.5rem',
      padding: '0.5rem 1rem',
      backgroundColor: '#1f6cac',
      color: 'white',
      border: 'none',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '0.9rem',
      fontWeight: '500'
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
    loadMoreButton: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      margin: '3rem auto',
      padding: '1rem 2rem',
      backgroundColor: '#1f6cac',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      cursor: 'pointer',
      fontSize: '1rem',
      fontWeight: '600',
      transition: 'all 0.3s ease',
      maxWidth: '200px'
    },
    loadMoreButtonDisabled: {
      backgroundColor: '#9ca3af',
      cursor: 'not-allowed'
    },
    paginationInfo: {
      textAlign: 'center',
      marginTop: '2rem',
      color: '#6b7280',
      fontSize: '0.9rem'
    },
  };

  return (
    <div>
      {/* Search Results Header */}
      {searchQuery && (
        <div style={styles.searchHeader}>
          <h2 style={styles.searchHeaderText}>
            {articles.length > 0 
              ? `Encontrados ${articles.length} resultado${articles.length !== 1 ? 's' : ''} para "${searchQuery}"`
              : `Nenhum resultado encontrado para "${searchQuery}"`
            }
          </h2>
          <button 
            style={styles.clearSearchButton}
            onClick={fetchNews}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#1557a0'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#1f6cac'}
          >
            ← Ver todas as notícias
          </button>
        </div>
      )}

      {/* Hero Section */}
      {!searchQuery && (
        <div style={styles.hero}>
          <h1 style={styles.heroTitle}>TejoMag</h1>
          <p style={styles.heroSubtitle}>
            Informação além das margens
          </p>
        </div>
      )}

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
      {!loading && !error && articles.length === 0 && !searchQuery && (
        <div style={styles.noArticles}>
          <p>Nenhuma notícia encontrada. Tente atualizar a página.</p>
        </div>
      )}

      {/* Articles Grid */}
      <div style={styles.articlesGrid}>
        {articles.map((article) => (
          <Link 
            key={article.id} 
            to={`/article/${article.slug || article.id}`}
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

      {/* Load More Button */}
      {!searchQuery && pagination && pagination.has_next && (
        <div style={{ textAlign: 'center' }}>
          <button
            style={{
              ...styles.loadMoreButton,
              ...(loadingMore ? styles.loadMoreButtonDisabled : {})
            }}
            onClick={loadMore}
            disabled={loadingMore}
            onMouseEnter={(e) => {
              if (!loadingMore) {
                e.target.style.backgroundColor = '#1557a0';
              }
            }}
            onMouseLeave={(e) => {
              if (!loadingMore) {
                e.target.style.backgroundColor = '#1f6cac';
              }
            }}
          >
            {loadingMore ? (
              <>
                <span>🔄</span>
                <span>Carregando...</span>
              </>
            ) : (
              <>
                <span>📄</span>
                <span>Carregar mais notícias</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Pagination Info */}
      {!searchQuery && pagination && (
        <div style={styles.paginationInfo}>
          Mostrando {articles.length} de {pagination.total_count} notícias
          {pagination.total_pages > 1 && (
            <span> • Página {pagination.current_page} de {pagination.total_pages}</span>
          )}
        </div>
      )}

    </div>
  );
};

export default HomePage;
