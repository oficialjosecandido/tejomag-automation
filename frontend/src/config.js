// Configuration for API endpoints
const config = {
  // Use Azure backend URL in production, localhost in development
  // Updated for custom domain tejomag.pt
  API_BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://tejomag-backend.azurewebsites.net' 
    : 'http://localhost:5000'
};

export default config;
