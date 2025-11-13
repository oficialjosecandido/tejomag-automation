import React, { useEffect, useState } from 'react';
import axios from 'axios';
import config from '../config';

const SitemapPage = () => {
  const [sitemapXml, setSitemapXml] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSitemap = async () => {
      try {
        // Fetch sitemap from backend
        const response = await axios.get(`${config.API_BASE_URL}/sitemap.xml`, {
          headers: {
            'Accept': 'application/xml'
          }
        });
        setSitemapXml(response.data);
      } catch (error) {
        console.error('Error fetching sitemap:', error);
        setSitemapXml('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://tejomag.pt/</loc></url></urlset>');
      } finally {
        setLoading(false);
      }
    };

    fetchSitemap();
  }, []);

  // Return XML content
  useEffect(() => {
    if (!loading && sitemapXml) {
      // Set content type to XML
      document.contentType = 'application/xml';
    }
  }, [sitemapXml, loading]);

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Loading sitemap...</p>
      </div>
    );
  }

  // Return XML as plain text
  return (
    <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
      {sitemapXml}
    </pre>
  );
};

export default SitemapPage;

