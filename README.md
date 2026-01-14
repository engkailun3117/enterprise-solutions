# Enterprise AI Chatbot API

A FastAPI-based chatbot API for enterprise onboarding, integrated with Supabase PostgreSQL database and external JWT authentication.

## 🚀 Version 3.0 - External Authentication & Supabase Migration

**New in v3.0:**
- 🔐 **External JWT Authentication** - Integrates with main user system
- 🔄 **Auto User Sync** - Users automatically created from JWT tokens
- 🗄️ **Supabase Database** - Migrated from Neon to company Supabase
- 🤖 **AI-Powered Chatbot** - Intelligent company onboarding assistant
- 📊 **Data Collection** - Structured company and product information gathering

📖 **See [CHATBOT_MIGRATION_GUIDE.md](./CHATBOT_MIGRATION_GUIDE.md) for migration details**

## 🏗️ Tech Stack

- **Backend**: FastAPI + SQLAlchemy + External JWT Validation
- **Database**: Supabase PostgreSQL
- **AI**: OpenAI GPT-4o-mini for intelligent conversations
- **Language**: Python 3.9+
- **Security**: External JWT token validation, auto user sync

## 📋 Features

### External Authentication
- ✅ JWT token validation from main user system
- ✅ Automatic user creation and synchronization
- ✅ No local password management required
- ✅ Seamless integration with existing user systems
- ✅ Protected API endpoints with Bearer tokens

### AI Chatbot Capabilities
- ✅ Intelligent conversational data collection
- ✅ Natural language understanding (OpenAI GPT-4o-mini)
- ✅ Sequential question-based flow (rule-based mode)
- ✅ Multi-turn conversation support
- ✅ Session management and history tracking
- ✅ Progress tracking and completion detection

### Data Collection
- ✅ Company information (industry, capital, patents)
- ✅ Certification data (including ESG)
- ✅ Product details (multi-product support)
- ✅ Structured JSON export format
- ✅ Chinese language support (Traditional)

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Supabase project with PostgreSQL database
- Access to main user system's JWT secret key
- OpenAI API key (optional, for AI chatbot mode)

### 1. Environment Configuration

Create the `.env` file in the backend directory:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your configuration:

```env
# Supabase Database
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# External JWT Authentication (from main system)
EXTERNAL_JWT_SECRET=your-shared-jwt-secret-from-main-system

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI Configuration (optional)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
USE_AI_CHATBOT=true
```

**How to get your Supabase DATABASE_URL:**
1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **Database**
4. Find **Connection String** → **URI**
5. Copy the connection string (replace `[YOUR-PASSWORD]` with actual password)

**How to get EXTERNAL_JWT_SECRET:**
1. Contact your main system developers
2. Request the shared JWT secret key
3. Confirm JWT payload includes `user_id` and `username`

### 2. Backend Setup

Install Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

The database tables will be created automatically when you start the server.

Start the FastAPI server:

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Documentation: `http://localhost:8000/redoc`

### 3. Integration with Main System

The chatbot API expects JWT tokens from your main user system. The token should be passed in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

**Required JWT Payload:**
```json
{
  "user_id": "12345",
  "username": "john_doe"
}
```

Users will be automatically created in the chatbot database on their first API call.

## 📊 Database Schema

### Core Chatbot Tables

#### Users Table (Auto-synced from main system)
| Column Name       | Type         | Constraints      | Description                    |
|------------------|--------------|------------------|--------------------------------|
| id               | INTEGER      | PRIMARY KEY      | Local database user ID         |
| external_user_id | VARCHAR(100) | UNIQUE, NOT NULL | User ID from main system       |
| username         | VARCHAR(50)  | NOT NULL         | Username from main system      |
| role             | ENUM         | NOT NULL         | 'user' or 'admin'              |
| is_active        | BOOLEAN      | NOT NULL         | Account active status          |
| created_at       | TIMESTAMP    | NOT NULL         | First sync timestamp           |
| updated_at       | TIMESTAMP    | NOT NULL         | Last sync timestamp            |

