# Chatbot API Migration Guide: Neon → Supabase

## 🔄 Migration Overview

This guide documents the migration from Neon.tech to Supabase, and the transition from local password-based authentication to external JWT authentication for the AI Chatbot API.

## 📋 What Changed

### 1. **Database Provider**
- **Before**: Neon.tech PostgreSQL
- **After**: Supabase PostgreSQL

### 2. **Authentication Method**
- **Before**: Local username/password authentication with hashed passwords
- **After**: External JWT token validation from main user system

### 3. **User Management**
- **Before**: Users register and login within the chatbot API
- **After**: Users are auto-synced from main system via JWT tokens

## 🏗️ New Architecture

### Authentication Flow

```
Main User System                    Chatbot API
----------------                    -----------
1. User logs in          →
2. JWT token created     →
3. User calls chatbot    →         4. Validate JWT token
   with Bearer token                5. Extract user_id & username
                                    6. Auto-create/update user in local DB
                                    7. Return chatbot response
```

### JWT Token Format

The JWT token from your main system should contain:
```json
{
  "user_id": "12345",      // User ID from main system
  "username": "john_doe",  // Username
  "exp": 1234567890        // Optional expiration timestamp
}
```

## 🗄️ Database Changes

### Updated `users` Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Local database user ID |
| external_user_id | VARCHAR(100) UNIQUE | User ID from main system |
| username | VARCHAR(50) | Username from main system |
| role | ENUM (user/admin) | User role |
| is_active | BOOLEAN | Account status |
| created_at | TIMESTAMP | First sync timestamp |
| updated_at | TIMESTAMP | Last sync timestamp |

**Removed columns:**
- ❌ `email` (not needed for chatbot)
- ❌ `hashed_password` (no local authentication)

### Chatbot Tables (Unchanged)

These tables remain the same and are the core responsibility of the chatbot API:

1. **chat_sessions** - User chat sessions
2. **chat_messages** - Chat conversation history
3. **company_onboarding** - Collected company data
4. **products** - Product information from chatbot

## 🚀 Setup Instructions

### 1. Get Supabase Database URL

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on **Settings** → **Database**
3. Find **Connection String** → **URI**
4. Copy the connection string (format: `postgresql://postgres:[password]@[host]:5432/postgres`)

### 2. Get JWT Secret from Main System

Contact your main system developers to get:
- The **shared JWT secret key** used to sign tokens
- Confirm the JWT payload structure (user_id, username)

### 3. Configure Environment Variables

Create/update `backend/.env`:

```env
# Supabase Database
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# External JWT Authentication
EXTERNAL_JWT_SECRET=your-shared-jwt-secret-from-main-system

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI (for AI Chatbot)
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
USE_AI_CHATBOT=true
```

### 4. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Start the API

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The database tables will be created automatically on first run.

## 🔌 API Usage

### Authentication

All chatbot endpoints require a JWT token from the main system:

```http
Authorization: Bearer <jwt-token-from-main-system>
```

### Example: Create New Chat Session

```bash
curl -X POST http://localhost:8000/api/chatbot/sessions/new \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Example: Send Message

```bash
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我的公司是電子業",
    "session_id": 1
  }'
```

### Available Chatbot Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/me` | Get current user info (auto-syncs user) |
| POST | `/api/chatbot/sessions/new` | Create new chat session |
| POST | `/api/chatbot/message` | Send message to chatbot |
| GET | `/api/chatbot/sessions` | Get all user sessions |
| GET | `/api/chatbot/sessions/latest` | Get latest active session |
| GET | `/api/chatbot/sessions/{id}/messages` | Get session messages |
| GET | `/api/chatbot/data/{session_id}` | Get collected onboarding data |
| GET | `/api/chatbot/export/{session_id}` | Export session data as JSON |
| GET | `/api/chatbot/export/all` | Export all completed sessions |

## 🔐 Security Notes

- ✅ JWT tokens are validated using the shared secret
- ✅ Users are automatically created on first API call
- ✅ Username updates are synced automatically
- ✅ User data is isolated by user_id
- ⚠️ **EXTERNAL_JWT_SECRET must match** the one used by main system
- ⚠️ **Never expose JWT secret** in client-side code

## 🔄 Integration with Main System

### Step 1: User Logs In (Main System)
```javascript
// In your main system
const token = jwt.sign(
  { user_id: user.id, username: user.username },
  EXTERNAL_JWT_SECRET,
  { algorithm: 'HS256', expiresIn: '24h' }
);
```

### Step 2: Call Chatbot API (Frontend)
```javascript
// In your frontend application
const response = await fetch('http://chatbot-api/api/chatbot/sessions/new', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log('Session created:', data.session_id);
```

### Step 3: Auto-User-Sync (Chatbot API)
The chatbot API will automatically:
1. Validate the JWT token
2. Extract user_id and username
3. Create user in local DB if doesn't exist
4. Update username if changed
5. Return chatbot response

## 🧪 Testing

### Test JWT Token Generation

You can test by creating a JWT token manually:

```python
# test_token.py
from jose import jwt

EXTERNAL_JWT_SECRET = "your-shared-secret"

token = jwt.encode(
    {"user_id": "test123", "username": "testuser"},
    EXTERNAL_JWT_SECRET,
    algorithm="HS256"
)

print(f"Test Token: {token}")
```

Then test the API:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <generated-token>"
```

## 🐛 Troubleshooting

### "Could not validate credentials"
- Check that `EXTERNAL_JWT_SECRET` matches between main system and chatbot API
- Verify JWT token format includes `user_id` and `username`
- Check token hasn't expired

### "Invalid token: missing user_id or username"
- JWT payload must include both `user_id` and `username` fields
- Check JWT payload structure in main system

### Database connection errors
- Verify `DATABASE_URL` is correct
- Check Supabase project is active
- Ensure database password is correct in connection string

### User not auto-created
- Check backend logs for error messages
- Verify JWT token is valid
- Ensure database tables are created

## 📊 Monitoring

Check backend logs for user sync activity:
```
✅ Created new user: john_doe (external_id: 12345)
✅ Updated user: jane_doe (external_id: 67890)
```

## 🔮 Future Enhancements

- [ ] Add refresh token support
- [ ] Implement role-based permissions from main system
- [ ] Add user activity logging
- [ ] Support for multiple JWT issuers
- [ ] Webhook notifications to main system

## 📞 Support

For integration questions:
1. Check JWT token format with main system team
2. Verify shared secret is correctly configured
3. Review backend logs for detailed error messages
4. Test with manual JWT token generation

---

**Migration completed**: The chatbot API is now ready to integrate with your company's main user system via JWT authentication!
