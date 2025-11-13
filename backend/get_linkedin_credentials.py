#!/usr/bin/env python3
"""
Helper script to get LinkedIn Access Token and Person URN

This script helps you:
1. Get an OAuth 2.0 access token
2. Get your Person URN from the LinkedIn API

Usage:
    python get_linkedin_credentials.py
"""

import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import os
import getpass

# Your LinkedIn App Credentials
# Get from environment variables or prompt user
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')

# If not in environment, prompt user
if not CLIENT_ID:
    CLIENT_ID = input("Enter your LinkedIn Client ID: ").strip()
if not CLIENT_SECRET:
    CLIENT_SECRET = getpass.getpass("Enter your LinkedIn Client Secret: ").strip()

# OAuth 2.0 Configuration
REDIRECT_URI = "http://localhost:8080/callback"
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Required scopes for posting
SCOPES = [
    "w_member_social",  # Required for posting
    "r_liteprofile",    # Required to get profile info
    "r_basicprofile"    # Required to get profile info
]

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback"""
    auth_code = None
    
    def do_GET(self):
        """Handle GET request from LinkedIn callback"""
        if self.path.startswith('/callback'):
            # Parse the authorization code from the callback
            query_params = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query_params)
            
            if 'code' in params:
                self.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                    <head><title>Authorization Successful</title></head>
                    <body>
                        <h1>Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                        <script>window.close();</script>
                    </body>
                    </html>
                """)
            elif 'error' in params:
                error = params['error'][0]
                error_description = params.get('error_description', ['Unknown error'])[0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"""
                    <html>
                    <head><title>Authorization Failed</title></head>
                    <body>
                        <h1>Authorization Failed</h1>
                        <p>Error: {error}</p>
                        <p>Description: {error_description}</p>
                    </body>
                    </html>
                """.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass

def get_access_token(auth_code):
    """Exchange authorization code for access token"""
    print("\n🔄 Exchanging authorization code for access token...")
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(TOKEN_URL, data=token_data)
    
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info.get('access_token')
        expires_in = token_info.get('expires_in', 0)
        print(f"✅ Access token obtained! (expires in {expires_in} seconds)")
        return access_token
    else:
        print(f"❌ Failed to get access token: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_person_urn(access_token):
    """Get Person URN from LinkedIn API"""
    print("\n🔄 Getting your Person URN from LinkedIn...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Get current user's profile
    response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        person_id = profile.get('id')
        
        if person_id:
            person_urn = f"urn:li:person:{person_id}"
            print(f"✅ Person URN obtained!")
            print(f"\n📋 Your LinkedIn Credentials:")
            print(f"=" * 60)
            print(f"Person ID: {person_id}")
            print(f"Person URN: {person_urn}")
            print(f"=" * 60)
            return person_urn, person_id
        else:
            print("❌ Could not find 'id' in profile response")
            print(f"Response: {profile}")
            return None, None
    else:
        print(f"❌ Failed to get profile: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None

def main():
    """Main function to get LinkedIn credentials"""
    print("=" * 60)
    print("LinkedIn Credentials Helper")
    print("=" * 60)
    print("\nThis script will help you get:")
    print("1. LinkedIn Access Token")
    print("2. Your Person URN")
    
    # Validate credentials
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n❌ Error: Client ID and Client Secret are required!")
        print("   Set them as environment variables:")
        print("   export LINKEDIN_CLIENT_ID='your_client_id'")
        print("   export LINKEDIN_CLIENT_SECRET='your_client_secret'")
        print("\n   Or enter them when prompted.")
        return
    
    print(f"\n✅ Using Client ID: {CLIENT_ID[:10]}...")
    print("\n⚠️  Make sure you have configured the redirect URI in your LinkedIn app:")
    print(f"   {REDIRECT_URI}")
    print("\nPress Enter to continue...")
    input()
    
    # Step 1: Start local server for callback
    print("\n🌐 Starting local server for OAuth callback...")
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("✅ Local server started on http://localhost:8080")
    
    # Step 2: Build authorization URL
    scope_string = " ".join(SCOPES)
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': 'random_state_string',
        'scope': scope_string
    }
    
    auth_url = f"{AUTHORIZATION_URL}?{urllib.parse.urlencode(auth_params)}"
    
    print("\n🔗 Opening browser for LinkedIn authorization...")
    print(f"   If browser doesn't open, visit: {auth_url}")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Step 3: Wait for callback
    print("\n⏳ Waiting for authorization...")
    print("   Please authorize the app in your browser.")
    
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while CallbackHandler.auth_code is None:
        if time.time() - start_time > timeout:
            print("\n❌ Timeout waiting for authorization")
            server.shutdown()
            return
        
        time.sleep(1)
    
    auth_code = CallbackHandler.auth_code
    server.shutdown()
    print("✅ Authorization code received!")
    
    # Step 4: Get access token
    access_token = get_access_token(auth_code)
    if not access_token:
        return
    
    # Step 5: Get Person URN
    person_urn, person_id = get_person_urn(access_token)
    if not person_urn:
        return
    
    # Step 6: Display results
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Here are your credentials:")
    print("=" * 60)
    print(f"\n🔑 Access Token:")
    print(f"   {access_token}")
    print(f"\n👤 Person URN (full format):")
    print(f"   {person_urn}")
    print(f"\n📝 Person ID (use this in env var):")
    print(f"   {person_id}")
    print("\n" + "=" * 60)
    print("\n📋 Add these to your environment variables:")
    print("=" * 60)
    print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    print(f"LINKEDIN_PERSON_URN={person_id}")
    print("\n⚠️  Important:")
    print("   - Store only the Person ID (not the full URN) in LINKEDIN_PERSON_URN")
    print("   - The code will automatically format it as: urn:li:person:{id}")
    print("   - Access tokens expire after 60 days (2 months)")
    print("   - You'll need to refresh it using the same process when it expires")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