#### Chat Sessions Table
| Column Name  | Type      | Constraints      | Description                        |
|-------------|-----------|------------------|------------------------------------|
| id          | INTEGER   | PRIMARY KEY      | Auto-increment session ID          |
| user_id     | INTEGER   | FK → users.id    | User who owns the session          |
| status      | ENUM      | NOT NULL         | active/completed/abandoned         |
| created_at  | TIMESTAMP | NOT NULL         | Session creation time              |
| updated_at  | TIMESTAMP | NOT NULL         | Last activity time                 |
| completed_at| TIMESTAMP | NULLABLE         | Completion timestamp               |

#### Chat Messages Table
| Column Name | Type      | Constraints         | Description                     |
|------------|-----------|---------------------|---------------------------------|
| id         | INTEGER   | PRIMARY KEY         | Auto-increment message ID       |
| session_id | INTEGER   | FK → chat_sessions.id | Session this message belongs to|
| role       | VARCHAR(20)| NOT NULL           | 'user' or 'assistant'           |
| content    | TEXT      | NOT NULL            | Message content                 |
| created_at | TIMESTAMP | NOT NULL            | Message timestamp               |

#### Company Onboarding Table (Collected by Chatbot)
| Column Name              | Type      | Constraints              | Description                          |
|-------------------------|-----------|--------------------------|--------------------------------------|
| id                      | INTEGER   | PRIMARY KEY              | Auto-increment onboarding ID         |
| chat_session_id         | INTEGER   | FK → chat_sessions.id, UNIQUE | Associated chat session        |
| user_id                 | INTEGER   | FK → users.id            | User who provided the data           |
| industry                | VARCHAR(100) | NULLABLE              | 產業別                               |
| capital_amount          | INTEGER   | NULLABLE                 | 資本總額 (in 臺幣)                   |
| invention_patent_count  | INTEGER   | NULLABLE                 | 發明專利數量                         |
| utility_patent_count    | INTEGER   | NULLABLE                 | 新型專利數量                         |
| certification_count     | INTEGER   | NULLABLE                 | 公司認證資料數量                     |
| esg_certification       | BOOLEAN   | NULLABLE                 | ESG相關認證資料                      |
| created_at              | TIMESTAMP | NOT NULL                 | Data creation time                   |
| updated_at              | TIMESTAMP | NOT NULL                 | Last update time                     |

#### Products Table (Sub-records of company onboarding)
| Column Name           | Type         | Constraints                  | Description                      |
|----------------------|--------------|------------------------------|----------------------------------|
| id                   | INTEGER      | PRIMARY KEY                  | Auto-increment product ID        |
| onboarding_id        | INTEGER      | FK → company_onboarding.id   | Parent onboarding record         |
| product_id           | VARCHAR(100) | NULLABLE                     | 產品ID                           |
| product_name         | VARCHAR(200) | NULLABLE                     | 產品名稱                         |
| price                | VARCHAR(50)  | NULLABLE                     | 價格                             |
| main_raw_materials   | VARCHAR(500) | NULLABLE                     | 主要原料                         |
| product_standard     | VARCHAR(200) | NULLABLE                     | 產品規格(尺寸、精度)             |
| technical_advantages | TEXT         | NULLABLE                     | 技術優勢                         |
| created_at           | TIMESTAMP    | NOT NULL                     | Product creation time            |

### Other Tables (Not Chatbot Responsibility)

The `Company_Info` table exists but is managed by other systems, not this chatbot API.

## 🔌 API Endpoints

### Authentication

All endpoints require a JWT token from the main user system:

```http
Authorization: Bearer <jwt-token-from-main-system>
```

### User Endpoints

**Get Current User (Auto-sync from JWT)**
```http
GET /api/auth/me
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "external_user_id": "12345",
  "username": "john_doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Chatbot Endpoints

**Create New Chat Session**
```http
POST /api/chatbot/sessions/new
Authorization: Bearer <token>

Response:
{
  "session_id": 1,
  "message": "您好！我是企業導入 AI 助理 🤖...",
  "company_info_copied": false,
  "progress": {...}
}
```

**Send Message to Chatbot**
```http
POST /api/chatbot/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "我的公司是電子業",
  "session_id": 1
}

