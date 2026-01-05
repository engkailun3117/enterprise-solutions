# Authentication & Authorization System

## Overview

This document describes the authentication and authorization system implemented for the Supplier Onboarding Platform.

## Features

### 1. User Authentication
- **JWT-based authentication** using Bearer tokens
- **Password hashing** with bcrypt
- **User registration** with email and username validation
- **Login/logout** functionality
- **Token-based API access** (24-hour token expiration)

### 2. Role-Based Access Control (RBAC)
Two user roles:
- **user**: Regular users who can register and submit supplier applications
- **admin**: Administrators who can review and approve/reject applications

### 3. Supplier Onboarding Workflow
- **One-time submission**: Each user can only submit ONE supplier application
- **Approval workflow**: Applications go through pending → approved/rejected states
- **Admin review**: Admins can approve or reject applications with reasons
- **Status tracking**: Users can view their application status in real-time

---

## Database Schema

### Users Table
```sql
users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
)
```

### Updated Company_Info Table
```sql
Company_Info (
    Company_ID VARCHAR(50) PRIMARY KEY,
    Company_Name VARCHAR(100) NOT NULL,
    Company_Head VARCHAR(80) NOT NULL,
    Company_Email VARCHAR(50) NOT NULL,
    Company_Link VARCHAR(200),
    user_id INTEGER NOT NULL REFERENCES users(id),
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    rejection_reason VARCHAR(500)
)
```

---

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

#### POST /api/auth/login
Login with username and password.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response:** Same as register

#### GET /api/auth/me
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2025-01-01T00:00:00"
}
```

---

### Company/Application Endpoints

#### POST /api/companies
Create a supplier application (authenticated users only, one-time).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "company_id": "12345678",
  "company_name": "智群科技股份有限公司",
  "company_head": "林小明",
  "company_email": "sales@example.com",
  "company_link": "https://www.example.com"
}
```

**Restrictions:**
- User must be authenticated
- Each user can only submit ONE application
- Company ID must be unique

#### GET /api/companies/my-application
Get the current user's application (authenticated users only).

**Headers:**
```
Authorization: Bearer <token>
```

#### GET /api/companies/{company_id}
Get a specific company application.

**Authorization:**
- Regular users: Can only view their own application
- Admins: Can view any application

---

### Admin Endpoints

#### GET /api/admin/applications
Get all applications with optional status filter (admin only).

**Query Parameters:**
- `status_filter`: optional (pending, approved, rejected)
- `skip`: pagination offset (default: 0)
- `limit`: results per page (default: 100)

**Headers:**
```
Authorization: Bearer <admin_token>
```

#### PUT /api/admin/applications/{company_id}/review
Approve or reject an application (admin only).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**
```json
{
  "action": "approve"
}
```

or

```json
{
  "action": "reject",
  "rejection_reason": "缺少必要文件"
}
```

#### GET /api/admin/stats
Get statistics about applications (admin only).

**Response:**
```json
{
  "total_applications": 100,
  "pending": 20,
  "approved": 70,
  "rejected": 10
}
```

---

## Frontend Pages

### Public Pages
- `/` - Landing page
- `/login` - Login page
- `/register` - Registration page

### User Pages (Authentication Required)
- `/dashboard` - User dashboard (view application status)
- `/onboarding` - Submit supplier application (one-time only)

### Admin Pages (Admin Role Required)
- `/admin/review` - Review and manage all applications

---

## User Flows

### New User Registration Flow
1. User visits `/` and clicks "立即註冊"
2. User fills out registration form on `/register`
3. Backend creates user account with default `user` role
4. User is automatically logged in and redirected to `/dashboard`
5. From dashboard, user can submit supplier application

### Supplier Application Submission Flow
1. Authenticated user goes to `/onboarding`
2. System checks if user already submitted an application
3. If yes, redirect to `/dashboard`
4. If no, user fills out the form
5. Upon submission, application status is set to `pending`
6. User is redirected to `/dashboard` to view status

### Admin Review Flow
1. Admin logs in and is redirected to `/admin/review`
2. Admin sees all applications with filter options
3. Admin can:
   - View application details
   - Approve applications
   - Reject applications with a reason
4. Upon review, application status changes to `approved` or `rejected`
5. Stats are updated in real-time

---

## Security Features

### Backend Security
- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Signed with SECRET_KEY
- **Token Expiration**: 24 hours
- **Role-Based Access Control**: Middleware checks user roles
- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **CSRF Protection**: Not needed (token-based auth)

### Frontend Security
- **Secure Storage**: Tokens stored in localStorage
- **Route Guards**: Authentication checks on protected pages
- **Role-Based UI**: Different interfaces for users vs admins
- **Auto-redirect**: Unauthenticated users redirected to login

---

## Configuration

### Backend Environment Variables

Add to `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@host/database
SECRET_KEY=your-super-secret-key-change-this-in-production
API_HOST=0.0.0.0
API_PORT=8000
```

**Important:** Change `SECRET_KEY` to a random string in production!

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Creating an Admin User

Since the default role is `user`, you need to manually create or promote an admin user.

### Option 1: Direct Database Update
```sql
UPDATE users SET role = 'admin' WHERE username = 'your_username';
```

### Option 2: Python Script
Create `backend/create_admin.py`:
```python
from database import SessionLocal
from models import User, UserRole
from auth import get_password_hash

db = SessionLocal()

# Check if admin exists
admin = db.query(User).filter(User.username == "admin").first()

if not admin:
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    print("Admin user created!")
else:
    print("Admin user already exists")

db.close()
```

Run:
```bash
cd backend
python create_admin.py
```

---

## Migration from Old System

If you have existing company data without user associations:

1. **Backup your database** first
2. Create a default admin user
3. Update existing records to link to admin user:
```sql
UPDATE "Company_Info"
SET user_id = (SELECT id FROM users WHERE role = 'admin' LIMIT 1),
    status = 'approved',
    created_at = NOW()
WHERE user_id IS NULL;
```

---

## Testing

### Test User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Test Authenticated Request
```bash
TOKEN="your_token_here"

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Issue: "Could not validate credentials"
- Check if token is expired (24 hours)
- Verify token is included in Authorization header
- Ensure SECRET_KEY hasn't changed

### Issue: "Admin access required"
- Verify user role is 'admin' in database
- Check if correct token is being used

### Issue: "You have already submitted an application"
- Each user can only submit ONE application
- Check database for existing application
- This is by design, not a bug

### Issue: Can't create admin user
- Use direct database update or Python script
- Default registration creates 'user' role only

---

## Best Practices

1. **Never commit SECRET_KEY** to version control
2. **Use HTTPS** in production
3. **Implement rate limiting** for login endpoints
4. **Add email verification** for registration
5. **Implement password reset** functionality
6. **Add audit logging** for admin actions
7. **Use refresh tokens** for better security
8. **Implement CORS** properly for production

---

## Future Enhancements

- [ ] Email verification on registration
- [ ] Password reset functionality
- [ ] Refresh token mechanism
- [ ] Two-factor authentication (2FA)
- [ ] Email notifications for status changes
- [ ] File upload for company documents
- [ ] Application revision/resubmission
- [ ] Admin notes/comments on applications
- [ ] Activity audit log
- [ ] Rate limiting on sensitive endpoints
