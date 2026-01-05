# Supplier Onboarding Platform

A full-stack application for managing supplier onboarding with Nuxt 3 frontend and FastAPI backend, integrated with Neon.tech PostgreSQL database.

## 🆕 Version 2.0 - Authentication & Approval Workflow

**New in v2.0:**
- 🔐 **User Authentication** - JWT-based login/registration system
- 👥 **Role-Based Access Control** - User and Admin roles
- ✅ **Approval Workflow** - Admins review and approve/reject applications
- 🔒 **One-Time Submission** - Each user can only submit one supplier application
- 📊 **Admin Dashboard** - Manage all applications with statistics
- 👤 **User Dashboard** - Track application status in real-time

📖 **See [AUTHENTICATION.md](./AUTHENTICATION.md) for complete authentication documentation**

## 🏗️ Tech Stack

- **Frontend**: Nuxt 3 + Vue 3 + Nuxt UI
- **Backend**: FastAPI + SQLAlchemy + JWT Authentication
- **Database**: Neon.tech PostgreSQL (Free Tier)
- **Language**: Python 3.9+ & TypeScript
- **Security**: JWT tokens, bcrypt password hashing, RBAC

## 📋 Features

### Authentication & Authorization
- ✅ User registration and login
- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (User/Admin)
- ✅ Protected routes and API endpoints

### Supplier Onboarding
- ✅ Supplier company information submission
- ✅ One-time application per user
- ✅ Application status tracking (pending/approved/rejected)
- ✅ Form validation (frontend and backend)
- ✅ Database integration with Neon.tech
- ✅ RESTful API endpoints

### Admin Features
- ✅ Review all supplier applications
- ✅ Approve/reject applications with reasons
- ✅ Filter applications by status
- ✅ View statistics dashboard
- ✅ Responsive UI with Nuxt UI components
- ✅ Success/Error notifications

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Neon.tech account with a database created

### 1. Environment Configuration

Create the `.env` file in the backend directory with your Neon.tech credentials:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your Neon.tech database URL and a secret key:

```env
DATABASE_URL=postgresql://neondb_owner:your-password@ep-hostname.region.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=your-super-secret-key-change-this-in-production
API_HOST=0.0.0.0
API_PORT=8000
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**How to get your Neon.tech DATABASE_URL:**
1. Log in to your Neon.tech dashboard at https://console.neon.tech
2. Select your project
3. Navigate to the "Connection Details" section
4. Copy the **full** connection string (must include `@ep-...neon.tech` hostname part)

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

### 3. Create Admin User

**IMPORTANT:** After starting the backend for the first time, create an admin user:

```bash
cd backend
python create_admin.py
```

Follow the interactive prompts to create your admin account. This account will have access to the admin dashboard to review and approve supplier applications.

**Quick create (non-interactive):**
```bash
python create_admin.py admin admin@example.com secure_password
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Documentation: `http://localhost:8000/redoc`

### 3. Frontend Setup

Install Node.js dependencies:

```bash
cd frontend
npm install
```

Start the Nuxt development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔄 Migrating Existing Data

If you have existing `Company_Info` records from before v2.0, you need to link them to a user:

**Option 1: Link to Admin User (Keep Old Data)**
```sql
-- Run this in Neon.tech SQL Editor
UPDATE "Company_Info"
SET user_id = (SELECT id FROM users WHERE role = 'admin' LIMIT 1),
    status = 'approved',
    created_at = NOW()
WHERE user_id IS NULL;
```

**Option 2: Delete Old Data (Fresh Start)**
```sql
DELETE FROM "Company_Info" WHERE user_id IS NULL;
```

## 📊 Database Schema

### Users Table
| Column Name      | Type         | Constraints    | Description                |
|-----------------|--------------|----------------|----------------------------|
| id              | INTEGER      | PRIMARY KEY    | Auto-increment user ID     |
| username        | VARCHAR(50)  | UNIQUE, NOT NULL | Username                  |
| email           | VARCHAR(100) | UNIQUE, NOT NULL | Email address             |
| hashed_password | VARCHAR(255) | NOT NULL       | Bcrypt hashed password     |
| role            | ENUM         | NOT NULL       | 'user' or 'admin'          |
| created_at      | TIMESTAMP    | NOT NULL       | Account creation time      |

