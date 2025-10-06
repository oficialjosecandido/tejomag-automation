import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import QuemSomosPage from './pages/QuemSomosPage';
import FichaTecnicaPage from './pages/FichaTecnicaPage';
import TermosPage from './pages/TermosPage';
import Layout from './components/Layout';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/article/:slug" element={<ArticleDetailPage />} />
          <Route path="/quem-somos" element={<QuemSomosPage />} />
          <Route path="/ficha-tecnica" element={<FichaTecnicaPage />} />
          <Route path="/termos" element={<TermosPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;