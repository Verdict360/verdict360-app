#!/bin/bash

echo "🧪 Testing Verdict360 Complete Vector Search Flow"
echo "================================================="

# Test 1: Check if Python API is running
echo ""
echo "1. Testing Python API health..."
curl -s http://localhost:8001/health | jq . || echo "❌ Python API not responding"

# Test 2: Test vector store directly
echo ""
echo "2. Testing vector store initialization..."
cd api-python
python test_vector_store.py
test_result=$?
cd ..

if [ $test_result -eq 0 ]; then
    echo "✅ Vector store test passed"
else
    echo "❌ Vector store test failed"
fi

# Test 3: Check if web app builds
echo ""
echo "3. Testing web app build..."
cd web
npm run build --silent && echo "✅ Web app builds successfully" || echo "❌ Web app build failed"
cd ..

# Test 4: Test document upload endpoint (mock)
echo ""
echo "4. Testing document upload endpoint..."
curl -s -X POST http://localhost:8001/documents/upload \
  -H "Authorization: Bearer demo" \
  -F "file=@README.md" \
  -F "title=Test Document" \
  -F "document_type=article" \
  -F "jurisdiction=South Africa" | jq . || echo "❌ Upload endpoint not responding"

# Test 5: Test search endpoint (mock)
echo ""
echo "5. Testing search endpoint..."
curl -s -X POST http://localhost:8001/documents/search \
  -H "Authorization: Bearer demo" \
  -F "query=legal document" \
  -F "limit=3" | jq . || echo "❌ Search endpoint not responding"

echo ""
echo "🎉 Flow testing complete!"
echo ""
echo "Next steps to test manually:"
echo "1. Start Python API: cd api-python && uvicorn app.main:app --reload --port 8001"
echo "2. Start Web App: cd web && npm run dev"
echo "3. Visit http://localhost:3000/legal-search"
echo "4. Upload a document and then search for it"
