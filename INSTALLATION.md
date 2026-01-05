# Frontend Setup - Detailed Instructions

## Prerequisites

Make sure you have installed on your local device:

### Required Software

1. **Node.js** (version 18 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`
   - Should show: v18.x.x or higher

2. **npm** (comes with Node.js)
   - Verify installation: `npm --version`
   - Should show: 9.x.x or higher

3. **Python** (version 3.9 or higher) for backend
   - Download from: https://www.python.org/
   - Verify installation: `python --version` or `python3 --version`

## Step-by-Step Frontend Setup

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

This will install:
- Nuxt 3
- Vue 3
- Nuxt UI
- TypeScript
- All required dependencies

### Step 2: Generate Nuxt Type Definitions

After installation, run:

```bash
npm run prepare
```

Or:

```bash
npx nuxt prepare
```

**This is crucial!** This command:
- Generates `.nuxt` directory
- Creates TypeScript definitions
- Sets up auto-imports for `useRuntimeConfig`, `$fetch`, etc.
- Configures IDE intellisense

### Step 3: Verify Setup

You should now see a `.nuxt` folder in the frontend directory. This contains all the type definitions.

### Step 4: Start Development Server

```bash
npm run dev
```

The server will start at `http://localhost:3000`

## Common Issues & Solutions

### Issue 1: "Cannot find name 'useRuntimeConfig'"

**Solution:**
```bash
cd frontend
npm install
npm run prepare  # This generates the .nuxt types
```

Then restart your IDE/editor.

### Issue 2: "Cannot find name '$fetch'"

**Solution:**
Same as above - run `npm run prepare` and restart your IDE.

### Issue 3: TypeScript errors in IDE but code runs fine

**Solution:**
1. Make sure `tsconfig.json` exists in frontend folder
2. Restart your IDE (VS Code, WebStorm, etc.)
3. In VS Code, try: `Ctrl+Shift+P` → "TypeScript: Restart TS Server"

### Issue 4: ".nuxt folder not created"

**Solution:**
```bash
rm -rf node_modules .nuxt
npm install
npm run prepare
```

## What Gets Installed?

### Frontend Dependencies:
- `nuxt` (v3.9.0) - The Nuxt framework
- `vue` (v3.4.0) - Vue.js
- `@nuxt/ui` (v2.11.0) - UI component library
- `typescript` - TypeScript support
- `@nuxt/devtools` - Development tools

### Auto-Imports Provided by Nuxt:
After running `npm run prepare`, these will be available without imports:
- `useRuntimeConfig()` - Access runtime configuration
- `$fetch()` - Enhanced fetch for API calls
- `ref()`, `computed()`, `watch()` - Vue composables
- `useRouter()`, `useRoute()` - Router composables
- `useState()` - Nuxt state management
- And many more...

## IDE Setup (Optional but Recommended)

### For Visual Studio Code:

Install these extensions:
1. **Volar** (Vue Language Features) - Official Vue extension
2. **TypeScript Vue Plugin (Volar)** - TypeScript support for Vue
3. **Nuxt** - Nuxt.js support

### For WebStorm/IntelliJ:
- Vue.js plugin should be installed by default
- Make sure TypeScript support is enabled

## Backend Setup

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Database

Create `.env` file in the backend directory:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and add your Neon.tech connection string:

```env
DATABASE_URL=postgresql://neondb_owner:password@ep-hostname.region.aws.neon.tech/neondb?sslmode=require
```

**Important:** Get the complete connection string from https://console.neon.tech (must include the `@ep-...neon.tech` hostname!)

This installs:
- FastAPI
- Uvicorn (ASGI server)
- SQLAlchemy (ORM)
- psycopg2-binary (PostgreSQL driver)
- Pydantic (data validation)
- python-dotenv (environment variables)

## Full Setup Commands Summary

```bash
# Frontend
cd frontend
npm install           # Install dependencies
npm run prepare      # Generate Nuxt types (IMPORTANT!)
npm run dev          # Start dev server

# Backend (in a new terminal)
cd backend
pip install -r requirements.txt
python main.py       # Start API server
```

## Verification Checklist

- [ ] Node.js 18+ installed
- [ ] Python 3.9+ installed
- [ ] Ran `npm install` in frontend directory
- [ ] Ran `npm run prepare` in frontend directory
- [ ] `.nuxt` folder exists in frontend directory
- [ ] `tsconfig.json` exists in frontend directory
- [ ] IDE/editor restarted after setup
- [ ] Backend dependencies installed with pip
- [ ] `.env` file created with DATABASE_URL
- [ ] potential issue for setup: pydantic[email] needs to 另外下載


If all checked, you should be good to go! 
