#!/bin/sh
set -e

echo "🚀 Starting Nginx..."

# Test nginx configuration
if ! nginx -t; then
    echo "❌ Nginx configuration test failed!"
    exit 1
fi

echo "✅ Nginx configuration is valid"

# Start nginx in foreground
echo "🌐 Starting nginx on port 8080..."
exec nginx -g "daemon off;"

