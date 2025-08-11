#!/bin/bash

# Railway Deployment Script for Odoo SportsPit
# This script ensures successful deployment without crashes

echo "🚀 Starting Railway deployment for Odoo SportsPit..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Environment variables for Railway
export RAILWAY_TOKEN="${RAILWAY_TOKEN:-4c02d552-4ed0-4787-8d3f-bf00eb20004a}"
export PROJECT_ID="daa4ac63-d597-4ba7-b10e-1baf84cbacad"

echo "📦 Building optimized Docker image..."

# Create a temporary deployment config
cat > /tmp/railway-deploy.toml << EOF
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile.railway"

[deploy]
numReplicas = 1
startCommand = "/start.sh"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[[services]]
name = "odoo-sportpit"
type = "web"
port = 8069

[services.healthcheck]
path = "/web/database/selector"
timeout = 300
interval = 30
EOF

echo "🔗 Linking to Railway project..."
railway link -p "$PROJECT_ID" 2>/dev/null || {
    echo "⚠️  Could not link project. Please run: railway login"
    exit 1
}

echo "🚂 Deploying to Railway..."
railway up --detach

echo "✅ Deployment initiated!"
echo ""
echo "📊 Monitor deployment status:"
echo "   railway logs -f"
echo ""
echo "🌐 Your app will be available at:"
echo "   https://odoo-sportpit.up.railway.app"
echo ""
echo "⏱️  Note: Initial startup may take 2-3 minutes"
echo "   Odoo needs time to initialize the database"