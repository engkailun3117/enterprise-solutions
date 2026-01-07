#!/bin/bash
# Chatbot UI Verification Script

echo "🔍 Verifying AI Chatbot Setup..."
echo ""

# Check if company.vue has chatbot UI
echo "1️⃣ Checking frontend file..."
if grep -q "企業導入 AI 助理" frontend/pages/dashboard/company.vue; then
    echo "   ✅ Chatbot UI is in company.vue"
else
    echo "   ❌ Chatbot UI not found in company.vue"
    exit 1
fi

# Check backend files
echo ""
echo "2️⃣ Checking backend files..."
if [ -f "backend/ai_chatbot_handler.py" ]; then
    echo "   ✅ AI chatbot handler exists"
else
    echo "   ❌ AI chatbot handler missing"
fi

if [ -f "backend/chatbot_handler.py" ]; then
    echo "   ✅ Rule-based chatbot handler exists"
else
    echo "   ❌ Rule-based chatbot handler missing"
fi

# Check .env configuration
echo ""
echo "3️⃣ Checking configuration..."
if [ -f "backend/.env" ]; then
    echo "   ✅ .env file exists"

    if grep -q "^DATABASE_URL=postgresql://" backend/.env; then
        echo "   ✅ DATABASE_URL is configured"
    else
        echo "   ❌ DATABASE_URL not configured properly"
    fi

    if grep -q "^OPENAI_API_KEY=sk-" backend/.env; then
        echo "   ✅ OPENAI_API_KEY is configured"
    else
        echo "   ⚠️  OPENAI_API_KEY not configured (chatbot will use rule-based mode)"
    fi
else
    echo "   ❌ .env file not found"
fi

# Check dependencies
echo ""
echo "4️⃣ Checking dependencies..."
if grep -q "openai" backend/requirements.txt; then
    echo "   ✅ OpenAI dependency in requirements.txt"
else
    echo "   ❌ OpenAI dependency missing"
fi

echo ""
echo "======================================"
echo "📋 What you should see on the page:"
echo "======================================"
echo ""
echo "When you visit http://localhost:3000/dashboard/company"
echo ""
echo "You should see at the TOP:"
echo ""
echo "┌─────────────────────────────────────┐"
echo "│ 🤖 企業導入 AI 助理         [展開] │"
echo "├─────────────────────────────────────┤"
echo "│                                     │"
echo "│  💬 Chat messages appear here      │"
echo "│                                     │"
echo "│  Progress bar: ████░░░░░ 5/10      │"
echo "│                                     │"
echo "│  [匯出 JSON] [新對話]               │"
echo "│                                     │"
echo "│  [Input box...........] [發送]     │"
echo "│                                     │"
echo "└─────────────────────────────────────┘"
echo ""
echo "Below that, you'll see the original:"
echo "🏢 企業識別資訊 (Identity)"
echo ""

echo "======================================"
echo "🚀 To start the application:"
echo "======================================"
echo ""
echo "Option 1: Quick start"
echo "  ./start.sh"
echo ""
echo "Option 2: Manual start"
echo "  # Terminal 1:"
echo "  cd backend && python main.py"
echo ""
echo "  # Terminal 2:"
echo "  cd frontend && npm run dev"
echo ""
