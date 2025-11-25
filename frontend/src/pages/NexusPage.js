import React, { useState, useEffect, useCallback } from 'react';
import config from '../config';

function NexusPage() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('');
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [articles, setArticles] = useState([]);
  const [pagination, setPagination] = useState({ current_page: 1, total_pages: 1, total_count: 0 });
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingArticle, setEditingArticle] = useState(null);
  const [formData, setFormData] = useState({
    title_pt: '',
    content_pt: '',
    title: '',
    content: '',
    source: 'Manual',
    category: 'Geral',
    image_url: '',
    images: [],
    url: ''
  });

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (authenticated) {
      fetchArticles();
    }
  }, [authenticated, fetchArticles]);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/admin/status`, {
        credentials: 'include'
      });
      const data = await response.json();
      setAuthenticated(data.authenticated);
      setUsername(data.username || '');
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(loginForm)
      });
      const data = await response.json();
      if (response.ok) {
        setAuthenticated(true);
        setUsername(data.username);
        setLoginForm({ username: '', password: '' });
      } else {
        alert(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please try again.');
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${config.API_BASE_URL}/api/admin/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      setAuthenticated(false);
      setUsername('');
      setArticles([]);
      setShowCreateForm(false);
      setEditingArticle(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const fetchArticles = useCallback(async () => {
    try {
      const response = await fetch(
        `${config.API_BASE_URL}/api/admin/articles?page=${pagination.current_page}&limit=20`,
        { credentials: 'include' }
      );
      if (response.ok) {
        const data = await response.json();
        setArticles(data.articles);
        setPagination(data.pagination);
      } else if (response.status === 401) {
        setAuthenticated(false);
      }
    } catch (error) {
      console.error('Fetch articles error:', error);
    }
  }, [pagination.current_page]);

  const handleCreateArticle = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/admin/articles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (response.ok) {
        alert('Article created successfully!');
        setShowCreateForm(false);
        setFormData({
          title_pt: '',
          content_pt: '',
          title: '',
          content: '',
          source: 'Manual',
          category: 'Geral',
          image_url: '',
          images: [],
          url: ''
        });
        fetchArticles();
      } else {
        alert(data.error || 'Failed to create article');
      }
    } catch (error) {
      console.error('Create article error:', error);
      alert('Failed to create article');
    }
  };

  const handleUpdateArticle = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/admin/articles/${editingArticle.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (response.ok) {
        alert('Article updated successfully!');
        setEditingArticle(null);
        setFormData({
          title_pt: '',
          content_pt: '',
          title: '',
          content: '',
          source: 'Manual',
          category: 'Geral',
          image_url: '',
          images: [],
          url: ''
        });
        fetchArticles();
      } else {
        alert(data.error || 'Failed to update article');
      }
    } catch (error) {
      console.error('Update article error:', error);
      alert('Failed to update article');
    }
  };

  const handleDeleteArticle = async (id) => {
    if (!window.confirm('Are you sure you want to delete this article?')) {
      return;
    }
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/admin/articles/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (response.ok) {
        alert('Article deleted successfully!');
        fetchArticles();
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to delete article');
      }
    } catch (error) {
      console.error('Delete article error:', error);
      alert('Failed to delete article');
    }
  };

  const startEdit = (article) => {
    setEditingArticle(article);
    setFormData({
      title_pt: article.title_pt || '',
      content_pt: article.content_pt || '',
      title: article.title || '',
      content: article.content || '',
      source: article.source || 'Manual',
      category: article.category || 'Geral',
      image_url: article.image_url || '',
      images: article.images || [],
      url: article.url || ''
    });
    setShowCreateForm(true);
  };

  const categories = ['Geral', 'Política', 'Economia', 'Tecnologia', 'Saúde', 'Desporto', 'Cultura', 'Guerra e Conflitos', 'Ambiente', 'Direitos Humanos', 'Ciência'];

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>;
  }

  if (!authenticated) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '2rem'
      }}>
        <div style={{
          background: 'white',
          padding: '3rem',
          borderRadius: '10px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
          maxWidth: '400px',
          width: '100%'
        }}>
          <h1 style={{ marginBottom: '2rem', color: '#333', textAlign: 'center' }}>🔐 Nexus Admin</h1>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                Username
              </label>
              <input
                type="text"
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #ddd',
                  borderRadius: '5px',
                  fontSize: '1rem'
                }}
              />
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                Password
              </label>
              <input
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #ddd',
                  borderRadius: '5px',
                  fontSize: '1rem'
                }}
              />
            </div>
            <button
              type="submit"
              style={{
                width: '100%',
                padding: '0.75rem',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'background 0.3s'
              }}
              onMouseOver={(e) => e.target.style.background = '#5568d3'}
              onMouseOut={(e) => e.target.style.background = '#667eea'}
            >
              Login
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <div style={{
        background: 'white',
        padding: '1.5rem 2rem',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1 style={{ margin: 0, color: '#333' }}>🔐 Nexus Admin Dashboard</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ color: '#666' }}>Welcome, {username}</span>
          <button
            onClick={handleLogout}
            style={{
              padding: '0.5rem 1rem',
              background: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '0 2rem' }}>
        <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, color: '#333' }}>Articles ({pagination.total_count})</h2>
          <button
            onClick={() => {
              setShowCreateForm(!showCreateForm);
              setEditingArticle(null);
              setFormData({
                title_pt: '',
                content_pt: '',
                title: '',
                content: '',
                source: 'Manual',
                category: 'Geral',
                image_url: '',
                images: [],
                url: ''
              });
            }}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            {showCreateForm ? 'Cancel' : '+ Create Article'}
          </button>
        </div>

        {showCreateForm && (
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '10px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            marginBottom: '2rem'
          }}>
            <h3 style={{ marginTop: 0, marginBottom: '1.5rem', color: '#333' }}>
              {editingArticle ? 'Edit Article' : 'Create New Article'}
            </h3>
            <form onSubmit={editingArticle ? handleUpdateArticle : handleCreateArticle}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                    Title (PT) *
                  </label>
                  <input
                    type="text"
                    value={formData.title_pt}
                    onChange={(e) => setFormData({ ...formData, title_pt: e.target.value })}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                    Title (Original)
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px'
                    }}
                  />
                </div>
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                  Content (PT) *
                </label>
                <textarea
                  value={formData.content_pt}
                  onChange={(e) => setFormData({ ...formData, content_pt: e.target.value })}
                  required
                  rows="10"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                  Content (Original)
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  rows="10"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                    Source
                  </label>
                  <input
                    type="text"
                    value={formData.source}
                    onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px'
                    }}
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                    Image URL
                  </label>
                  <input
                    type="url"
                    value={formData.image_url}
                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '5px'
                    }}
                  />
                </div>
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', color: '#666', fontWeight: '500' }}>
                  Original URL
                </label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #ddd',
                    borderRadius: '5px'
                  }}
                />
              </div>
              <button
                type="submit"
                style={{
                  padding: '0.75rem 2rem',
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                {editingArticle ? 'Update Article' : 'Create Article'}
              </button>
            </form>
          </div>
        )}

        <div style={{ background: 'white', borderRadius: '10px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#666', fontWeight: '600' }}>ID</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#666', fontWeight: '600' }}>Title (PT)</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#666', fontWeight: '600' }}>Source</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#666', fontWeight: '600' }}>Category</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#666', fontWeight: '600' }}>Date</th>
                <th style={{ padding: '1rem', textAlign: 'left', color: '#666', fontWeight: '600' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {articles.map(article => (
                <tr key={article.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: '1rem', color: '#666' }}>{article.id}</td>
                  <td style={{ padding: '1rem' }}>
                    <a
                      href={`/article/${article.slug}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: '#007bff', textDecoration: 'none' }}
                    >
                      {article.title_pt.substring(0, 50)}{article.title_pt.length > 50 ? '...' : ''}
                    </a>
                  </td>
                  <td style={{ padding: '1rem', color: '#666' }}>{article.source}</td>
                  <td style={{ padding: '1rem', color: '#666' }}>{article.category}</td>
                  <td style={{ padding: '1rem', color: '#666' }}>
                    {article.scraped_at ? new Date(article.scraped_at).toLocaleDateString() : '-'}
                  </td>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        onClick={() => startEdit(article)}
                        style={{
                          padding: '0.25rem 0.75rem',
                          background: '#ffc107',
                          color: '#333',
                          border: 'none',
                          borderRadius: '3px',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteArticle(article.id)}
                        style={{
                          padding: '0.25rem 0.75rem',
                          background: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '3px',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {pagination.total_pages > 1 && (
          <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
            <button
              onClick={() => setPagination({ ...pagination, current_page: pagination.current_page - 1 })}
              disabled={pagination.current_page === 1}
              style={{
                padding: '0.5rem 1rem',
                background: pagination.current_page === 1 ? '#ccc' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: pagination.current_page === 1 ? 'not-allowed' : 'pointer'
              }}
            >
              Previous
            </button>
            <span style={{ padding: '0.5rem 1rem', alignSelf: 'center', color: '#666' }}>
              Page {pagination.current_page} of {pagination.total_pages}
            </span>
            <button
              onClick={() => setPagination({ ...pagination, current_page: pagination.current_page + 1 })}
              disabled={pagination.current_page === pagination.total_pages}
              style={{
                padding: '0.5rem 1rem',
                background: pagination.current_page === pagination.total_pages ? '#ccc' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: pagination.current_page === pagination.total_pages ? 'not-allowed' : 'pointer'
              }}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default NexusPage;

