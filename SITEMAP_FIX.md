# Sitemap 404 Fix

The sitemap is returning 404 because the Azure Function might not be deployed yet. Here are the solutions:

## Quick Fix: Direct Backend Access

For now, you can access the sitemap directly from the backend:
- **Backend sitemap**: `https://tejomag-backend.azurewebsites.net/sitemap.xml` ✅ (This works)

## Why the Frontend Sitemap Returns 404

The Azure Function at `/api/sitemap` needs to be deployed. After the next deployment with `api_location: "api"` in the workflow, it should work.

## Verify Azure Function Deployment

1. Go to Azure Portal → Your Static Web App
2. Check **"Functions"** in the left menu
3. You should see the `sitemap` function listed
4. If it's not there, the function hasn't been deployed yet

## Temporary Workaround

Update `frontend/public/robots.txt` to point directly to the backend:
```
Sitemap: https://tejomag-backend.azurewebsites.net/sitemap.xml
```

Or wait for the next deployment to include the Azure Function.

## After Next Deployment

Once deployed, the sitemap should be accessible at:
- `https://tejomag.pt/sitemap.xml`
- `https://www.tejomag.pt/sitemap.xml`

The route works as: `/sitemap.xml` → `/api/sitemap` → Azure Function → Backend sitemap

