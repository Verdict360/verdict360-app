#!/bin/bash
echo "🎨 FRONTEND CONTEXT (Next.js/React)"
echo "=================================="
echo ""

echo "📱 CURRENT PAGES:"
find web/app -name "page.tsx" | sed 's/web\/app//g' | sed 's/\/page.tsx//g' | sort

echo ""
echo "🧩 KEY COMPONENTS:"
find web/components -name "*.tsx" | head -8 | xargs -I {} basename {} .tsx

echo ""
echo "🔧 PACKAGE.JSON DEPENDENCIES:"
if [ -f "web/package.json" ]; then
    grep -A 10 '"dependencies"' web/package.json | grep -E '"|:' | head -8
fi
