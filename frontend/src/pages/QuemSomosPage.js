import React from 'react';
import { Link } from 'react-router-dom';

const QuemSomosPage = () => {
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
      fontSize: '1.1rem',
      lineHeight: '1.8',
      color: '#374151',
      marginBottom: '2rem'
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
        <h1 style={styles.title}>Quem somos</h1>
      </div>
      
      <div style={styles.content}>
        <p>
          Somos uma publicação periódica eletrónica. Pretendemos focar-nos na análise das transformações emergentes. 
          Trabalhamos com uma equipa de jornalistas, no sentido de garantir uma abordagem plural, isenta e rigorosa.
        </p>
        <p>
          Ao sair da espuma dos acontecimentos, trazemos para o domínio público a análise da atualidade através de 
          reportagens de fundo. Informamos para além das margens do rio e do pensamento.
        </p>
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

export default QuemSomosPage;

