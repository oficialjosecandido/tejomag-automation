import React from 'react';
import { Link } from 'react-router-dom';

const Layout = ({ children }) => {
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
      padding: '1.5rem 0',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    },
    headerContent: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '0 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    },
    logo: {
      display: 'flex',
      alignItems: 'center',
      gap: '0',
      textDecoration: 'none',
      color: 'white',
      fontFamily: 'Arial, sans-serif'
    },
    logoTitle: {
      fontSize: '2.2rem',
      fontWeight: '700',
      margin: '0',
      letterSpacing: '-0.5px'
    },
    tagline: {
      fontSize: '0.9rem',
      opacity: '0.9',
      margin: '0',
      display: 'none'
    },
    nav: {
      display: 'flex',
      gap: '2rem',
      alignItems: 'center'
    },
    navLink: {
      color: 'white',
      textDecoration: 'none',
      fontSize: '1rem',
      fontWeight: '500',
      padding: '0.5rem 1rem',
      borderRadius: '6px',
      transition: 'background-color 0.2s ease'
    },
    main: {
      flex: '1',
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '2rem',
      width: '100%'
    },
    footer: {
      background: '#1e293b',
      color: '#94a3b8',
      textAlign: 'center',
      padding: '2rem 0',
      marginTop: 'auto'
    },
    footerContent: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '0 2rem'
    }
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <Link to="/" style={styles.logo}>
            <h1 style={styles.logoTitle}>TejoMag</h1>
          </Link>
          
          <nav style={styles.nav}>
            <Link to="/" style={styles.navLink}>Início</Link>
            <Link to="/" style={styles.navLink}>Últimas Notícias</Link>
          </nav>
        </div>
      </header>

      <main style={styles.main}>
        {children}
      </main>

      <footer style={styles.footer}>
        <div style={styles.footerContent}>
          <p>&copy; 2024 TejoMag - Notícias internacionais traduzidas para português</p>
          <p style={{ fontSize: '0.8rem', marginTop: '0.5rem', opacity: '0.7' }}>
            Conectando o mundo através das notícias em português
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
