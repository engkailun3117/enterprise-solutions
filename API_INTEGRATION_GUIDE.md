# Chatbot API Integration Guide for Developers

This guide explains how to integrate your application with the Enterprise AI Chatbot API.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Integration Workflow](#integration-workflow)
- [Code Examples](#code-examples)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## Overview

**Base URL:** `http://localhost:8000` (Development)
**Authentication:** JWT Bearer Token
**Content-Type:** `application/json`

The Chatbot API provides an AI-powered conversational interface for collecting company onboarding information including:
- Company details (industry, capital, patents, certifications)
- Product information (name, price, materials, specifications)

---

## Authentication

### JWT Token Requirements

All API requests require a valid JWT token in the `Authorization` header.

**JWT Payload Structure:**
```json
{
  "user_id": "12345",        // Required: User ID from your system
  "username": "john_doe",    // Required: Username
  "exp": 1234567890          // Optional: Expiration timestamp
}
```

**JWT Secret:**
- Must be shared between your system and the chatbot API
- Algorithm: `HS256`
- Configure in chatbot API's `.env` file as `EXTERNAL_JWT_SECRET`

### Generating JWT Token (Node.js Example)

```javascript
const jwt = require('jsonwebtoken');

const JWT_SECRET = 'your-shared-secret-key';

function generateChatbotToken(userId, username) {
  return jwt.sign(
    {
      user_id: userId,
      username: username
    },
    JWT_SECRET,
    {
      algorithm: 'HS256',
      expiresIn: '24h'
    }
  );
}

// Usage
const token = generateChatbotToken('12345', 'john_doe');
```

### Generating JWT Token (Python Example)

```python
from jose import jwt
from datetime import datetime, timedelta

JWT_SECRET = 'your-shared-secret-key'

def generate_chatbot_token(user_id: str, username: str) -> str:
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# Usage
token = generate_chatbot_token('12345', 'john_doe')
```

### Making Authenticated Requests

```javascript
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';
const token = 'your-jwt-token';

const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

// Example request
axios.get(`${API_BASE_URL}/api/auth/me`, { headers })
  .then(response => console.log(response.data))
  .catch(error => console.error(error.response.data));
```

---

## API Endpoints

### 1. Get Current User (Auto-Sync)

Validates the JWT token and auto-creates/updates the user in the chatbot database.

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
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

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token
- `403` - User account is inactive

---

### 2. Create New Chat Session

Starts a new chatbot conversation. Returns a welcome message and session ID.

**Endpoint:** `POST /api/chatbot/sessions/new`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "session_id": 1,
  "message": "您好！我是企業導入 AI 助理 🤖\n\n我將用智能對話的方式協助您建立公司資料...",
  "company_info_copied": false,
  "progress": {
    "industry": false,
    "capital_amount": false,
    "patents": false,
    "certifications": false,
    "products": false
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token

---

### 3. Send Message to Chatbot

Sends a user message to the chatbot and receives a response.

**Endpoint:** `POST /api/chatbot/message`

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "我的公司是電子業",
  "session_id": 1
}
```

**Response:**
```json
{
  "session_id": 1,
  "message": "好的，您的公司屬於電子業。接下來，請問貴公司的資本總額是多少？（請以臺幣為單位）",
  "completed": false,
  "progress": {
    "industry": true,
    "capital_amount": false,
    "patents": false,
    "certifications": false,
    "products": false
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request (missing message or session_id)
- `401` - Invalid or missing token
- `404` - Session not found

---

### 4. Get All Chat Sessions

Retrieves all chat sessions for the current user.

**Endpoint:** `GET /api/chatbot/sessions`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "status": "active",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:30:00",
    "completed_at": null
  },
  {
    "id": 2,
    "user_id": 1,
    "status": "completed",
    "created_at": "2024-01-02T10:00:00",
    "updated_at": "2024-01-02T11:00:00",
    "completed_at": "2024-01-02T11:00:00"
  }
]
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token

---

### 5. Get Latest Active Session

Retrieves the most recent active chat session for the current user.

**Endpoint:** `GET /api/chatbot/sessions/latest`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "session_id": 1,
  "status": "active",
  "created_at": "2024-01-01T10:00:00"
}
```

**Response (No Active Session):**
```json
{
  "session_id": null
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token

---

### 6. Get Session Messages

Retrieves all messages for a specific chat session.

**Endpoint:** `GET /api/chatbot/sessions/{session_id}/messages`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
[
  {
    "id": 1,
    "session_id": 1,
    "role": "assistant",
    "content": "您好！我是企業導入 AI 助理...",
    "created_at": "2024-01-01T10:00:00"
  },
  {
    "id": 2,
    "session_id": 1,
    "role": "user",
    "content": "我的公司是電子業",
    "created_at": "2024-01-01T10:01:00"
  },
  {
    "id": 3,
    "session_id": 1,
    "role": "assistant",
    "content": "好的，您的公司屬於電子業...",
    "created_at": "2024-01-01T10:01:05"
  }
]
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token
- `404` - Session not found or doesn't belong to user

---

### 7. Get Collected Onboarding Data

Retrieves the structured data collected during a chat session.

**Endpoint:** `GET /api/chatbot/data/{session_id}`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "id": 1,
  "chat_session_id": 1,
  "user_id": 1,
  "industry": "電子業",
  "capital_amount": 5000000,
  "invention_patent_count": 10,
  "utility_patent_count": 5,
  "certification_count": 3,
  "esg_certification": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T11:00:00",
  "products": [
    {
      "id": 1,
      "onboarding_id": 1,
      "product_id": "P001",
      "product_name": "智能晶片",
      "price": "1000元",
      "main_raw_materials": "矽晶圓",
      "product_standard": "10nm製程",
      "technical_advantages": "低功耗、高效能",
      "created_at": "2024-01-01T10:30:00"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token
- `404` - Session not found or no data collected

---

### 8. Export Session Data (Chinese Format)

Exports collected data in Chinese field names format.

**Endpoint:** `GET /api/chatbot/export/{session_id}`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "產業別": "電子業",
  "資本總額（以臺幣為單位）": 5000000,
  "發明專利數量": 10,
  "新型專利數量": 5,
  "公司認證資料數量": 3,
  "ESG相關認證資料": "有",
  "產品": [
    {
      "產品ID": "P001",
      "產品名稱": "智能晶片",
      "價格": "1000元",
      "主要原料": "矽晶圓",
      "產品規格(尺寸、精度)": "10nm製程",
      "技術優勢": "低功耗、高效能"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token
- `404` - Session not found or no data collected

---

### 9. Export All Completed Sessions

Exports all completed sessions for the current user.

**Endpoint:** `GET /api/chatbot/export/all`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
[
  {
    "產業別": "電子業",
    "資本總額（以臺幣為單位）": 5000000,
    "發明專利數量": 10,
    "新型專利數量": 5,
    "公司認證資料數量": 3,
    "ESG相關認證資料": "有",
    "產品": [...]
  },
  {
    "產業別": "製造業",
    "資本總額（以臺幣為單位）": 3000000,
    ...
  }
]
```

**Status Codes:**
- `200` - Success
- `401` - Invalid or missing token

---

### 10. Upload File for Data Extraction

Upload a document (PDF, Word, Image, or Text) for AI-powered data extraction. The chatbot will automatically extract company information and populate the onboarding data.

**Endpoint:** `POST /api/chatbot/upload-file`

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
file: <binary-file>
session_id: <integer> (optional)
```

**Supported File Types:**
- PDF (`.pdf`)
- Word Documents (`.docx`)
- Images (`.jpg`, `.jpeg`, `.png`)
- Text Files (`.txt`)

**File Size Limit:** 10MB

**Response:**
```json
{
  "session_id": 1,
  "message": "✅ 文件處理成功！\n\n📄 文件資訊：\n- 文件名稱：company_info.pdf\n- 文件類型：PDF文件\n- 提取字數：1500 字\n\n🤖 AI 已自動提取以下資訊：\n公司名稱：科技電子股份有限公司\n產業別：電子業\n資本額：5000000元...",
  "completed": false,
  "progress": {
    "industry": true,
    "capital_amount": true,
    "patents": true,
    "certifications": true,
    "products": true
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid file type or file too large
- `401` - Invalid or missing token
- `500` - File processing error

**JavaScript Example:**
```javascript
async function uploadFile(chatbot, file, sessionId = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (sessionId) {
    formData.append('session_id', sessionId);
  }

  const response = await fetch('http://localhost:8000/api/chatbot/upload-file', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
      // Don't set Content-Type - browser will set it with boundary
    },
    body: formData
  });

  return await response.json();
}
```

**Python Example:**
```python
async def upload_file(chatbot: ChatbotAPIClient, file_path: str, session_id: Optional[int] = None):
    """Upload file for data extraction"""
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {}
        if session_id:
            data['session_id'] = session_id

        response = await chatbot.client.post('/api/chatbot/upload-file', files=files, data=data)
        response.raise_for_status()
        return response.json()
```

**Notes:**
- If `session_id` is not provided, a new session will be created automatically
- The AI will extract structured company data including: company name, industry, capital, patents, certifications, and products
- Extracted data is automatically saved to the database
- For images, OpenAI Vision API is used for higher accuracy (if configured), otherwise Tesseract OCR is used
- Chinese characters are supported (Traditional Chinese)

---

## Integration Workflow

### Typical User Flow

```
1. User logs into your main system
   ↓
2. Generate JWT token with user_id and username
   ↓
3. Call POST /api/chatbot/sessions/new
   ↓
4. Display welcome message to user
   ↓
5. User sends messages via POST /api/chatbot/message
   ↓
6. Display chatbot responses
   ↓
7. Repeat step 5-6 until completed = true
   ↓
8. Call GET /api/chatbot/export/{session_id} to get collected data
   ↓
9. Process/store the collected company data in your system
```

### Resuming Existing Session

```
1. User returns to chatbot
   ↓
2. Call GET /api/chatbot/sessions/latest
   ↓
3. If session_id exists:
   - Load existing session
   - Call GET /api/chatbot/sessions/{session_id}/messages
   - Display chat history
   ↓
4. If session_id is null:
   - Create new session
```

---

## Code Examples

### Complete Integration Example (JavaScript/React)

```javascript
import axios from 'axios';

class ChatbotAPI {
  constructor(baseURL, token) {
    this.client = axios.create({
      baseURL: baseURL,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  }

  // Verify user authentication
  async verifyUser() {
    try {
      const response = await this.client.get('/api/auth/me');
      return response.data;
    } catch (error) {
      throw new Error('Authentication failed: ' + error.message);
    }
  }

  // Create new chat session
  async createSession() {
    const response = await this.client.post('/api/chatbot/sessions/new');
    return response.data;
  }

  // Get latest active session
  async getLatestSession() {
    const response = await this.client.get('/api/chatbot/sessions/latest');
    return response.data;
  }

  // Send message to chatbot
  async sendMessage(sessionId, message) {
    const response = await this.client.post('/api/chatbot/message', {
      session_id: sessionId,
      message: message
    });
    return response.data;
  }

  // Get session messages
  async getMessages(sessionId) {
    const response = await this.client.get(`/api/chatbot/sessions/${sessionId}/messages`);
    return response.data;
  }

  // Get all sessions
  async getAllSessions() {
    const response = await this.client.get('/api/chatbot/sessions');
    return response.data;
  }

  // Export session data
  async exportSession(sessionId) {
    const response = await this.client.get(`/api/chatbot/export/${sessionId}`);
    return response.data;
  }

  // Export all completed sessions
  async exportAll() {
    const response = await this.client.get('/api/chatbot/export/all');
    return response.data;
  }

  // Upload file for data extraction
  async uploadFile(file, sessionId = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    // Note: axios will automatically set Content-Type with boundary
    const response = await this.client.post('/api/chatbot/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }
}

// Usage Example
async function initializeChatbot(userId, username) {
  // Generate JWT token (use your JWT library)
  const token = generateJWTToken(userId, username);

  // Initialize API client
  const chatbot = new ChatbotAPI('http://localhost:8000', token);

  try {
    // Verify authentication
    const user = await chatbot.verifyUser();
    console.log('User authenticated:', user);

    // Check for existing session
    const latest = await chatbot.getLatestSession();

    let sessionId;
    if (latest.session_id) {
      // Resume existing session
      sessionId = latest.session_id;
      const messages = await chatbot.getMessages(sessionId);
      console.log('Resuming session with messages:', messages);
    } else {
      // Create new session
      const session = await chatbot.createSession();
      sessionId = session.session_id;
      console.log('New session created:', session.message);
    }

    return { chatbot, sessionId };
  } catch (error) {
    console.error('Failed to initialize chatbot:', error);
    throw error;
  }
}

// Send message example
async function sendChatMessage(chatbot, sessionId, userMessage) {
  try {
    const response = await chatbot.sendMessage(sessionId, userMessage);

    console.log('Bot response:', response.message);
    console.log('Progress:', response.progress);

    if (response.completed) {
      console.log('Chatbot completed! Exporting data...');
      const exportedData = await chatbot.exportSession(sessionId);
      console.log('Collected data:', exportedData);

      // Save to your system
      await saveCompanyData(exportedData);
    }

    return response;
  } catch (error) {
    console.error('Failed to send message:', error);
    throw error;
  }
}
```

### Complete Integration Example (Python/FastAPI)

```python
import httpx
from typing import Optional, Dict, Any

class ChatbotAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.client = httpx.AsyncClient(base_url=base_url, headers=self.headers)

    async def verify_user(self) -> Dict[str, Any]:
        """Verify user authentication"""
        response = await self.client.get('/api/auth/me')
        response.raise_for_status()
        return response.json()

    async def create_session(self) -> Dict[str, Any]:
        """Create new chat session"""
        response = await self.client.post('/api/chatbot/sessions/new')
        response.raise_for_status()
        return response.json()

    async def get_latest_session(self) -> Dict[str, Any]:
        """Get latest active session"""
        response = await self.client.get('/api/chatbot/sessions/latest')
        response.raise_for_status()
        return response.json()

    async def send_message(self, session_id: int, message: str) -> Dict[str, Any]:
        """Send message to chatbot"""
        response = await self.client.post('/api/chatbot/message', json={
            'session_id': session_id,
            'message': message
        })
        response.raise_for_status()
        return response.json()

    async def get_messages(self, session_id: int) -> list:
        """Get session messages"""
        response = await self.client.get(f'/api/chatbot/sessions/{session_id}/messages')
        response.raise_for_status()
        return response.json()

    async def export_session(self, session_id: int) -> Dict[str, Any]:
        """Export session data"""
        response = await self.client.get(f'/api/chatbot/export/{session_id}')
        response.raise_for_status()
        return response.json()

    async def upload_file(self, file_path: str, session_id: Optional[int] = None) -> Dict[str, Any]:
        """Upload file for data extraction"""
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.split('/')[-1], f)}
            data = {}
            if session_id:
                data['session_id'] = session_id

            response = await self.client.post('/api/chatbot/upload-file', files=files, data=data)
            response.raise_for_status()
            return response.json()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Usage Example
async def initialize_chatbot(user_id: str, username: str) -> tuple:
    """Initialize chatbot session"""
    # Generate JWT token
    token = generate_jwt_token(user_id, username)

    # Create API client
    chatbot = ChatbotAPIClient('http://localhost:8000', token)

    try:
        # Verify authentication
        user = await chatbot.verify_user()
        print(f"User authenticated: {user}")

        # Check for existing session
        latest = await chatbot.get_latest_session()

        if latest['session_id']:
            # Resume existing session
            session_id = latest['session_id']
            messages = await chatbot.get_messages(session_id)
            print(f"Resuming session with {len(messages)} messages")
        else:
            # Create new session
            session = await chatbot.create_session()
            session_id = session['session_id']
            print(f"New session created: {session['message']}")

        return chatbot, session_id
    except Exception as e:
        await chatbot.close()
        raise e

# Send message example
async def send_chat_message(chatbot: ChatbotAPIClient, session_id: int, user_message: str):
    """Send message and handle response"""
    try:
        response = await chatbot.send_message(session_id, user_message)

        print(f"Bot: {response['message']}")
        print(f"Progress: {response['progress']}")

        if response['completed']:
            print("Chatbot completed! Exporting data...")
            exported_data = await chatbot.export_session(session_id)
            print(f"Collected data: {exported_data}")

            # Save to your system
            await save_company_data(exported_data)

        return response
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise
```

---

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

**Causes:**
- Missing Authorization header
- Invalid JWT token
- Expired JWT token
- JWT secret mismatch

**Solution:** Regenerate JWT token and retry request

---

#### 403 Forbidden
```json
{
  "detail": "User account is inactive"
}
```

**Causes:**
- User account is disabled in the chatbot system

**Solution:** Contact system administrator

---

#### 404 Not Found
```json
{
  "detail": "Chat session not found"
}
```

**Causes:**
- Invalid session_id
- Session belongs to another user
- Session was deleted

**Solution:** Create new session or verify session_id

---

#### 500 Internal Server Error
```json
{
  "detail": "An error occurred while processing your message: ..."
}
```

**Causes:**
- Database connection issues
- OpenAI API errors (if AI mode enabled)
- Internal server errors

**Solution:** Retry request or contact system administrator

---

### Error Handling Best Practices

```javascript
async function sendMessageWithRetry(chatbot, sessionId, message, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await chatbot.sendMessage(sessionId, message);
    } catch (error) {
      if (error.response) {
        const status = error.response.status;

        // Don't retry on authentication errors
        if (status === 401 || status === 403) {
          throw new Error('Authentication failed. Please login again.');
        }

        // Don't retry on not found errors
        if (status === 404) {
          throw new Error('Session not found. Please create a new session.');
        }

        // Retry on server errors
        if (status >= 500 && attempt < maxRetries) {
          console.log(`Attempt ${attempt} failed. Retrying...`);
          await sleep(1000 * attempt); // Exponential backoff
          continue;
        }
      }

      throw error;
    }
  }

  throw new Error('Max retries exceeded');
}
```

---

## Best Practices

### 1. Token Management

- **Generate tokens on-demand** - Create a new token for each chatbot session
- **Set appropriate expiration** - 24 hours is recommended
- **Secure storage** - Never expose JWT tokens in client-side code
- **Validate tokens** - Always call `/api/auth/me` before starting a session

### 2. Session Management

- **Check for existing sessions** - Use `/api/chatbot/sessions/latest` to resume sessions
- **Store session_id** - Save session_id in your application state
- **Handle session completion** - Export data when `completed: true`

### 3. User Experience

- **Show progress** - Display the `progress` object to users
- **Handle long responses** - Set appropriate timeouts for AI responses
- **Error messages** - Show user-friendly error messages
- **Loading states** - Display loading indicators during API calls

### 4. Data Handling

- **Export data immediately** - Call `/api/chatbot/export/{session_id}` when session completes
- **Validate exported data** - Check for null values before storing
- **Backup strategy** - Store raw responses in case of processing errors

### 5. Performance

- **Connection pooling** - Reuse HTTP clients
- **Timeout settings** - Set appropriate timeouts (30s recommended)
- **Rate limiting** - Implement rate limiting on your side
- **Caching** - Cache session data to reduce API calls

---

## Testing

### API Documentation

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Testing with cURL

```bash
# Set your token
TOKEN="your-jwt-token"

# Verify authentication
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# Create new session
curl -X POST "http://localhost:8000/api/chatbot/sessions/new" \
  -H "Authorization: Bearer $TOKEN"

# Send message
curl -X POST "http://localhost:8000/api/chatbot/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我的公司是電子業",
    "session_id": 1
  }'

# Export data
curl -X GET "http://localhost:8000/api/chatbot/export/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Support

For technical support or questions:
- **Repository:** https://github.com/your-org/enterprise-solutions
- **Documentation:** See `CHATBOT_MIGRATION_GUIDE.md` for deployment details
- **Issues:** Submit issues to the repository

---

## Changelog

### v3.0.0 (Current)
- External JWT authentication
- Supabase PostgreSQL database
- AI-powered chatbot (OpenAI GPT-4o-mini)
- Auto user synchronization
- Chinese language support
- File upload and AI data extraction (PDF, DOCX, Images, TXT)

---

**Last Updated:** 2024-01-14
**API Version:** 3.0.0
