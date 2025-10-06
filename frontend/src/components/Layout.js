import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Layout = ({ children }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  const styles = {
    app: {
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
      backgroundColor: '#f8fafc',
      color: '#1e293b',
      lineHeight: '1.6'
    },
    header: {
      background: '#1f6cac',
      color: 'white',
      padding: '1rem 0',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    },
    headerContent: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '0 1rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '1rem',
      flexWrap: 'wrap'
    },
    logo: {
      display: 'flex',
      alignItems: 'center',
      textDecoration: 'none',
      color: 'white',
      fontFamily: 'Arial, sans-serif',
      flex: '0 0 auto'
    },
    logoTitle: {
      fontSize: 'clamp(1.5rem, 5vw, 2.2rem)',
      fontWeight: '700',
      margin: '0',
      letterSpacing: '-0.5px'
    },
    searchContainer: {
      flex: '1 1 auto',
      maxWidth: '500px',
      minWidth: '200px'
    },
    searchForm: {
      position: 'relative',
      width: '100%'
    },
    searchInput: {
      width: '100%',
      padding: '0.75rem 3rem 0.75rem 1rem',
      borderRadius: '8px',
      border: 'none',
      fontSize: '1rem',
      outline: 'none',
      boxSizing: 'border-box'
    },
    searchButton: {
      position: 'absolute',
      right: '0.5rem',
      top: '50%',
      transform: 'translateY(-50%)',
      background: 'none',
      border: 'none',
      color: '#1f6cac',
      fontSize: '1.2rem',
      cursor: 'pointer',
      padding: '0.5rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    },
    nav: {
      display: 'flex',
      gap: '1rem',
      alignItems: 'center',
      flex: '0 0 auto'
    },
    navLink: {
      color: 'white',
      textDecoration: 'none',
      fontSize: '1rem',
      fontWeight: '500',
      padding: '0.5rem 1rem',
      borderRadius: '6px',
      transition: 'background-color 0.2s ease',
      whiteSpace: 'nowrap'
    },
    main: {
      flex: '1',
      maxWidth: '1200px',
      margin: '0 auto',
      padding: 'clamp(1rem, 3vw, 2rem)',
      width: '100%',
      boxSizing: 'border-box'
    },
    footer: {
      background: '#1e293b',
      color: '#94a3b8',
      textAlign: 'center',
      padding: '2rem 1rem',
      marginTop: 'auto'
    },
    footerContent: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '0 1rem'
    },
    footerText: {
      margin: '0.5rem 0',
      fontSize: 'clamp(0.8rem, 2vw, 1rem)'
    },
    footerLinks: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '0.75rem',
      marginBottom: '1rem',
      flexWrap: 'wrap'
    },
    footerLink: {
      color: '#94a3b8',
      textDecoration: 'none',
      fontSize: 'clamp(0.8rem, 2vw, 0.9rem)',
      transition: 'color 0.2s ease'
    },
    footerSeparator: {
      color: '#64748b',
      fontSize: '0.8rem'
    },
    mobileSearchContainer: {
      flex: '1 1 100%',
      width: '100%',
      marginTop: '0.5rem',
      display: 'none'
    }
  };

  // Media query for mobile
  const isMobile = window.innerWidth < 768;
  if (isMobile) {
    styles.headerContent.flexDirection = 'column';
    styles.headerContent.alignItems = 'stretch';
    styles.searchContainer.maxWidth = '100%';
    styles.nav.justifyContent = 'center';
  }

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <Link to="/" style={styles.logo}>
            <h1 style={styles.logoTitle}>TejoMag</h1>
          </Link>
          
          <div style={styles.searchContainer}>
            <form onSubmit={handleSearch} style={styles.searchForm}>
              <input
                type="text"
                placeholder="Pesquisar notícias..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={styles.searchInput}
              />
              <button type="submit" style={styles.searchButton} aria-label="Pesquisar">
                🔍
              </button>
            </form>
          </div>
        </div>
      </header>

      <main style={styles.main}>
        {children}
      </main>

      <footer style={styles.footer}>
        <div style={styles.footerContent}>
          <div style={styles.footerLinks}>
            <Link 
              to="/quem-somos" 
              style={styles.footerLink}
              onMouseEnter={(e) => e.target.style.color = '#fff'}
              onMouseLeave={(e) => e.target.style.color = '#94a3b8'}
            >
              Quem somos
            </Link>
            <span style={styles.footerSeparator}>•</span>
            <Link 
              to="/ficha-tecnica" 
              style={styles.footerLink}
              onMouseEnter={(e) => e.target.style.color = '#fff'}
              onMouseLeave={(e) => e.target.style.color = '#94a3b8'}
            >
              Ficha Técnica
            </Link>
            <span style={styles.footerSeparator}>•</span>
            <Link 
              to="/termos" 
              style={styles.footerLink}
              onMouseEnter={(e) => e.target.style.color = '#fff'}
              onMouseLeave={(e) => e.target.style.color = '#94a3b8'}
            >
              Termos e Condições
            </Link>
          </div>
          <p style={styles.footerText}>&copy; 2024 TejoMag - Notícias internacionais traduzidas para português</p>
          <p style={{...styles.footerText, fontSize: 'clamp(0.7rem, 1.5vw, 0.8rem)', marginTop: '0.5rem', opacity: '0.7'}}>
            Conectando o mundo através das notícias em português
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
