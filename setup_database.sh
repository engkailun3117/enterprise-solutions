#!/bin/bash

echo "=================================="
echo "Database Setup for Enterprise Solutions"
echo "=================================="
echo ""
echo "Please provide your Neon PostgreSQL connection string."
echo "Format: postgresql://username:password@host/database"
echo ""
echo "You can find this in your Neon dashboard:"
echo "1. Go to https://neon.tech"
echo "2. Select your project"
echo "3. Go to 'Connection Details'"
echo "4. Copy the connection string"
echo ""
read -p "Enter your DATABASE_URL: " db_url

# Create .env file
cat > /home/user/enterprise-solutions/backend/.env << EOF
# Database Configuration
DATABASE_URL=$db_url

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=$(openssl rand -hex 32)

# OpenAI Configuration (optional - for AI chatbot)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
USE_AI_CHATBOT=true
EOF

echo ""
echo "✓ .env file created successfully!"
echo ""
echo "Next steps:"
echo "1. cd /home/user/enterprise-solutions/backend"
echo "2. python3 main.py"
echo ""
