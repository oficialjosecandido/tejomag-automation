import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import QuemSomosPage from './pages/QuemSomosPage';
import FichaTecnicaPage from './pages/FichaTecnicaPage';
import TermosPage from './pages/TermosPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import SitemapPage from './pages/SitemapPage';
import Layout from './components/Layout';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/sitemap.xml" element={<SitemapPage />} />
        <Route path="/" element={<Layout><HomePage /></Layout>} />
        <Route path="/article/:slug" element={<Layout><ArticleDetailPage /></Layout>} />
        <Route path="/quem-somos" element={<Layout><QuemSomosPage /></Layout>} />
        <Route path="/ficha-tecnica" element={<Layout><FichaTecnicaPage /></Layout>} />
        <Route path="/termos" element={<Layout><TermosPage /></Layout>} />
        <Route path="/privacidade" element={<Layout><PrivacyPolicyPage /></Layout>} />
      </Routes>
    </Router>
  );
}

export default App;