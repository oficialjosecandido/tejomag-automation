import React from 'react';
import { Link } from 'react-router-dom';

const FichaTecnicaPage = () => {
  const styles = {
    container: {
      maxWidth: '800px',
      margin: '0 auto',
      padding: '2rem 1rem'
    },
    header: {
      marginBottom: '2rem',
      paddingBottom: '1rem',
      borderBottom: '3px solid #1f6cac'
    },
    title: {
      fontSize: 'clamp(2rem, 5vw, 3rem)',
      fontWeight: '700',
      color: '#1e293b',
      marginBottom: '1rem'
    },
    content: {
      fontSize: '1rem',
      lineHeight: '1.8',
      color: '#374151',
      marginBottom: '2rem'
    },
    infoSection: {
      marginBottom: '1.5rem'
    },
    label: {
      fontWeight: '600',
      color: '#1e293b',
      display: 'inline-block',
      minWidth: '150px'
    },
    value: {
      color: '#374151'
    },
    backButton: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      color: '#1f6cac',
      textDecoration: 'none',
      fontSize: '1rem',
      fontWeight: '500',
      padding: '0.75rem 1.5rem',
      backgroundColor: '#f0f9ff',
      borderRadius: '8px',
      transition: 'all 0.2s ease'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Ficha Técnica</h1>
      </div>
      
      <div style={styles.content}>
        <div style={styles.infoSection}>
          <span style={styles.label}>Proprietário:</span>
          <span style={styles.value}> José Vicente Cândido</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Diretor:</span>
          <span style={styles.value}> José Cândido</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Redação:</span>
          <span style={styles.value}> Tomás Cascão e Sérgio Aleluia</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Colaboradores:</span>
          <span style={styles.value}> Rita Costa, Carolina Piedade, Francisca Ribeiro e Miguel Penhalta</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Imagem:</span>
          <span style={styles.value}> Joana Brito, Richard Borg, Jimmy Bégue</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Título da Publicação:</span>
          <span style={styles.value}> TejoMag</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Registo ERC:</span>
          <span style={styles.value}> nº 127918</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Sede da Editora:</span>
          <span style={styles.value}> Rua da Fontaínha 7, 2640-019 Santo Isidoro</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Sede da Redação:</span>
          <span style={styles.value}> Rua da Fontaínha 7, 2640-019 Santo Isidoro</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Publicação:</span>
          <span style={styles.value}> online</span>
        </div>

        <div style={styles.infoSection}>
          <span style={styles.label}>Periodicidade:</span>
          <span style={styles.value}> dias úteis</span>
        </div>
      </div>

      <Link 
        to="/" 
        style={styles.backButton}
        onMouseEnter={(e) => e.target.style.backgroundColor = '#dbeafe'}
        onMouseLeave={(e) => e.target.style.backgroundColor = '#f0f9ff'}
      >
        ← Voltar ao início
      </Link>
    </div>
  );
};

export default FichaTecnicaPage;

