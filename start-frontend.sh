#!/bin/bash

echo "🌐 Starting Verdict360 Frontend Development Server"
echo "=================================================="

# Change to web directory
cd "$(dirname "$0")/web"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🚀 Starting SvelteKit development server..."
echo "- Server will start on http://localhost:5173"
echo "- Browser will open automatically"
echo "- Press Ctrl+C to stop the server"
echo ""

# Start the development server with auto-open
npm run dev