### Company_Info Table
| Column Name      | Type         | Constraints    | Description                |
|-----------------|--------------|----------------|----------------------------|
| Company_ID      | VARCHAR(50)  | PRIMARY KEY    | 統一編號 (Business ID)      |
| Company_Name    | VARCHAR(100) | NOT NULL       | 企業名稱 (Company Name)     |
| Company_Head    | VARCHAR(80)  | NOT NULL       | 負責人 (Person in Charge)   |
| Company_Email   | VARCHAR(50)  | NOT NULL       | 聯絡 Email (Contact Email)  |
| Company_Link    | VARCHAR(200) | NULLABLE       | 公司網址 (Company Website)  |
| user_id         | INTEGER      | FK → users.id  | User who submitted         |
| status          | ENUM         | NOT NULL       | pending/approved/rejected  |
| reviewed_by     | INTEGER      | FK → users.id  | Admin who reviewed         |
| reviewed_at     | TIMESTAMP    | NULLABLE       | Review timestamp           |
| created_at      | TIMESTAMP    | NOT NULL       | Submission timestamp       |
| rejection_reason| VARCHAR(500) | NULLABLE       | Reason if rejected         |

## 🔌 API Endpoints

### Authentication Endpoints

**Register New User**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Get Current User**
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Company/Application Endpoints (Authenticated)

**Submit Supplier Application**
```http
POST /api/companies
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": "23456789",
  "company_name": "智群科技股份有限公司",
  "company_head": "林小明",
  "company_email": "sales@accton.com",
  "company_link": "https://www.accton.com"
}
```

**Get My Application**
```http
GET /api/companies/my-application
Authorization: Bearer <token>
```

**Get Specific Application**
```http
GET /api/companies/{company_id}
Authorization: Bearer <token>
```

### Admin Endpoints (Admin Only)

**Get All Applications**
```http
GET /api/admin/applications?status_filter=pending
Authorization: Bearer <admin_token>
```

**Review Application**
```http
PUT /api/admin/applications/{company_id}/review
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "action": "approve"
}
```

**Get Statistics**
```http
GET /api/admin/stats
Authorization: Bearer <admin_token>
```

## 🧪 Testing

### Test User Workflow

1. **Visit** http://localhost:3000
2. **Register** a new user account
3. **Login** with your credentials
4. **Submit** a supplier application (one-time only)
5. **Track** application status in dashboard

### Test Admin Workflow

1. **Login** as admin at http://localhost:3000/login
2. **Review** pending applications at http://localhost:3000/admin/review
3. **Approve/Reject** applications with optional reasons
4. **View** statistics dashboard

### Test Backend API

Using curl:
```bash
# Health check
curl http://localhost:8000/

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}' \
  | jq -r '.access_token')

# Submit application (requires token)
curl -X POST http://localhost:8000/api/companies \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "company_id": "23456789",
    "company_name": "智群科技股份有限公司",
    "company_head": "林小明",
    "company_email": "sales@accton.com",
    "company_link": "https://www.accton.com"
  }'
```

Or use the interactive API documentation at `http://localhost:8000/docs`

## 📁 Project Structure

```
AI_recommend/
├── backend/
│   ├── main.py              # FastAPI application & API routes
│   ├── auth.py              # JWT authentication & authorization
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models (User, CompanyInfo)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── create_admin.py      # Admin user creation script
│   ├── setup_database.sql   # Manual database setup (if needed)
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (not in git)
├── frontend/
│   ├── pages/
│   │   ├── index.vue         # Landing page
│   │   ├── login.vue         # Login page
│   │   ├── register.vue      # Registration page
│   │   ├── dashboard.vue     # User dashboard
│   │   ├── onboarding.vue    # Supplier application form
│   │   └── admin/
│   │       └── review.vue    # Admin review dashboard
│   ├── composables/
│   │   └── useApi.ts         # API integration with auth
│   ├── app.vue               # Root component
│   ├── nuxt.config.ts        # Nuxt configuration
│   └── package.json          # Node.js dependencies
├── AUTHENTICATION.md         # Complete auth documentation
├── .env.example             # Example environment variables
└── README.md                # This file
```

## 🔒 Security Notes

