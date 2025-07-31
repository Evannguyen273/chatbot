# H&M Data Assistant - Quick Start Guide

## 🚀 Interactive Application

Run the main interactive application:
```bash
python app.py
```

This will start an interactive chat session where you can ask questions about your H&M ServiceNow data.

## 📋 Command Line Options

### Run example queries:
```bash
python app.py --examples
```

### Ask a single question:
```bash
python app.py --query "How many incidents were created this year?"
```

## 🧪 Testing

Test the pipeline with predefined queries:
```bash
python main.py
```

## 💬 Example Interactions

```
💬 You: Hi there!
🤖 Assistant: Hello! I'm your H&M data assistant. How can I help you with incident or problem data today?

💬 You: How many critical incidents do we have?
🤖 Assistant: [Generates SQL query and returns results]

💬 You: What's the weather like?
🤖 Assistant: I don't have access to weather data. I specialize in H&M's incident and problem management data.
```

## 🔧 Available Query Types

- **Greetings**: "hi", "hello", "hey"
- **Data Queries**: Questions about incidents, problems, counts, etc.
- **General Knowledge**: Non-data questions get informative responses

## 🛑 Exit Commands

Type any of these to exit the interactive mode:
- `quit`
- `exit` 
- `bye`
- `q`
- Or press `Ctrl+C`