Response:
{
  "session_id": 1,
  "message": "好的，您的公司屬於電子業...",
  "completed": false,
  "progress": {...}
}
```

**Get All Chat Sessions**
```http
GET /api/chatbot/sessions
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "user_id": 1,
    "status": "active",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

**Get Latest Active Session**
```http
GET /api/chatbot/sessions/latest
Authorization: Bearer <token>

Response:
{
  "session_id": 1,
  "status": "active",
  "created_at": "2024-01-01T00:00:00"
}
```

**Get Session Messages**
```http
GET /api/chatbot/sessions/{session_id}/messages
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "session_id": 1,
    "role": "assistant",
    "content": "您好！我是企業導入 AI 助理...",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

**Get Collected Onboarding Data**
```http
GET /api/chatbot/data/{session_id}
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "chat_session_id": 1,
  "industry": "電子業",
  "capital_amount": 5000000,
  "invention_patent_count": 10,
  "products": [...]
}
```

**Export Session Data**
```http
GET /api/chatbot/export/{session_id}
Authorization: Bearer <token>

Response:
{
  "產業別": "電子業",
  "資本總額（以臺幣為單位）": 5000000,
  "發明專利數量": 10,
  "產品": [...]
}
```

**Export All Completed Sessions**
```http
GET /api/chatbot/export/all
Authorization: Bearer <token>

Response:
[
  {
    "產業別": "電子業",
    ...
  }
]
```

## 🧪 Testing

### Generate Test JWT Token

Create a test token for development:

```python
# backend/test_token.py
from jose import jwt

EXTERNAL_JWT_SECRET = "your-shared-secret"  # Same as .env

token = jwt.encode(
    {
        "user_id": "test123",
        "username": "testuser"
    },
    EXTERNAL_JWT_SECRET,
    algorithm="HS256"
)

print(f"Test Token:\n{token}")
```

Run:
```bash
cd backend
python test_token.py
```

### Test Chatbot API

Using curl:
```bash
# Set your test token
TOKEN="your-generated-jwt-token"

# Health check
curl http://localhost:8000/

# Get current user (auto-creates user from JWT)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Create new chat session
curl -X POST http://localhost:8000/api/chatbot/sessions/new \
  -H "Authorization: Bearer $TOKEN"

# Send message to chatbot
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我的公司是電子業",
    "session_id": 1
  }'

# Get session messages
curl http://localhost:8000/api/chatbot/sessions/1/messages \
  -H "Authorization: Bearer $TOKEN"

# Export collected data
curl http://localhost:8000/api/chatbot/export/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive testing.

**To test with JWT:**
1. Click "Authorize" button in Swagger UI
2. Enter: `Bearer your-jwt-token`
3. Click "Authorize"
4. Test any endpoint

## 📁 Project Structure

```
enterprise-solutions/
├── backend/
│   ├── main.py                     # FastAPI application & chatbot routes
│   ├── auth.py                     # External JWT validation & user sync
│   ├── config.py                   # Configuration settings
│   ├── database.py                 # Supabase database connection
│   ├── models.py                   # SQLAlchemy models (User, ChatSession, etc.)
│   ├── schemas.py                  # Pydantic validation schemas
│   ├── chatbot_handler.py          # Rule-based chatbot logic
│   ├── ai_chatbot_handler.py       # AI-powered chatbot logic
│   ├── create_admin.py             # Admin user creation utility
│   ├── view_database.py            # Database viewer utility
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (not in git)
│   ├── .env.example                # Example environment variables
│   └── migrations/
│       └── 003_remove_company_info_fields.py
├── CHATBOT_MIGRATION_GUIDE.md      # Migration documentation
└── README.md                       # This file
```

## 🔒 Security Notes

- ✅ **External JWT validation** for authentication
- ✅ **Auto user synchronization** from main system
- ✅ **No password storage** in chatbot database
- ✅ **Protected API endpoints** require valid JWT tokens
- ✅ **Role-based access control** (User/Admin)
- ⚠️ **Never commit `.env`** file to version control
- ⚠️ **EXTERNAL_JWT_SECRET must match** main system secret
- ⚠️ **Update CORS settings** in production
- ⚠️ **Use HTTPS** in production environments
- ⚠️ **Protect JWT secret** - never expose in client-side code

