# Azure Blob Storage Setup for User Sessions

## 🗄️ Container Structure

Your Azure Storage Account should have these containers:

```
Azure Storage Account: stninsightsdev01
├── prediction-artifact (existing - for schemas/prompts)
│   ├── classify_intent.txt
│   ├── general_response.txt
│   ├── generate_sql.txt
│   └── incident_schemas.txt
└── chatbot-conversation (for user sessions)
    ├── user123/
    │   ├── conversations.json
    │   ├── feedback.json
    │   └── metadata.json
    ├── user456/
    │   ├── conversations.json
    │   └── feedback.json
    └── analytics/ (optional)
        └── usage-stats.json
```

## 🔧 Azure Portal Setup

### 1. Create User Sessions Container:
```bash
# Using Azure CLI
az storage container create \
  --name user-sessions \
  --account-name your-storage-account \
  --account-key your-account-key
```

### 2. Set Container Permissions:
- **Access Level**: Private (blob access only)
- **Lifecycle Management**: Optional (auto-delete after 90 days)

### 3. Environment Variables:
```env
# Add to your .env file
BLOB_CONNECTION_STRING="https://stninsightsdev01.blob.core.windows.net/prediction-artifact?sp=racwdli&st=2025-05-13T08:29:41Z&se=2026-05-13T16:29:41Z&spr=https&sv=2024-11-04&sr=c&sig=tUX9050p4E1YSSK%2F8a9iTZJNkNsAjOUPl%2F9fi8h2h8o%3D"
BLOB_CONNECTION_STRING_CONVERSATION="https://stninsightsdev01.blob.core.windows.net/chatbot-conversation?sp=racwli&st=2025-05-13T19:45:39Z&se=2026-05-14T03:45:39Z&spr=https&sv=2024-11-04&sr=c&sig=qXQtX7ZddtM85rdlafJ8iSLQkAx9G0X%2FnWvrT7N6uEc%3D"
USER_SESSION_CONTAINER=chatbot-conversation
```

## 📁 File Formats

### conversations.json:
```json
{
  "user_id": "user123",
  "last_updated": "2025-01-15T10:30:00Z",
  "history": [
    {
      "user": "Show me critical incidents",
      "bot": "Here are 5 critical incidents...",
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ],
  "detailed_data": [
    {
      "user_query": "Show me critical incidents",
      "sql_query": "SELECT * FROM incidents WHERE priority='1'",
      "response": "Here are 5 critical incidents...",
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### feedback.json:
```json
{
  "user_id": "user123",
  "last_updated": "2025-01-15T10:35:00Z",
  "feedback_entries": [
    {
      "query": "Show me critical incidents", 
      "feedback": "like",
      "comments": "Very helpful response",
      "timestamp": "2025-01-15T10:35:00Z"
    }
  ]
}
```

## 🚀 Usage

### Start with Blob Storage:
```bash
python app.py --api
```

### Start without Blob Storage (memory only):
```python
assistant = DataAssistant(use_blob_sessions=False)
```

### Test Session Storage:
```bash
# Test API endpoints
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Hi there", "user_id": "test123"}'

curl -X POST http://localhost:5000/finish \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123"}'
```

## 💰 Cost Comparison

| Storage Type | Monthly Cost (1000 users) | Features |
|--------------|---------------------------|----------|
| **Azure Blob** | ~$0.50 | ✅ Persistent, scalable |
| **SQL Server** | ~$50+ | ⚠️ Complex, expensive |
| **BigQuery** | ~$25+ | ❌ Wrong use case |
| **Memory Only** | $0 | ❌ Lost on restart |

## 🔧 Troubleshooting

### Blob Storage Not Working:
1. Check Azure connection string
2. Verify container exists
3. Check permissions
4. Look for error messages in console

### Sessions Not Persisting:
1. Verify `use_blob_sessions=True`
2. Check if user_id is provided in API calls
3. Look for "Saved session to blob storage" messages

Your system now uses Azure Blob Storage instead of SQL Server! 🎉