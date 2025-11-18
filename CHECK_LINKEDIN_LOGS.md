# How to Check LinkedIn Posting Logs

## Azure App Service Logs

LinkedIn posting logs are written to the backend application logs. Here's how to access them:

### Option 1: Azure Portal (Recommended)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your resource group: `tejomag-rg`
3. Click on your App Service: `tejomag-backend`
4. In the left menu, go to **"Log stream"** or **"Logs"**
5. You'll see real-time logs including:
   - `✅ Successfully posted to LinkedIn: [article title]...`
   - `❌ LinkedIn posting failed: [status code] - [error message]`
   - `📱 LinkedIn posting queued for: [article title]...`
   - `Error posting to LinkedIn: [error details]`

### Option 2: Kudu Console (Advanced)

1. Go to: `https://tejomag-backend.scm.azurewebsites.net`
2. Click on **"Debug console"** → **"CMD"**
3. Navigate to: `LogFiles/Application`
4. View the latest log files

### Option 3: Application Insights (If Enabled)

If Application Insights is enabled:
1. Go to Azure Portal → `tejomag-backend`
2. Click **"Application Insights"** in the left menu
3. Go to **"Logs"** and query:
   ```
   traces
   | where message contains "LinkedIn"
   | order by timestamp desc
   ```

## What to Look For

### Success Messages:
- `✅ Successfully posted to LinkedIn: [title]...`
- `📱 LinkedIn posting queued for: [title]...`

### Error Messages:
- `❌ LinkedIn posting failed: [status code] - [error]`
- `Error posting to LinkedIn: [exception]`
- `LinkedIn posting disabled - missing credentials`

## Common Issues

1. **Missing Credentials**: Check if all LinkedIn environment variables are set:
   - `LINKEDIN_CLIENT_ID`
   - `LINKEDIN_CLIENT_SECRET`
   - `LINKEDIN_ACCESS_TOKEN`
   - `LINKEDIN_PERSON_URN`

2. **Access Token Expired**: LinkedIn access tokens expire. You may need to refresh it.

3. **API Errors**: Check the status code in error messages:
   - `401`: Unauthorized (token expired/invalid)
   - `403`: Forbidden (permissions issue)
   - `429`: Rate limit exceeded

## Enable Detailed Logging

The backend already logs LinkedIn posting attempts. To see more details, check the logs right after a scheduled news job runs (every 30 minutes).