## 🎨 Chatbot Features

- Intelligent conversational interface (AI mode)
- Sequential question flow (rule-based mode)
- Multi-turn conversation support
- Progress tracking and completion detection
- Session history and resume capability
- Structured data collection and export
- Chinese (Traditional) language support
- Real-time message streaming
- Context-aware responses

## 📝 Future Enhancements

Potential features to add:

1. ✅ ~~External JWT Authentication~~ - **DONE in v3.0**
2. ✅ ~~Supabase Migration~~ - **DONE in v3.0**
3. ✅ ~~AI Chatbot~~ - **DONE in v2.0**
4. **Webhook Notifications** - Notify main system on completion
5. **Multi-language Support** - English, Simplified Chinese
6. **Voice Input** - Speech-to-text for chatbot
7. **File Upload** - Allow document uploads during chat
8. **Advanced Analytics** - Track chatbot performance metrics
9. **LangGraph Integration** - More sophisticated conversation flows
10. **Chatbot Customization** - Configurable chatbot personality

## 🐛 Troubleshooting

### JWT Authentication Issues

**Problem:** 401 Unauthorized - "Could not validate credentials"
```
Solution:
1. Verify EXTERNAL_JWT_SECRET in .env matches main system
2. Check JWT token format includes user_id and username
3. Ensure token is not expired
4. Check backend logs for detailed JWT errors
5. Restart backend after changing EXTERNAL_JWT_SECRET
```

**Problem:** "Invalid token: missing user_id or username"
```
Solution:
1. JWT payload must include both fields:
   {"user_id": "123", "username": "john"}
2. Verify main system JWT generation code
3. Test with manually generated token (see Testing section)
```

**Problem:** User not auto-created
```
Solution:
1. Check backend logs for errors
2. Verify JWT token is valid
3. Ensure database tables are created (check startup logs)
4. Verify DATABASE_URL is correct
```

### Database Issues

**Problem:** Database connection errors
```
Solution:
1. Verify DATABASE_URL in .env is correct
2. Ensure Supabase project is active
3. Check database password in connection string
4. Test connection in Supabase dashboard
5. Verify network/firewall settings
```

**Problem:** "relation does not exist" errors
```
Solution:
- Tables are auto-created on first startup
- Restart the backend to trigger table creation
- Check backend logs for creation errors
- Verify Supabase database permissions
```

**Problem:** ENUM type errors
```
Solution:
Tables are auto-created with ENUM types.
If manual creation needed, check models.py for ENUM definitions.
```

### Installation Issues

**Problem:** psycopg2-binary installation fails
```
Solution:
pip install psycopg2-binary==2.9.10
Or use Python 3.9-3.12 (recommended)
```

**Problem:** python-jose installation fails
```
Solution:
pip install python-jose[cryptography]==3.3.0
Ensure cryptography package is installed
```

**Problem:** OpenAI module errors
```
Solution:
pip install openai==1.54.0
Check OPENAI_API_KEY is set if using AI mode
```

### Chatbot Issues

**Problem:** Chatbot not responding
```
Solution:
1. Check USE_AI_CHATBOT setting in .env
2. If AI mode: Verify OPENAI_API_KEY is valid
3. Check backend logs for errors
4. Ensure session_id is correct
```

**Problem:** Data not saving
```
Solution:
1. Check database connection
2. Verify user has active session
3. Check backend logs for SQL errors
4. Ensure session is not already completed
```

### General Issues

**Problem:** CORS errors
```
Solution:
- Backend runs on http://localhost:8000
- Check CORS settings in backend/main.py
- Verify frontend URL is allowed
```

**Problem:** Module not found errors
```
Solution:
cd backend
pip install -r requirements.txt
```

**Need more help?** See [CHATBOT_MIGRATION_GUIDE.md](./CHATBOT_MIGRATION_GUIDE.md) for detailed migration documentation.

## 📄 License

This project is for testing and development purposes.
