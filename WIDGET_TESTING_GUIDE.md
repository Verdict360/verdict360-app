# 🧪 Widget Testing Guide

## Overview
This guide explains how to use the three test pages to validate your Verdict360 Legal Chatbot Widget functionality.

## Prerequisites
- ✅ Development environment running (`./start-dev.sh`)
- ✅ All services healthy (API, Frontend, Database, Ollama)
- ✅ HTTP server for test files (`python3 -m http.server 9090`)

## Test Pages

### 1. 📈 **Conversion Widget Test** (`test-conversion-widget.html`)
**URL:** http://localhost:9090/test-conversion-widget.html

**Purpose:** Tests client acquisition features and conversion optimization

**What to Test:**
- ✅ Widget appears in bottom-right corner
- ✅ Firm branding displays correctly (Smith & Associates Legal)
- ✅ AI provides intelligent legal responses
- ✅ Conversion buttons appear: `[SCHEDULE_CONSULTATION]` and `[CONTACT_FIRM]`
- ✅ Emergency contact information is accessible
- ✅ Voice call functionality (if enabled)

**Test Scripts:**
```javascript
// Sample questions to test:
"I need help with a contract dispute"
"What are my rights in employment law?"
"I'm going through a divorce"
"My business needs legal advice"
```

**Expected Behavior:**
- Professional legal responses with South African law context
- Clear call-to-action buttons for client conversion
- Firm-specific contact information displayed
- Professional branding and theming

### 2. 🔗 **Widget Embedding Test** (`test-widget-embed.html`)
**URL:** http://localhost:9090/test-widget-embed.html

**Purpose:** Tests iframe embedding for law firm websites

**What to Test:**
- ✅ Widget loads properly in iframe
- ✅ Responsive design works on different screen sizes
- ✅ No cross-origin issues
- ✅ Widget integrates seamlessly with law firm website design
- ✅ Microphone/camera permissions work if needed

**Technical Validation:**
- Check browser console for errors
- Verify iframe security and sandboxing
- Test on mobile devices
- Validate accessibility features

**Integration Method:**
```html
<div class="widget-container">
    <iframe 
        src="http://localhost:5173/widget" 
        title="Legal Chatbot Assistant"
        allow="microphone; camera">
    </iframe>
</div>
```

### 3. 🔌 **API Test** (`test-widget-api.html`)
**URL:** http://localhost:9090/test-widget-api.html

**Purpose:** Tests API connectivity and response validation

**Test Scenarios:**

#### A. **SvelteKit Widget API Test**
- Tests standard widget integration
- Validates session management
- Checks response formatting

#### B. **Static Widget API Test**
- Tests external website integration
- Validates CORS configuration
- Checks context passing (firm info, page URL)

#### C. **Direct API Test**
- Tests core API functionality
- Validates error handling
- Checks response times

**API Endpoints Tested:**
```bash
POST http://localhost:8000/api/v1/simple-chat/
```

**Expected Response Format:**
```json
{
  "response": "Intelligent legal response...",
  "session_id": "unique-session-id",
  "timestamp": "2025-07-26T...",
  "legal_area": "Commercial Law",
  "urgency": "Normal",
  "confidence": 0.85
}
```

## Testing Workflow

### 🚀 **Quick Start Testing**
1. Start all services: `./start-dev.sh`
2. Start test server: `python3 -m http.server 9090`
3. Open test pages:
   ```bash
   open http://localhost:9090/test-conversion-widget.html
   open http://localhost:9090/test-widget-embed.html
   open http://localhost:9090/test-widget-api.html
   ```

### 📋 **Comprehensive Testing Checklist**

#### Widget Functionality ✅
- [ ] Widget loads and displays correctly
- [ ] AI provides intelligent responses
- [ ] Conversion buttons work
- [ ] Firm branding displays
- [ ] Contact information accurate
- [ ] Voice features functional
- [ ] Mobile responsive design

#### Technical Integration ✅
- [ ] API connectivity working
- [ ] CORS configuration correct
- [ ] Session management functional
- [ ] Error handling graceful
- [ ] Performance acceptable (<3s response)
- [ ] Security measures in place

#### Legal Content ✅
- [ ] South African law context accurate
- [ ] Professional legal language
- [ ] Appropriate disclaimers included
- [ ] Ethical compliance maintained
- [ ] Conversion optimization effective

## Troubleshooting

### Common Issues

**❌ Widget not loading:**
```bash
# Check services status
curl http://localhost:8000/health
curl http://localhost:5173
```

**❌ API errors:**
```bash
# Test API directly
curl -X POST http://localhost:8000/api/v1/simple-chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

**❌ CORS issues:**
- Check CORS_ORIGINS in docker-compose.yml
- Verify frontend is serving on correct port
- Test from different domains

**❌ Ollama not responding:**
```bash
# Check Ollama health
curl http://localhost:8000/api/v1/simple-chat/health
```

### Debug Commands

```bash
# View API logs
docker-compose logs api-python --tail=50

# View frontend logs  
docker-compose logs web --tail=50

# Test Ollama directly
curl http://localhost:11434/api/tags
```

## Production Deployment Testing

### Pre-Deployment Checklist
- [ ] All test pages pass
- [ ] API responses under 3 seconds
- [ ] No console errors in browser
- [ ] Mobile responsiveness verified
- [ ] Security headers configured
- [ ] Analytics tracking working
- [ ] Error monitoring active

### Production URLs
Replace localhost URLs with production equivalents:
- API: `https://api.verdict360.com/api/v1`
- Widget: `https://widget.verdict360.com`
- Script: `https://cdn.verdict360.com/widget.js`

## Support & Documentation

- **Main Documentation:** [WIDGET_INTEGRATION.md](./WIDGET_INTEGRATION.md)
- **API Reference:** http://localhost:8000/docs
- **Project Structure:** [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
- **Troubleshooting:** [README.md](./README.md)

---

**Last Updated:** 2025-07-26  
**Version:** 1.0.0  
**Environment:** Development