import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from '../config';

const SitemapPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSitemap = async () => {
      try {
        const response = await axios.get(`${config.API_BASE_URL}/sitemap.xml`, {
          responseType: 'text',
          headers: {
            'Accept': 'application/xml'
          }
        });
        
        // Replace entire document with XML
        document.open('text/xml');
        document.write(response.data);
        document.close();
      } catch (error) {
        console.error('Error fetching sitemap:', error);
        // Redirect to home on error
        navigate('/');
      }
    };

    fetchSitemap();
  }, [navigate]);

  // Return minimal content while loading
  return (
    <div style={{ display: 'none' }}>
      Loading sitemap...
    </div>
  );
};

export default SitemapPage;

