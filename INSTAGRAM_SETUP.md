# Instagram Automatic Posting Setup

Instagram automatic posting is now integrated into TejoMag. Articles will be automatically posted to Instagram when:
- New articles are scraped from news sources
- Articles are manually created via the Nexus admin dashboard

## 📋 Prerequisites

1. **Facebook Page**: You need a Facebook Page (not a personal profile)
2. **Instagram Business Account**: Your Instagram account must be converted to a Business or Creator account
3. **Connection**: Your Instagram Business account must be connected to your Facebook Page
4. **Facebook App**: You need a Facebook App with Instagram Graph API permissions

## 🔧 Setup Steps

### Step 1: Create/Use a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or use an existing one
3. Add the **Instagram Graph API** product to your app

### Step 2: Get Facebook Page Access Token

1. In your Facebook App, go to **Tools** → **Graph API Explorer**
2. Select your app from the dropdown
3. Click **Generate Access Token**
4. Select the following permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
5. Copy the generated access token (this is your `INSTAGRAM_ACCESS_TOKEN`)

**Note**: For production, you should create a **Long-Lived Access Token**:
- Go to **Tools** → **Access Token Tool**
- Exchange your short-lived token for a long-lived one (60 days)
- For permanent tokens, set up a Page Access Token that doesn't expire

### Step 3: Get Instagram Business Account ID

1. Make sure your Instagram account is:
   - A Business or Creator account
   - Connected to your Facebook Page
2. Get your Facebook Page ID:
   - Go to your Facebook Page
   - Click **About** → Your Page ID is listed there
3. Use the Graph API to get your Instagram Business Account ID:
   ```
   GET https://graph.facebook.com/v18.0/{page-id}?fields=instagram_business_account&access_token={access-token}
   ```
4. The response will contain `instagram_business_account.id` - this is your `INSTAGRAM_BUSINESS_ACCOUNT_ID`

### Step 4: Set Environment Variables in Azure

Add these environment variables to your Azure App Service:

```bash
az webapp config appsettings set \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --settings INSTAGRAM_ACCESS_TOKEN="your-facebook-page-access-token" \
             INSTAGRAM_BUSINESS_ACCOUNT_ID="your-instagram-business-account-id"
```

Or via Azure Portal:
1. Go to `tejomag-backend` → **Configuration** → **Application settings**
2. Add:
   - **Name**: `INSTAGRAM_ACCESS_TOKEN`
     **Value**: Your Facebook Page Access Token
   - **Name**: `INSTAGRAM_BUSINESS_ACCOUNT_ID`
     **Value**: Your Instagram Business Account ID
3. Click **Save**

## 📸 How It Works

When a new article is created:
1. The system formats the article with:
   - Title and content in Portuguese
   - Article image (required for Instagram)
   - Hashtags based on category
   - Link to the TejoMag article
2. Creates an Instagram media container
3. Publishes the post to your Instagram account

## ⚠️ Important Notes

- **Images Required**: Instagram posts require an image. Articles without `image_url` will skip Instagram posting
- **Caption Length**: Instagram captions are limited to 2,200 characters. Content is automatically truncated if needed
- **Hashtags**: Up to 30 hashtags are included based on the article category
- **Links**: Instagram doesn't support clickable links in captions. The link is included in the caption with "Link na bio" (Link in bio)

## 🐛 Troubleshooting

### "Instagram posting disabled - missing credentials"
- Check that both `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_BUSINESS_ACCOUNT_ID` are set
- Verify the access token hasn't expired
- Restart the app after setting environment variables

### "No image URL available for Instagram post"
- Articles must have an `image_url` to be posted to Instagram
- Check that articles are being scraped with images

### "Instagram media creation failed"
- Verify your access token has the correct permissions
- Check that your Instagram account is a Business/Creator account
- Ensure the account is connected to your Facebook Page

### "Instagram publishing failed"
- The media container might not be ready yet (the system waits 2 seconds)
- Check Instagram API status
- Verify your account hasn't been restricted

## 🔗 Useful Links

- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api/)
- [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Tool](https://developers.facebook.com/tools/accesstoken/)

