import React from 'react';
import { Link } from 'react-router-dom';

const TermosPage = () => {
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
    sectionTitle: {
      fontSize: '1.3rem',
      fontWeight: '600',
      color: '#1e293b',
      marginTop: '2rem',
      marginBottom: '1rem'
    },
    paragraph: {
      marginBottom: '1rem'
    },
    list: {
      paddingLeft: '2rem',
      marginBottom: '1rem'
    },
    listItem: {
      marginBottom: '0.5rem'
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
      transition: 'all 0.2s ease',
      marginTop: '2rem'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Termos e Condições</h1>
      </div>
      
      <div style={styles.content}>
        <p style={styles.paragraph}>Bem-vindo a TejoMag!</p>
        
        <p style={styles.paragraph}>
          Estes termos e condições descrevem as regras e regulamentos para o uso do site de TejoMag, 
          localizado em https://www.tejomag.com.
        </p>

        <p style={styles.paragraph}>
          Ao aceder a este site, presumimos que aceita estes termos e condições. Não continue a usar 
          TejoMag se não concordar com todos os termos e condições declarados nesta página.
        </p>

        <h2 style={styles.sectionTitle}>Cookies</h2>
        <p style={styles.paragraph}>
          O site usa cookies para ajudar a personalizar a sua experiência online. Ao aceder TejoMag, 
          concordou em usar os cookies necessários.
        </p>

        <h2 style={styles.sectionTitle}>Licença</h2>
        <p style={styles.paragraph}>
          Salvo indicação em contrário, TejoMag e/ou os seus licenciados possuem os direitos de 
          propriedade intelectual de todo o material em TejoMag. Todos os direitos de propriedade 
          intelectual são reservados.
        </p>

        <p style={styles.paragraph}>Não deve:</p>
        <ul style={styles.list}>
          <li style={styles.listItem}>Copiar ou republicar o material de TejoMag</li>
          <li style={styles.listItem}>Vender, alugar ou sublicenciar o material de TejoMag</li>
          <li style={styles.listItem}>Reproduzir, duplicar ou copiar o material de TejoMag</li>
          <li style={styles.listItem}>Redistribuir o conteúdo de TejoMag</li>
        </ul>

        <h2 style={styles.sectionTitle}>Responsabilidade pelo conteúdo</h2>
        <p style={styles.paragraph}>
          Não seremos responsabilizados por qualquer conteúdo que apareça no seu site. Concorda em 
          proteger-nos e defender contra todas as reclamações levantadas no seu site.
        </p>

        <h2 style={styles.sectionTitle}>Reserva de direitos</h2>
        <p style={styles.paragraph}>
          Reservamos o direito de solicitar que remova todos os links ou qualquer link específico para 
          o nosso site. Também nos reservamos o direito de alterar estes termos e condições e a sua 
          política de vinculação a qualquer momento.
        </p>

        <h2 style={styles.sectionTitle}>Isenção de responsabilidade</h2>
        <p style={styles.paragraph}>
          Na extensão máxima permitida pela lei aplicável, excluímos todas as representações, garantias 
          e condições relacionadas ao nosso site e ao uso deste site.
        </p>

        <p style={styles.paragraph}>
          Desde que o site e as informações e serviços nele fornecidos sejam gratuitos, não seremos 
          responsáveis por perdas ou danos de qualquer natureza.
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

export default TermosPage;

