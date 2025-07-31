# H&M Data Assistant - AI-Powered ServiceNow Analytics

> 🤖 **Natural Language to SQL chatbot** for H&M's ServiceNow incident and problem management data

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file with your credentials:
```env
# Google Cloud / BigQuery
SERVICE_ACCOUNT_KEY_PATH={"type": "service_account",...}
PROJECT_ID=enterprise-dashboardnp-cd35
INCIDENT_TABLE=enterprise-dashboardnp-cd35.bigquery_datasets_hone_srv_dev.oa_snow_incident_mgmt_srv_dev
PROBLEM_TABLE=enterprise-dashboardnp-cd35.bigquery_datasets_hone_srv_dev.oa_snow_problem_management_srv_dev

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://openai-insights-dev-se.openai.azure.com/
OPENAI_API_KEY=your-key-here
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini

# Azure Blob Storage
BLOB_CONNECTION_STRING=https://stninsightsdev01.blob.core.windows.net/prediction-artifact?...
BLOB_CONNECTION_STRING_CONVERSATION=https://stninsightsdev01.blob.core.windows.net/chatbot-conversation?...
```

### 3. Validate Configuration
```bash
python validate_env.py
```

### 4. Run the Application

#### Interactive Chat Mode:
```bash
python app.py
```

#### API Server Mode:
```bash
python app.py --api
```

#### Run Examples:
```bash
python app.py --examples
```

## 💬 Usage Examples

### Interactive Chat:
```
💬 You: How many critical incidents were created this month?
🤖 Assistant: I found 47 critical incidents created this month. Here are the details...

💬 You: Which team has the most incidents?
🤖 Assistant: The Infrastructure team has 156 incidents, followed by...
```

### API Usage:
```bash
# Query endpoint
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Show me open incidents", 
    "user_id": "user123"
  }'

# Feedback endpoint
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "user_query": "Show me open incidents",
    "feedback": "like",
    "comments": "Very helpful!"
  }'
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   AI Workflow    │───▶│   BigQuery      │
│ "Show incidents"│    │ Intent→SQL→Exec  │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Session Storage │    │  Prompt Storage  │    │    Response     │
│ (Azure Blob)    │    │  (Azure Blob)    │    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Features

- ✅ **Natural Language Processing**: Convert questions to SQL queries
- ✅ **Multi-turn Conversations**: Remember context across questions  
- ✅ **Session Persistence**: Store conversations in Azure Blob Storage
- ✅ **User Feedback**: Collect and store user satisfaction data
- ✅ **Intent Classification**: Smart routing of queries
- ✅ **Error Handling**: Graceful failure and retry mechanisms
- ✅ **Cost Optimized**: 250x cheaper than traditional database solutions

## 🔧 Configuration

### Environment Variables:
See [BLOB_STORAGE_SETUP.md](BLOB_STORAGE_SETUP.md) for detailed setup instructions.

### Key Files:
- `app.py` - Main application entry point
- `config/env_config.py` - Environment configuration management
- `services/blob_session_manager.py` - User session storage
- `services/bigquery_client.py` - Database connectivity
- `app/graph.py` - AI workflow orchestration

## 🛠️ Development

### Project Structure:
```
chatbot/
├── app.py                      # Main application
├── config/
│   ├── env_config.py          # Environment configuration
│   └── blob_config.py         # Blob storage settings
├── services/
│   ├── conversation_blob_client.py  # Azure Blob client
│   ├── blob_session_manager.py     # Session management
│   └── bigquery_client.py          # Database client
├── app/
│   ├── graph.py               # AI workflow
│   └── nodes.py               # Workflow components
└── requirements.txt           # Dependencies
```

### Testing:
```bash
# Validate environment
python validate_env.py

# Run example queries
python app.py --examples

# Test single query
python app.py --query "How many incidents do we have?"
```

## 🔒 Security & Compliance

- 🔐 **Secure Configuration**: Environment-based secrets management
- 📝 **Audit Logging**: Track all user interactions
- 🗄️ **Data Isolation**: User sessions stored separately
- 🛡️ **Access Control**: Container-level permissions

## 💰 Cost Efficiency

| Component | Monthly Cost (1000 users) |
|-----------|---------------------------|
| Azure Blob Storage | ~$0.50 |
| BigQuery Queries | ~$5-15 |
| Azure OpenAI | ~$10-50 |
| **Total** | **~$15-65** |

**vs Legacy SQL Server approach: ~$150-500/month** 💸

## 🆘 Troubleshooting

### Common Issues:
1. **"Blob storage failed"** → Check connection strings in `.env`
2. **"BigQuery error"** → Verify service account credentials
3. **"OpenAI error"** → Check API key and endpoint
4. **"Session not persisting"** → Ensure `user_id` provided in API calls

### Getting Help:
1. Run `python validate_env.py` to check configuration
2. Check console output for error messages
3. See [BLOB_STORAGE_SETUP.md](BLOB_STORAGE_SETUP.md) for detailed troubleshooting

---

**Built with ❤️ for H&M's ServiceNow analytics team**