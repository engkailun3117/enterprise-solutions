# Quick Setup Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Configure Neon.tech Database

1. **Get your Neon.tech connection string:**
   - Go to https://console.neon.tech
   - Select your project
   - Click on "Connection Details"
   - Copy the connection string (looks like: `postgresql://user:password@ep-hostname.region.aws.neon.tech/dbname?sslmode=require`)

2. **Create your .env file in the backend folder:**
   ```bash
   cd backend
   cp .env.example .env
   ```

3. **Edit backend/.env and paste your connection string:**
   ```env
   DATABASE_URL=postgresql://neondb_owner:your-password@ep-hostname.region.aws.neon.tech/neondb?sslmode=require
   ```

   **Important:** Make sure to include the full hostname (the `@ep-....neon.tech` part)!

### Step 2: Start the Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# (Optional) Test your .env configuration
python test_env.py

# Start the server
python main.py
```

The API will start at `http://localhost:8000`

✅ **Verify it works:** Visit http://localhost:8000/docs to see the API documentation

### Step 3: Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run prepare   # IMPORTANT: Generates Nuxt types for useRuntimeConfig, $fetch, etc.
npm run dev
```

The frontend will start at `http://localhost:3000`

✅ **Verify it works:** Open http://localhost:3000 in your browser

**Note:** The `npm run prepare` command is crucial - it generates TypeScript definitions for Nuxt's auto-imports like `useRuntimeConfig` and `$fetch`. If you skip this, you'll get "Cannot find name" errors.

### Step 4: Test the Integration

1. Open http://localhost:3000 in your browser
2. Fill in the supplier onboarding form:
   - **統一編號**: 23456789
   - **企業名稱**: 智群科技股份有限公司
   - **負責人**: 林小明
   - **聯絡 Email**: sales@accton.com
   - **公司網址**: https://www.accton.com
3. Click "提交申請"
4. You should see a success modal!

### Step 5: Verify Data in Database

You can verify the data was saved in two ways:

**Method 1: Using the API**
Visit http://localhost:8000/api/companies to see all companies

**Method 2: Using Neon.tech Console**
1. Go to https://console.neon.tech
2. Select your project
3. Go to "SQL Editor"
4. Run: `SELECT * FROM "Company_Info";`

## 🎉 You're Done!

Your supplier onboarding system is now running! The form data is being saved to your Neon.tech PostgreSQL database.

## 📚 What's Included

- ✅ Full-stack application (Nuxt 3 + FastAPI)
- ✅ Database integration with Neon.tech
- ✅ RESTful API with full CRUD operations
- ✅ Form validation
- ✅ Error handling
- ✅ Success notifications
- ✅ Responsive UI

## 🔧 Troubleshooting

### "Connection refused" error
- Make sure both backend (port 8000) and frontend (port 3000) are running
- Check that your Neon.tech database is active

### "Module not found" error
- Run `pip install -r requirements.txt` in backend/
- Run `npm install` in frontend/

### "Cannot find name 'useRuntimeConfig'" or "$fetch" errors
- Run `npm run prepare` in frontend/ directory
- Restart your IDE/editor
- In VS Code: Press `Ctrl+Shift+P` → "TypeScript: Restart TS Server"

### Database connection error
- Verify your DATABASE_URL in .env is correct
- Check that your Neon.tech project is not paused (free tier auto-pauses after inactivity)

## 📖 Next Steps

See the main [README.md](README.md) for:
- Detailed API documentation
- Database schema information
- Production deployment tips
- Security considerations
