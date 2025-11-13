import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPolicyPage = () => {
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
    lastUpdated: {
      fontSize: '0.9rem',
      color: '#6b7280',
      fontStyle: 'italic',
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
        <h1 style={styles.title}>Política de Privacidade</h1>
        <p style={styles.lastUpdated}>Última atualização: {new Date().toLocaleDateString('pt-PT', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>
      
      <div style={styles.content}>
        <p style={styles.paragraph}>
          A TejoMag ("nós", "nosso" ou "nos") está comprometida em proteger a sua privacidade. 
          Esta Política de Privacidade explica como recolhemos, utilizamos, divulgamos e protegemos 
          as suas informações quando utiliza o nosso site https://tejomag.pt (o "Serviço").
        </p>

        <p style={styles.paragraph}>
          Ao utilizar o nosso Serviço, concorda com a recolha e utilização de informações de acordo 
          com esta política. Se não concordar com a nossa política, não utilize o nosso Serviço.
        </p>

        <h2 style={styles.sectionTitle}>1. Informações que Recolhemos</h2>
        <p style={styles.paragraph}>
          Recolhemos diferentes tipos de informações para melhorar e fornecer o nosso Serviço:
        </p>
        <ul style={styles.list}>
          <li style={styles.listItem}>
            <strong>Dados de Utilização:</strong> Informações sobre como acede e utiliza o nosso 
            Serviço, incluindo endereços IP, tipo de navegador, páginas visitadas, tempo de visita 
            e outras estatísticas.
          </li>
          <li style={styles.listItem}>
            <strong>Cookies e Tecnologias Similares:</strong> Utilizamos cookies e tecnologias 
            similares para rastrear a atividade no nosso Serviço e armazenar certas informações.
          </li>
        </ul>

        <h2 style={styles.sectionTitle}>2. Como Utilizamos as Suas Informações</h2>
        <p style={styles.paragraph}>Utilizamos as informações recolhidas para:</p>
        <ul style={styles.list}>
          <li style={styles.listItem}>Fornecer, manter e melhorar o nosso Serviço</li>
          <li style={styles.listItem}>Analisar como o nosso Serviço é utilizado</li>
          <li style={styles.listItem}>Detetar, prevenir e resolver problemas técnicos</li>
          <li style={styles.listItem}>Personalizar a sua experiência de navegação</li>
        </ul>

        <h2 style={styles.sectionTitle}>3. Cookies</h2>
        <p style={styles.paragraph}>
          Utilizamos cookies para melhorar a sua experiência no nosso site. Os cookies são pequenos 
          ficheiros de texto que são colocados no seu dispositivo quando visita um website.
        </p>
        <p style={styles.paragraph}>
          Pode instruir o seu navegador a recusar todos os cookies ou a indicar quando um cookie está 
          a ser enviado. No entanto, se não aceitar cookies, pode não conseguir utilizar algumas partes 
          do nosso Serviço.
        </p>

        <h2 style={styles.sectionTitle}>4. Partilha de Informações</h2>
        <p style={styles.paragraph}>
          Não vendemos, comercializamos ou transferimos as suas informações pessoais para terceiros. 
          Podemos partilhar informações agregadas e anonimizadas que não identifiquem pessoalmente 
          os utilizadores.
        </p>
        <p style={styles.paragraph}>
          Podemos divulgar as suas informações pessoais se acreditarmos de boa fé que tal divulgação 
          é necessária para:
        </p>
        <ul style={styles.list}>
          <li style={styles.listItem}>Cumprir uma obrigação legal</li>
          <li style={styles.listItem}>Proteger e defender os direitos ou propriedade da TejoMag</li>
          <li style={styles.listItem}>Prevenir ou investigar possíveis irregularidades relacionadas 
          com o Serviço</li>
          <li style={styles.listItem}>Proteger a segurança pessoal dos utilizadores do Serviço ou 
          do público</li>
        </ul>

        <h2 style={styles.sectionTitle}>5. Segurança dos Dados</h2>
        <p style={styles.paragraph}>
          A segurança dos seus dados é importante para nós, mas lembre-se de que nenhum método de 
          transmissão pela Internet ou método de armazenamento eletrónico é 100% seguro. Embora 
          nos esforcemos para utilizar meios comercialmente aceitáveis para proteger as suas 
          informações pessoais, não podemos garantir a sua segurança absoluta.
        </p>

        <h2 style={styles.sectionTitle}>6. Links para Outros Sites</h2>
        <p style={styles.paragraph}>
          O nosso Serviço pode conter links para outros sites que não são operados por nós. Se 
          clicar num link de terceiros, será direcionado para o site desse terceiro. Recomendamos 
          vivamente que reveja a Política de Privacidade de cada site que visita.
        </p>
        <p style={styles.paragraph}>
          Não temos controlo e não assumimos responsabilidade pelo conteúdo, políticas de privacidade 
          ou práticas de quaisquer sites ou serviços de terceiros.
        </p>

        <h2 style={styles.sectionTitle}>7. Os Seus Direitos</h2>
        <p style={styles.paragraph}>
          De acordo com o Regulamento Geral sobre a Proteção de Dados (RGPD), tem os seguintes direitos:
        </p>
        <ul style={styles.list}>
          <li style={styles.listItem}>
            <strong>Direito de Acesso:</strong> Pode solicitar cópias das suas informações pessoais
          </li>
          <li style={styles.listItem}>
            <strong>Direito de Retificação:</strong> Pode solicitar que corrijamos qualquer informação 
            que considere imprecisa
          </li>
          <li style={styles.listItem}>
            <strong>Direito ao Apagamento:</strong> Pode solicitar que apaguemos as suas informações 
            pessoais, em certas circunstâncias
          </li>
          <li style={styles.listItem}>
            <strong>Direito de Oposição:</strong> Pode opor-se ao nosso processamento das suas 
            informações pessoais
          </li>
          <li style={styles.listItem}>
            <strong>Direito à Portabilidade:</strong> Pode solicitar a transferência das suas 
            informações para outro serviço
          </li>
        </ul>

        <h2 style={styles.sectionTitle}>8. Privacidade de Menores</h2>
        <p style={styles.paragraph}>
          O nosso Serviço não se dirige a menores de 18 anos. Não recolhemos conscientemente 
          informações pessoais identificáveis de menores de 18 anos. Se descobrirmos que um menor 
          de 18 anos nos forneceu informações pessoais, apagaremos imediatamente essas informações 
          dos nossos servidores.
        </p>

        <h2 style={styles.sectionTitle}>9. Alterações a Esta Política de Privacidade</h2>
        <p style={styles.paragraph}>
          Podemos atualizar a nossa Política de Privacidade periodicamente. Notificaremos sobre 
          quaisquer alterações publicando a nova Política de Privacidade nesta página e atualizando 
          a data de "Última atualização" no topo desta Política de Privacidade.
        </p>
        <p style={styles.paragraph}>
          Recomendamos que reveja esta Política de Privacidade periodicamente para quaisquer 
          alterações. As alterações a esta Política de Privacidade entram em vigor quando são 
          publicadas nesta página.
        </p>

        <h2 style={styles.sectionTitle}>10. Contacto</h2>
        <p style={styles.paragraph}>
          Se tiver questões sobre esta Política de Privacidade, pode contactar-nos através do 
          nosso site em https://tejomag.pt.
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

export default PrivacyPolicyPage;

