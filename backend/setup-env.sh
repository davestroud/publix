#!/bin/bash
# Helper script to add DATABASE_URL to .env file

ENV_FILE=".env"
DB_URL="postgresql://publix_admin:Kk8pKDxT00jm+tMbusEXYG+oRqHZ2jZp@publix-expansion-db.co1dd6f49wfo.us-east-1.rds.amazonaws.com:5432/publix_db"

echo "Setting up DATABASE_URL in .env file..."

# Check if DATABASE_URL already exists
if grep -q "^DATABASE_URL=" "$ENV_FILE" 2>/dev/null; then
    echo "⚠️  DATABASE_URL already exists in .env file"
    echo "Current value:"
    grep "^DATABASE_URL=" "$ENV_FILE"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old DATABASE_URL line
        sed -i.bak '/^DATABASE_URL=/d' "$ENV_FILE"
        echo "DATABASE_URL=$DB_URL" >> "$ENV_FILE"
        echo "✅ Updated DATABASE_URL in .env file"
    else
        echo "Keeping existing DATABASE_URL"
    fi
else
    # Add DATABASE_URL if it doesn't exist
    echo "DATABASE_URL=$DB_URL" >> "$ENV_FILE"
    echo "✅ Added DATABASE_URL to .env file"
fi

echo ""
echo "Current DATABASE_URL:"
grep "^DATABASE_URL=" "$ENV_FILE"

