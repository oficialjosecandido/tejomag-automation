# 🚀 Azure Deployment Guide - TejoMag

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│           Azure Static Web Apps             │
│         (React Frontend - Port 80)          │
└─────────────────┬───────────────────────────┘
                  │
                  │ API Calls
                  │
┌─────────────────▼───────────────────────────┐
│          Azure App Service                  │
│       (Python Backend - Port 8000)          │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Gunicorn + Flask                    │  │
│  │  SQLite Database                     │  │
│  │  Background Scheduler                │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## Prerequisites

- Azure account ([Get free trial](https://azure.microsoft.com/free/))
- Azure CLI installed
- Git repository
- DeepL API key

---

## Part 1: Deploy Backend (Python App Service)

### Step 1: Create Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name tejomag-rg --location westeurope

# Create App Service Plan (Linux, Python)
az appservice plan create \
  --name tejomag-plan \
  --resource-group tejomag-rg \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --plan tejomag-plan \
  --runtime "PYTHON:3.11"
```

### Step 2: Configure App Settings

```bash
# Set environment variables
az webapp config appsettings set \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --settings \
    DEEPL_API_KEY="your-deepl-api-key" \
    FLASK_ENV="production" \
    FLASK_DEBUG="False" \
    LOG_LEVEL="INFO" \
    SCHEDULER_ENABLED="True" \
    WEBSITES_PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

### Step 3: Deploy Backend

```bash
# From project root
cd backend

# Deploy using Git
git init
az webapp deployment source config-local-git \
  --name tejomag-backend \
  --resource-group tejomag-rg

# Get deployment credentials
az webapp deployment list-publishing-credentials \
  --name tejomag-backend \
  --resource-group tejomag-rg

# Add Azure remote and push
git remote add azure <YOUR_GIT_URL>
git add .
git commit -m "Initial backend deployment"
git push azure main
```

**OR deploy using ZIP:**

```bash
# Create deployment package
cd backend
zip -r deploy.zip . -x "*.pyc" -x "__pycache__/*" -x "*.db"

# Deploy
az webapp deployment source config-zip \
  --resource-group tejomag-rg \
  --name tejomag-backend \
  --src deploy.zip
```

### Step 4: Configure Startup Command

```bash
az webapp config set \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --startup-file "startup.sh"
```

---

## Part 2: Deploy Frontend (Static Web App)

### Step 1: Create Static Web App

```bash
# Create Static Web App
az staticwebapp create \
  --name tejomag-frontend \
  --resource-group tejomag-rg \
  --location westeurope
```

### Step 2: Configure Frontend Environment

Create `frontend/.env.production`:

```env
REACT_APP_API_URL=https://tejomag-backend.azurewebsites.net
```

### Step 3: Build and Deploy

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Deploy using Azure Static Web Apps CLI
npx @azure/static-web-apps-cli deploy \
  --app-location="build" \
  --resource-group="tejomag-rg" \
  --app-name="tejomag-frontend"
```

**OR use GitHub Actions** (Recommended):

Azure Static Web Apps automatically creates a GitHub Actions workflow.

---

## Part 3: Configure CORS

```bash
# Allow frontend domain to access backend
az webapp cors add \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --allowed-origins "https://tejomag-frontend.azurestaticapps.net" "*"
```

---

## Part 4: Custom Domain (Optional)

### Backend Custom Domain

```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name tejomag-backend \
  --resource-group tejomag-rg \
  --hostname api.tejomag.com

# Enable HTTPS
az webapp config set \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --https-only true
```

### Frontend Custom Domain

```bash
# Add custom domain to Static Web App
az staticwebapp hostname set \
  --name tejomag-frontend \
  --resource-group tejomag-rg \
  --hostname www.tejomag.com
```

---

## Part 5: Enable Application Insights (Monitoring)

```bash
# Create Application Insights
az monitor app-insights component create \
  --app tejomag-insights \
  --resource-group tejomag-rg \
  --location westeurope

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app tejomag-insights \
  --resource-group tejomag-rg \
  --query instrumentationKey -o tsv)

# Configure backend to use App Insights
az webapp config appsettings set \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY"
```

---

## Part 6: Setup Continuous Deployment

### Using GitHub Actions

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r ../requirements.txt
      
      - name: Deploy to Azure
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'tejomag-backend'
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          package: backend

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Build
        run: |
          cd frontend
          npm install
          npm run build
      
      - name: Deploy to Static Web App
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          app_location: "frontend"
          output_location: "build"
```

---

## Part 7: Database Persistence

### Option A: Keep SQLite (Simple)

Azure App Service includes ephemeral storage. For persistent SQLite:

```bash
# Mount persistent storage
az webapp config storage-account add \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --custom-id database \
  --storage-type AzureBlob \
  --account-name <storage-account-name> \
  --share-name tejomag-data \
  --access-key <access-key> \
  --mount-path /home/data
```

### Option B: Upgrade to Azure SQL (Recommended for Production)

See separate guide: `AZURE_SQL_MIGRATION.md`

---

## Environment Variables Reference

### Backend (App Service)

| Variable | Value | Description |
|----------|-------|-------------|
| `DEEPL_API_KEY` | Your key | DeepL translation API key |
| `FLASK_ENV` | production | Flask environment |
| `FLASK_DEBUG` | False | Debug mode |
| `LOG_LEVEL` | INFO | Logging level |
| `SCHEDULER_ENABLED` | True | Enable news scheduler |
| `WEBSITES_PORT` | 8000 | Port for App Service |
| `DATABASE_PATH` | /home/data/news.db | Database location |

---

## Monitoring & Logs

### View Application Logs

```bash
# Stream logs
az webapp log tail \
  --name tejomag-backend \
  --resource-group tejomag-rg

# Download logs
az webapp log download \
  --name tejomag-backend \
  --resource-group tejomag-rg \
  --log-file logs.zip
```

### Application Insights Queries

```
# Failed requests
requests
| where success == false
| summarize count() by resultCode

# Response times
requests
| summarize avg(duration) by bin(timestamp, 5m)

# News scraping errors
traces
| where message contains "scraping"
| where severityLevel >= 3
```

---

## Costs Estimate (EUR/month)

| Service | Tier | Cost |
|---------|------|------|
| App Service Plan | B1 Basic | ~€13 |
| Static Web App | Free | €0 |
| Application Insights | Basic | ~€2 |
| Storage Account | Standard | ~€1 |
| **Total** | | **~€16/month** |

---

## Troubleshooting

### Backend not starting?

```bash
# Check logs
az webapp log tail --name tejomag-backend --resource-group tejomag-rg

# Check startup command
az webapp config show --name tejomag-backend --resource-group tejomag-rg --query "appCommandLine"

# Restart app
az webapp restart --name tejomag-backend --resource-group tejomag-rg
```

### CORS errors?

```bash
# Check CORS settings
az webapp cors show --name tejomag-backend --resource-group tejomag-rg

# Update CORS
az webapp cors add --name tejomag-backend --resource-group tejomag-rg --allowed-origins "*"
```

### Database issues?

```bash
# SSH into container
az webapp ssh --name tejomag-backend --resource-group tejomag-rg

# Check database file
ls -la /home/data/news.db
```

---

## Quick Deployment Checklist

- [ ] Azure account created
- [ ] Resource group created
- [ ] App Service created
- [ ] Backend deployed
- [ ] Environment variables configured
- [ ] Static Web App created
- [ ] Frontend built and deployed
- [ ] CORS configured
- [ ] Custom domain configured (optional)
- [ ] Application Insights enabled
- [ ] GitHub Actions configured
- [ ] First news fetch triggered
- [ ] Monitoring setup complete

---

## Useful Commands

```bash
# Check app status
az webapp show --name tejomag-backend --resource-group tejomag-rg --query "state"

# Get app URL
az webapp show --name tejomag-backend --resource-group tejomag-rg --query "defaultHostName" -o tsv

# Scale up/down
az appservice plan update --name tejomag-plan --resource-group tejomag-rg --sku B2

# Stop/Start app
az webapp stop --name tejomag-backend --resource-group tejomag-rg
az webapp start --name tejomag-backend --resource-group tejomag-rg
```

---

## Next Steps

1. Deploy using this guide
2. Test the deployment
3. Configure monitoring alerts
4. Set up automated backups
5. Implement CI/CD pipeline

---

**Need help?** Check Azure Documentation:
- [App Service Python](https://learn.microsoft.com/azure/app-service/quickstart-python)
- [Static Web Apps](https://learn.microsoft.com/azure/static-web-apps/)
- [Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)

