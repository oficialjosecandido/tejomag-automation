#!/usr/bin/env python3
"""
Helper script to get Person URN from an existing LinkedIn Access Token
"""
import requests
import sys

def get_person_urn(access_token):
    """Get Person URN using an access token"""
    print(f"\n🔄 Getting Person URN with access token...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Try /v2/me with projection to get just the ID
    print("Trying GET /v2/me?projection=(id)...")
    response = requests.get('https://api.linkedin.com/v2/me?projection=(id)', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        person_id = data.get('id')
        if person_id:
            person_urn = f"urn:li:person:{person_id}"
            print(f"\n✅ Success!")
            print(f"Person ID: {person_id}")
            print(f"Person URN: {person_urn}")
            print(f"\n📋 Your LinkedIn Credentials:")
            print("=" * 60)
            print(f"Access Token: {access_token[:50]}...")
            print(f"Person URN: {person_urn}")
            print("=" * 60)
            return person_urn
        else:
            print(f"❌ No 'id' field in response: {data}")
            return None
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Response: {response.text}")
        print("\n💡 The access token might not have the right permissions.")
        print("   You may need to re-run get_linkedin_credentials.py with r_liteprofile scope.")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_person_urn.py <access_token>")
        print("\nOr paste your access token when prompted:")
        access_token = input("Paste your Access Token: ").strip()
    else:
        access_token = sys.argv[1]
    
    if not access_token:
        print("❌ No access token provided")
        sys.exit(1)
    
    get_person_urn(access_token)

