# LinkedIn API Setup Guide

This guide explains how to set up automatic LinkedIn posting for TejoMag news articles.

## Prerequisites

1. A LinkedIn account
2. Access to LinkedIn Developer Portal
3. Azure App Service environment variables access

## Step 1: Create LinkedIn App

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Click "Create App"
3. Fill in the required information:
   - App name: `TejoMag News`
   - LinkedIn Page: (optional)
   - App logo: (optional)
   - Legal agreement: Check the box
4. Click "Create app"

## Step 2: Configure App Permissions

1. In your app dashboard, go to "Auth" tab
2. Add the following OAuth 2.0 scopes:
   - `w_member_social` - Write posts as the authenticated user
3. Add redirect URL: `https://your-domain.com/auth/linkedin/callback`

## Step 3: Get Your Credentials

1. In the "Auth" tab, you'll find:
   - **Client ID** - This is your `LINKEDIN_CLIENT_ID`
   - **Client Secret** - This is your `LINKEDIN_CLIENT_SECRET`

2. To get your **Person URN**:
   - Go to [LinkedIn Profile API](https://developer.linkedin.com/docs/guide/v2/people/profile-api)
   - Use the API endpoint: `GET /people/~`
   - Your URN will be in the format: `urn:li:person:ABC123DEF456`

## Step 4: Get Access Token

### Option A: Using LinkedIn Developer Tools (Recommended for testing)

1. In your LinkedIn app dashboard, go to "Auth" tab
2. Click "Generate a token"
3. Select the scopes you need (`w_member_social`)
4. Copy the generated token - this is your `LINKEDIN_ACCESS_TOKEN`

### Option B: Using OAuth Flow (For production)

1. Implement OAuth flow to get user authorization
2. Exchange authorization code for access token
3. Store the access token securely

## Step 5: Configure Environment Variables

Add these environment variables to your Azure App Service:

```bash
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_PERSON_URN=your_person_urn_here
```

### How to add environment variables in Azure:

1. Go to Azure Portal
2. Navigate to your App Service
3. Go to "Configuration" → "Application settings"
4. Add each variable as a new application setting
5. Save the configuration
6. Restart your App Service

## Step 6: Test the Integration

1. Check the health endpoint: `GET /api/health`
2. Look for `linkedin_enabled: true` in the response
3. Trigger a manual post: `POST /api/linkedin/post/{article_id}`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns LinkedIn integration status.

### Manual Post
```
POST /api/linkedin/post/{article_id}
```
Manually post a specific article to LinkedIn.

## Post Format

LinkedIn posts will include:
- Article title and content (in Portuguese)
- Source and category information
- Relevant hashtags based on category
- Link to original article
- TejoMag branding hashtags

## Troubleshooting

### Common Issues:

1. **"LinkedIn posting disabled"**
   - Check that all environment variables are set correctly
   - Verify the values are correct (no extra spaces, quotes, etc.)

2. **"LinkedIn posting failed: 401"**
   - Access token may be expired
   - Check token permissions include `w_member_social`

3. **"LinkedIn posting failed: 403"**
   - App may not have permission to post
   - Verify OAuth scopes are configured correctly

4. **"LinkedIn posting failed: 400"**
   - Post content may be too long
   - Check for invalid characters in post content

### Debug Mode:

Enable debug logging by checking the application logs in Azure App Service.

## Security Notes

- Never commit LinkedIn credentials to version control
- Use Azure Key Vault for production environments
- Regularly rotate access tokens
- Monitor API usage and rate limits

## Rate Limits

LinkedIn API has rate limits:
- 100 posts per day per user
- 1000 API calls per day per app

Monitor your usage to avoid hitting limits.
