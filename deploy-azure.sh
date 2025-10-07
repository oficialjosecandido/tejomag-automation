#!/bin/bash
# Quick deployment script for Azure

set -e

echo "🚀 TejoMag - Azure Deployment Script"
echo "======================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install it first.${NC}"
    echo "Visit: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo -e "${BLUE}🔐 Logging into Azure...${NC}"
    az login
fi

# Variables
RESOURCE_GROUP="${RESOURCE_GROUP:-tejomag-rg}"
LOCATION="${LOCATION:-westeurope}"
BACKEND_APP="${BACKEND_APP:-tejomag-backend}"
FRONTEND_APP="${FRONTEND_APP:-tejomag-frontend}"
APP_PLAN="${APP_PLAN:-tejomag-plan}"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Backend App: $BACKEND_APP"
echo "  Frontend App: $FRONTEND_APP"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Create resource group
echo -e "${BLUE}📦 Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION || true

# Create App Service Plan
echo -e "${BLUE}📊 Creating App Service Plan...${NC}"
az appservice plan create \
  --name $APP_PLAN \
  --resource-group $RESOURCE_GROUP \
  --is-linux \
  --sku B1 || true

# Create Backend Web App
echo -e "${BLUE}🐍 Creating Backend Web App...${NC}"
az webapp create \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_PLAN \
  --runtime "PYTHON:3.11" || true

# Get DeepL API Key
read -p "Enter your DeepL API Key: " DEEPL_KEY

# Configure Backend
echo -e "${BLUE}⚙️  Configuring Backend...${NC}"
az webapp config appsettings set \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    DEEPL_API_KEY="$DEEPL_KEY" \
    FLASK_ENV="production" \
    FLASK_DEBUG="False" \
    LOG_LEVEL="INFO" \
    SCHEDULER_ENABLED="True" \
    WEBSITES_PORT="8000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Set startup command
az webapp config set \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --startup-file "startup.sh"

# Enable CORS
echo -e "${BLUE}🌐 Enabling CORS...${NC}"
az webapp cors add \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "*"

# Deploy Backend
echo -e "${BLUE}🚀 Deploying Backend...${NC}"
cd backend
zip -r deploy.zip . -x "*.pyc" -x "__pycache__/*" -x "*.db" -x "logs/*"
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --src deploy.zip
rm deploy.zip
cd ..

# Get backend URL
BACKEND_URL=$(az webapp show --name $BACKEND_APP --resource-group $RESOURCE_GROUP --query "defaultHostName" -o tsv)

echo -e "${GREEN}✅ Backend deployed successfully!${NC}"
echo -e "   URL: https://$BACKEND_URL"

# Create Static Web App
echo -e "${BLUE}🌐 Creating Static Web App...${NC}"
az staticwebapp create \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION || true

# Get frontend URL
FRONTEND_URL=$(az staticwebapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --query "defaultHostname" -o tsv)

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "======================================"
echo -e "Backend URL:  ${BLUE}https://$BACKEND_URL${NC}"
echo -e "Frontend URL: ${BLUE}https://$FRONTEND_URL${NC}"
echo ""
echo "Next steps:"
echo "1. Build and deploy frontend:"
echo "   cd frontend"
echo "   npm install && npm run build"
echo "   npx @azure/static-web-apps-cli deploy --app-location=build"
echo ""
echo "2. Test the backend:"
echo "   curl https://$BACKEND_URL/api/health"
echo ""
echo "3. Trigger news fetch:"
echo "   curl -X POST https://$BACKEND_URL/api/news/refresh"
echo ""
echo "View logs:"
echo "   az webapp log tail --name $BACKEND_APP --resource-group $RESOURCE_GROUP"