- ✅ **JWT tokens** used for authentication (24-hour expiration)
- ✅ **Bcrypt** password hashing for secure storage
- ✅ **Role-based access control** (User/Admin)
- ✅ **Protected API endpoints** require authentication
- ⚠️ **Never commit `.env`** file to version control
- ⚠️ **Generate secure SECRET_KEY** for production
- ⚠️ **Update CORS settings** in production to only allow your frontend domain
- ⚠️ **Use HTTPS** in production environments

## 🎨 UI Features

- Modern interface with Nuxt UI components
- JWT-based authentication
- Protected routes with auth guards
- Real-time application status tracking
- Admin dashboard with statistics
- Form validation (frontend + backend)
- Loading states and toast notifications
- Responsive design
- Chinese (Traditional) language support

## 📝 Future Enhancements

Potential features to add:

1. ✅ ~~Authentication~~ - **DONE in v2.0**
2. ✅ ~~Admin Panel~~ - **DONE in v2.0**
3. **Email Notifications** - Send emails on status changes
4. **Refresh Tokens** - Implement refresh token mechanism
5. **AI Integration** - Implement the "AI 資料整合" step
6. **File Upload** - Allow uploading company documents
7. **Password Reset** - Email-based password reset
8. **Two-Factor Authentication** - Add 2FA for extra security
9. **LangGraph Integration** - AI-powered chat assistance
10. **Email Verification** - Verify email on registration

## 🐛 Troubleshooting

### Authentication Issues

**Problem:** 401 Unauthorized errors
```
Solution:
1. Ensure you're logged in
2. Check if token exists: localStorage.getItem('access_token')
3. Token may be expired (24h) - login again
4. SECRET_KEY must be set in backend/.env
```

**Problem:** "Could not validate credentials"
```
Solution:
1. Verify SECRET_KEY in .env matches what backend is using
2. Restart backend after changing SECRET_KEY
3. Clear browser localStorage and login again
4. Check backend logs for detailed JWT errors
```

**Problem:** "Subject must be a string" JWT error
```
Solution: This is fixed in latest code (v2.0)
- User IDs are now converted to strings in JWT tokens
```

### Database Issues

**Problem:** "user_id cannot be null" or validation errors
```
Solution: Migrate existing Company_Info records
UPDATE "Company_Info"
SET user_id = (SELECT id FROM users WHERE role = 'admin' LIMIT 1),
    status = 'approved'
WHERE user_id IS NULL;
```

**Problem:** Database connection issues
```
Solution:
- Verify DATABASE_URL in .env is correct
- Ensure Neon.tech project is active (free tier may pause)
- Check your IP is allowed in Neon.tech settings
```

**Problem:** ENUM type errors
```
Solution: Run backend/setup_database.sql in Neon.tech SQL Editor
This creates the required ENUM types (userrole, applicationstatus)
```

### Installation Issues

**Problem:** psycopg2-binary installation fails (Python 3.13)
```
Solution: Use psycopg2-binary==2.9.10 or higher
Or use Python 3.12 (recommended for better package support)
```

**Problem:** bcrypt/passlib compatibility errors
```
Solution:
pip uninstall bcrypt passlib -y
pip install passlib==1.7.4 bcrypt==4.0.1
```

**Problem:** pydantic requires Rust compiler
```
Solution: Upgrade to pydantic==2.10.5 or higher
(Has pre-built wheels for Python 3.13)
```

### Frontend Issues

**Problem:** "GET /api/companies/my-application 401"
```
Solution:
1. Check if logged in: api.isAuthenticated()
2. Check token in localStorage
3. Clear cache and login again
```

**Problem:** Admin dashboard shows "目前沒有的申請"
```
Solution:
- Existing records need user_id (see Database Issues above)
- Check backend logs for errors
- Verify admin token is valid
```

### General Issues

**Problem:** CORS errors
```
Solution:
- Backend should run on http://localhost:8000
- Frontend should run on http://localhost:3000
- Check CORS settings in backend/main.py
```

**Problem:** Module not found errors
```
Solution:
- Backend: pip install -r backend/requirements.txt
- Frontend: npm install (in frontend/)
- Frontend: npm run prepare (generates Nuxt types)
```

**Need more help?** See [AUTHENTICATION.md](./AUTHENTICATION.md) for detailed documentation.

## 📄 License

This project is for testing and development purposes.
