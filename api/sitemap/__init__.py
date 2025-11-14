import azure.functions as func
import requests
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Proxy sitemap from backend to frontend domain"""
    logging.info('Sitemap proxy function triggered')
    
    try:
        # Fetch sitemap from backend
        backend_url = "https://tejomag-backend.azurewebsites.net/sitemap.xml"
        response = requests.get(backend_url, timeout=10)
        
        if response.status_code == 200:
            # Return XML with proper headers
            return func.HttpResponse(
                response.text,
                status_code=200,
                mimetype="application/xml",
                headers={
                    "Content-Type": "application/xml; charset=utf-8",
                    "Access-Control-Allow-Origin": "*"
                }
            )
        else:
            logging.error(f"Backend returned status {response.status_code}")
            return func.HttpResponse(
                f"Error fetching sitemap: {response.status_code}",
                status_code=response.status_code
            )
    except Exception as e:
        logging.error(f"Error in sitemap proxy: {str(e)}")
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )

