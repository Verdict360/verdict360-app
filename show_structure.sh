#!/bin/bash
echo "📁 VERDICT360 PROJECT STRUCTURE"
echo "================================"
echo ""

echo "🔧 CORE COMPONENTS:"
tree -L 3 -I 'node_modules|__pycache__|.git|*.pyc|dist|build|.next|chroma_db|backups' || {
    echo "Using ls fallback (install tree with: brew install tree)"
    echo "/"
    ls -la | grep ^d | awk '{print "├── " $9}' | grep -v "^\.$\|^\.\.$"
    for dir in web api-python mobile api docker scripts; do
        if [ -d "$dir" ]; then
            echo "├── $dir/"
            ls -la "$dir" 2>/dev/null | grep ^d | head -5 | awk '{print "│   ├── " $9}' | grep -v "^\.$\|^\.\.$"
        fi
    done
}

echo ""
echo "📄 KEY CONFIGURATION FILES:"
find . -maxdepth 2 \( -name "*.json" -o -name "docker-compose*.yml" -o -name ".env*" -o -name "*.md" \) | grep -v node_modules | sort

echo ""
echo "🚀 SERVICES STATUS:"
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose ps 2>/dev/null || echo "Docker services not running"
else
    echo "Docker Compose not available"
fi

echo ""
echo "📊 PROJECT STATS:"
echo "- Web components: $(find web -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')"
echo "- API endpoints: $(find api-python -name "*.py" 2>/dev/null | grep -E "(main|router)" | wc -l | tr -d ' ')"
echo "- Mobile screens: $(find mobile -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')"
