# Azure Web App Deployment Guide for H&M Data Assistant

## 🚨 Unicode Symbol Issues

### Problem:
Unicode symbols (🚀, ✅, ❌, 🤖) may not display correctly in:
- Azure App Service console logs
- Application Insights logs  
- Windows Server environments
- Some terminal emulators

### Solutions:

#### 1. Environment Variable Control
Set in Azure Portal → Configuration → Application Settings:
```
USE_UNICODE=false
```
This will automatically switch to ASCII symbols:
- 🚀 → [INIT]
- ✅ → [OK]  
- ❌ → [ERROR]
- 🤖 → [BOT]
- 🤔 → [PROCESSING]

#### 2. Command Line Override
Force ASCII mode:
```bash
python app.py --no-unicode
```

#### 3. Auto-Detection
The app automatically detects Azure environment and disables Unicode:
- Checks for `WEBSITE_SITE_NAME` (Azure App Service)
- Checks for `APPSVC_RUN_ZIP` (Azure App Service)
- Checks Windows Server environment

## 📋 Deployment Checklist

### Azure App Service Configuration:
```
# Required Environment Variables
OPENAI_API_KEY=your-openai-key
GCP_PROJECT_ID=your-gcp-project  
BQ_DATASET=your-dataset
BQ_TABLES=incidents,problems

# Production Settings
USE_UNICODE=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Performance Settings  
MAX_QUERY_LENGTH=500
TIMEOUT_SECONDS=30
```

### Startup Command:
```bash
python app.py
```

## 🧪 Testing Deployment

### Test locally with production settings:
```bash
export USE_UNICODE=false
export ENVIRONMENT=production
python app.py --examples
```

### Verify ASCII output:
```
[INIT] Initializing H&M Data Assistant...
[OK] Assistant ready!
[APP] H&M Data Assistant - Interactive Mode
[USER] You: Hi there!
[BOT] Assistant: Hello! I'm your H&M data assistant...
```

## 📊 Monitoring in Azure

### Application Insights Logs:
- All messages logged with timestamps
- Error messages include full stack traces
- Search for "[ERROR]" to find issues
- Unicode symbols replaced with readable tags

### App Service Logs:
- Stream logs in Azure Portal
- Download logs for analysis
- ASCII symbols ensure readability

## 🔧 Troubleshooting

### If Unicode still appears in logs:
1. Check `USE_UNICODE` environment variable
2. Restart the App Service
3. Use `python app.py --no-unicode` as startup command

### If symbols show as `?` or `[]`:
1. This is expected in some environments
2. Functionality remains intact
3. Consider switching to ASCII mode

## ✅ Production-Ready Features

- ✅ Auto-detects Azure environment
- ✅ Falls back to ASCII symbols
- ✅ Proper error logging
- ✅ Environment variable control
- ✅ Manual override options
- ✅ Maintains functionality in all environments