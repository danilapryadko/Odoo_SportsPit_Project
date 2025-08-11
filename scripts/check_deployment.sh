#!/bin/bash

echo "=== Railway Deployment Monitor ==="
echo "Checking deployment status..."
echo ""

# Possible Railway URLs for the project
URLS=(
    "https://athletic-emotion.up.railway.app"
    "https://odoo-sportspit-project-production.up.railway.app"
    "https://odoo-sportspit-project.up.railway.app"
    "https://daa4ac63-d597-4ba7-b10e-1baf84cbacad.up.railway.app"
)

echo "Testing Railway endpoints:"
for url in "${URLS[@]}"; do
    echo -n "  $url ... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url/web/health" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ SUCCESS (HTTP $response)"
        echo ""
        echo "🎉 Deployment successful! Your Odoo instance is running at:"
        echo "   $url"
        echo ""
        echo "Admin panel: $url/web"
        exit 0
    elif [ "$response" = "000" ]; then
        echo "⏳ No response (deployment may be in progress)"
    else
        echo "❌ HTTP $response"
    fi
done

echo ""
echo "📊 Checking latest Git commit:"
git log --oneline -1

echo ""
echo "⚠️  Deployment may still be in progress. Railway typically takes 2-5 minutes."
echo "    Run this script again in a minute to check status."
echo ""
echo "To monitor in real-time, check Railway dashboard:"
echo "https://railway.app/project/daa4ac63-d597-4ba7-b10e-1baf84cbacad"