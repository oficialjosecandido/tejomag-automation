# Sitemap Deployment Guide

## Current Issue
The sitemap at `https://tejomag.pt/sitemap.xml` returns 404 because the Azure Function isn't deployed yet.

## Solution: Deploy Azure Function

The Azure Function is configured but needs to be deployed. Here's what to do:

### 1. Verify Files Are Committed
All necessary files should be committed:
- ✅ `api/sitemap/__init__.py` - Function code
- ✅ `api/sitemap/function.json` - Function configuration
- ✅ `api/host.json` - Azure Functions host configuration
- ✅ `api/requirements.txt` - Python dependencies
- ✅ `.github/workflows/azure-deploy.yml` - Has `api_location: "api"`

### 2. Push and Deploy
```bash
git add .
git commit -m "Fix sitemap Azure Function deployment"
git push origin main
```

### 3. Wait for Deployment
- GitHub Actions will automatically deploy
- Check the Actions tab in your GitHub repo
- Wait 5-10 minutes for deployment to complete

### 4. Verify Deployment
After deployment, check:
1. **Azure Portal** → Static Web App → **Functions**
   - You should see `sitemap` function listed
2. **Test the function directly:**
   - `https://tejomag.pt/api/sitemap` (should return XML)
3. **Test the sitemap route:**
   - `https://tejomag.pt/sitemap.xml` (should return XML)

### 5. Submit to Google Search Console
Once `https://tejomag.pt/sitemap.xml` works:
1. Go to Google Search Console
2. Navigate to **Sitemaps**
3. Enter: `sitemap.xml` (just the path, not full URL)
4. Click **Submit**

## Troubleshooting

### If Azure Function Still Doesn't Work

**Option 1: Check Azure Portal**
- Go to Static Web App → Functions
- Check if function is listed
- Check function logs for errors

**Option 2: Verify API Location**
- Ensure `api_location: "api"` is in `.github/workflows/azure-deploy.yml`
- The `api` folder must be at the root of the repository

**Option 3: Check Function Logs**
- Azure Portal → Static Web App → Functions → `sitemap` → Logs
- Look for any errors

## Current Workaround

Until the Azure Function is deployed, you can:
- Use the backend sitemap directly: `https://tejomag-backend.azurewebsites.net/sitemap.xml`
- But Google Search Console requires it on the same domain, so this is temporary

