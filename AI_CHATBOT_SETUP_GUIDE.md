# 🤖 AI Chatbot Setup Guide

## Overview

Your enterprise solutions chatbot now uses **OpenAI GPT-4o-mini** for intelligent, natural conversations! The AI can:

✨ **Smart Features:**
- Understand natural language (no rigid format needed)
- Extract multiple pieces of information from one message
- Handle conversational flow intelligently
- Auto-fill related data (e.g., tax from country)
- Remember context throughout the conversation

## 🚀 Quick Start

### Step 1: Get Your API Keys

#### **NeonDB (Required)**
1. Go to [https://neon.tech](https://neon.tech)
2. Create a free account (or log in)
3. Create a new project
4. Copy your connection string (looks like):
   ```
   postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname
   ```

#### **OpenAI (Required)**
1. Go to [https://platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-proj-...`)

### Step 2: Configure Environment

Edit `/backend/.env` file with your credentials:

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://your-username:your-password@ep-xxx-xxx.region.aws.neon.tech/your-database

# Security (REQUIRED)
SECRET_KEY=your-random-secret-key-at-least-32-characters

# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Optional Settings
OPENAI_MODEL=gpt-4o-mini
USE_AI_CHATBOT=true
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run the Backend

```bash
python main.py
```

You should see:
```
🔧 Backend Configuration:
   Database: postgresql://...
   API Host: 0.0.0.0
   API Port: 8000
   SECRET_KEY: ... (length: 43)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Test the Chatbot!

Visit: `http://localhost:3000/dashboard/company`

## 💬 Example AI Conversations

### Example 1: Multi-field Input
```
User: 我們公司叫鳳梨有限公司，ID是C001，是食品業，在台灣

Bot: 太好了！我已經記錄以下資訊：
     ✓ 公司ID：C001
     ✓ 公司名稱：鳳梨有限公司
     ✓ 產業別：食品業
     ✓ 國家：台灣

     請問您的公司地址是？
```

### Example 2: Natural Language
```
User: 我們有30件發明專利和30件新型專利

Bot: 已記錄：
     ✓ 發明專利：30件
     ✓ 新型專利：30件

     請問公司有多少份認證資料？
```

### Example 3: Product Information
```
User: 我要新增產品：
     罐頭鳳梨，400克，價格40元，
     原料是鳳梨塊、糖漿和鹽

Bot: 產品「罐頭鳳梨 - 400克」已新增成功！
     是否要繼續新增其他產品？
```

## 🎯 AI vs Rule-Based Comparison

| Feature | AI Chatbot | Rule-Based |
|---------|-----------|------------|
| Natural Language | ✅ Yes | ❌ Limited |
| Multi-field Input | ✅ Yes | ❌ One at a time |
| Context Understanding | ✅ Excellent | ⚠️ Basic |
| Flexibility | ✅ Very Flexible | ❌ Rigid |
| Setup | Requires OpenAI | No external deps |
| Cost | ~$0.001 per conversation | Free |

## 📊 Cost Estimation

Using **gpt-4o-mini** (most cost-effective):
- **Input**: $0.150 / 1M tokens
- **Output**: $0.600 / 1M tokens

**Average conversation** (~20 messages):
- Input: ~5,000 tokens = $0.00075
- Output: ~2,000 tokens = $0.0012
- **Total: ~$0.002 per onboarding session**

💡 **For 1,000 users**: ~$2 in API costs

## ⚙️ Configuration Options

### Use Different AI Model

Edit `.env`:
```env
# For better quality (more expensive)
OPENAI_MODEL=gpt-4o

# For faster/cheaper (recommended)
OPENAI_MODEL=gpt-4o-mini

# For legacy compatibility
OPENAI_MODEL=gpt-3.5-turbo
```

### Disable AI (Use Rule-Based)

Edit `.env`:
```env
USE_AI_CHATBOT=false
```

Or remove/comment out OpenAI key:
```env
# OPENAI_API_KEY=sk-proj-...
```

## 🔧 Troubleshooting

### Error: "OpenAI API key not configured"
**Solution**: Check `.env` file has valid `OPENAI_API_KEY`

### Error: "Rate limit exceeded"
**Solution**:
1. Wait a few minutes
2. Upgrade OpenAI tier
3. Switch to `gpt-3.5-turbo` (higher limits)

### Error: "Connection refused"
**Solution**: Check DATABASE_URL is correct

### Chatbot not responding
**Solution**:
1. Check backend logs
2. Verify OpenAI API key is valid
3. Test with: `curl http://localhost:8000/`

## 🎨 Advanced Customization

### Modify AI Behavior

Edit `/backend/ai_chatbot_handler.py` - `get_system_prompt()`:

```python
def get_system_prompt(self) -> str:
    return """你是一個專業的企業導入助理...

    # Add custom instructions here
    - 使用更正式的語氣
    - 提供額外的驗證
    - 自動建議常見的產業分類
    """
```

### Add Custom Fields

1. Update models in `models.py`
2. Add to AI function schema in `ai_chatbot_handler.py`
3. Update system prompt with new fields

## 📝 Data Export

Export collected data as JSON:

```bash
# Single session
curl -X GET http://localhost:8000/api/chatbot/export/1 \
  -H "Authorization: Bearer YOUR_TOKEN"

# All sessions
curl -X GET http://localhost:8000/api/chatbot/export/all \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Output format:
```json
{
  "公司ID": "C001",
  "公司名稱": "鳳梨有限公司",
  "產業別": "食品業",
  "國家": "台灣",
  "關稅": 0.1,
  ...
  "產品": [...]
}
```

## 🔐 Security Notes

1. **Never commit `.env` file** to git
2. **Rotate API keys** regularly
3. **Use environment variables** in production
4. **Monitor API usage** on OpenAI dashboard
5. **Set spending limits** on OpenAI account

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [NeonDB Documentation](https://neon.tech/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## 💡 Tips for Best Results

1. **Speak naturally**: The AI understands conversational Chinese
2. **Provide context**: More information helps the AI understand better
3. **Review before exporting**: Check collected data is accurate
4. **Use structured format for products**: Makes extraction more reliable

## 🆘 Need Help?

1. Check logs: `tail -f backend/logs/app.log`
2. Test API: Visit `http://localhost:8000/docs`
3. Review conversation: Check chat_messages table
4. Contact support: GitHub Issues

---

**Version**: 1.0.0 (AI-Enhanced)
**Last Updated**: 2024-01-06
**AI Model**: GPT-4o-mini
