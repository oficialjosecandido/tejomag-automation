# LinkedIn Credentials Setup Guide

This guide will help you get your **Access Token** and **Person URN** for LinkedIn API integration.

## Prerequisites

- Your LinkedIn App Client ID (from your LinkedIn Developer Portal)
- Your LinkedIn App Client Secret (from your LinkedIn Developer Portal)

**⚠️ Security Note:** Never commit your Client Secret to version control. Keep it in environment variables or a secure location.

## Step 1: Configure Redirect URI in LinkedIn App

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Select your app **TejoMag**
3. Go to **Auth** tab
4. Under **"Authorized redirect URLs for your app"**, add:
   ```
   http://localhost:8080/callback
   ```
5. **Save** the changes

## Step 2: Get Your Credentials

### Option A: Using the Python Script (Recommended)

1. **Run the helper script:**
   ```bash
   cd backend
   python get_linkedin_credentials.py
   ```

2. **The script will:**
   - Open your browser for LinkedIn authorization
   - Ask you to authorize the app
   - Automatically get your access token and Person URN
   - Display them for you to copy

### Option B: Manual Method (Using Browser)

#### Step 2.1: Get Authorization Code

1. **Build the authorization URL** (replace `YOUR_CLIENT_ID` and `YOUR_STATE`):
   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080/callback&state=YOUR_STATE&scope=w_member_social%20r_liteprofile%20r_basicprofile
   ```
   
   **Replace:**
   - `YOUR_CLIENT_ID` with your actual Client ID from LinkedIn Developer Portal
   - `YOUR_STATE` with any random string for security

2. **Open this URL in your browser** and authorize the app

3. **After authorization**, you'll be redirected to `http://localhost:8080/callback?code=AUTHORIZATION_CODE`

4. **Copy the `code` parameter** from the URL (the `AUTHORIZATION_CODE` part)

#### Step 2.2: Exchange Code for Access Token

Use curl or Postman to exchange the authorization code for an access token:

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTHORIZATION_CODE" \
  -d "redirect_uri=http://localhost:8080/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**Replace:**
- `YOUR_CLIENT_ID` with your actual Client ID from LinkedIn Developer Portal
- `YOUR_CLIENT_SECRET` with your actual Client Secret from LinkedIn Developer Portal

**Response will look like:**
```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "expires_in": 5184000
}
```

**Copy the `access_token` value.**

#### Step 2.3: Get Your Person URN

Use the access token to get your Person ID:

```bash
curl -X GET "https://api.linkedin.com/v2/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Restli-Protocol-Version: 2.0.0"
```

**Response will look like:**
```json
{
  "id": "YOUR_PERSON_ID",
  "firstName": {...},
  "lastName": {...},
  ...
}
```

**Your Person URN is:** `urn:li:person:YOUR_PERSON_ID`

## Step 3: Set Environment Variables

Add these to your Azure App Service environment variables or `.env` file:

```bash
LINKEDIN_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
LINKEDIN_PERSON_URN=YOUR_PERSON_ID
```

**Note:** 
- Use only the **Person ID** (not the full URN) for `LINKEDIN_PERSON_URN`
- The code will automatically format it as `urn:li:person:{id}`

## Step 4: Verify It Works

Test the LinkedIn posting endpoint:

```bash
curl -X POST https://tejomag-backend.azurewebsites.net/api/linkedin/post/1 \
  -H "Content-Type: application/json"
```

## Important Notes

⚠️ **Access Token Expiration:**
- Access tokens expire after **60 days** (2 months)
- You'll need to refresh it using the same process when it expires

⚠️ **Required Scopes:**
- `w_member_social` - Required for posting content
- `r_liteprofile` - Required to get profile info
- `r_basicprofile` - Required to get profile info

⚠️ **Security:**
- Never commit your access token or client secret to version control
- Keep them in environment variables only

## Troubleshooting

### "Invalid redirect_uri"
- Make sure you added `http://localhost:8080/callback` in your LinkedIn app's redirect URIs

### "Invalid client credentials"
- Double-check your Client ID and Client Secret
- Make sure there are no extra spaces

### "Insufficient permissions"
- Make sure you requested the correct scopes: `w_member_social`, `r_liteprofile`, `r_basicprofile`

### "Person URN not found"
- Make sure you're using the `id` field from the `/v2/me` response
- The format should be: `urn:li:person:{id}` (but store only the `{id}` part in env var)

## References

- [LinkedIn Profile API Documentation](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api)
- [LinkedIn OAuth 2.0 Documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)

