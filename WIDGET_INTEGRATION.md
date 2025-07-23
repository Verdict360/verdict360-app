# Verdict360 Legal Widget - Integration Guide

## Overview

The Verdict360 Legal Widget is an embeddable AI-powered legal assistant designed for South African law firms. It provides instant legal guidance, consultation booking, and professional client engagement directly on law firm websites.

## Quick Integration

### Method 1: Static JavaScript Widget (Recommended)

Add this single line to your website:

```html
<script src="http://localhost:5173/verdict360-widget.js" data-auto-embed="true"></script>
```

### Method 2: IFrame Embedding

```html
<iframe 
  src="http://localhost:5173/widget" 
  width="400" 
  height="600"
  style="border: none; border-radius: 12px;"
  title="Legal Chatbot Assistant">
</iframe>
```

## Configuration Options

### Basic Configuration

```html
<script 
  src="http://localhost:5173/verdict360-widget.js" 
  data-auto-embed="true"
  data-firm-name="Smith & Associates Legal"
  data-firm-phone="+27 11 123 4567"
  data-firm-email="info@smithlaw.co.za"
  data-position="bottom-right"
  data-theme="light"
  data-color="#1E40AF">
</script>
```

### Advanced Configuration

```html
<script 
  src="http://localhost:5173/verdict360-widget.js" 
  data-auto-embed="true"
  data-firm-name="Your Law Firm"
  data-firm-logo="https://yourfirm.co.za/logo.png"
  data-firm-phone="+27 11 123 4567"
  data-firm-email="contact@yourfirm.co.za"
  data-emergency-phone="+27 82 123 4567"
  data-office-hours="Monday - Friday: 8:00 AM - 5:00 PM"
  data-position="bottom-right"
  data-theme="light"
  data-color="#1E40AF"
  data-voice-call="true"
  data-consultation="true">
</script>
```

## Configuration Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `data-auto-embed` | Automatically show widget | `false` | `true`, `false` |
| `data-firm-name` | Your law firm's name | `""` | Any string |
| `data-firm-logo` | URL to your firm's logo | `""` | Valid image URL |
| `data-firm-phone` | Primary phone number | `""` | Phone format: +27 XX XXX XXXX |
| `data-firm-email` | Contact email address | `""` | Valid email |
| `data-emergency-phone` | Emergency contact number | `""` | Phone format: +27 XX XXX XXXX |
| `data-office-hours` | Business hours display | `"Monday - Friday: 8:00 AM - 5:00 PM"` | Any string |
| `data-position` | Widget position on screen | `"bottom-right"` | `bottom-right`, `bottom-left`, `top-right`, `top-left` |
| `data-theme` | Visual theme | `"light"` | `light`, `dark` |
| `data-color` | Primary brand color | `"#1E40AF"` | Any hex color |
| `data-voice-call` | Enable voice call button | `true` | `true`, `false` |
| `data-consultation` | Enable consultation booking | `true` | `true`, `false` |

## Implementation Examples

### Example 1: Full-Featured Law Firm

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smith & Associates - Leading Legal Experts</title>
</head>
<body>
    <!-- Your website content -->
    <h1>Welcome to Smith & Associates</h1>
    <p>Professional legal services in South Africa</p>
    
    <!-- Verdict360 Widget Integration -->
    <script 
      src="http://localhost:5173/verdict360-widget.js" 
      data-auto-embed="true"
      data-firm-name="Smith & Associates Legal"
      data-firm-logo="https://smithlaw.co.za/assets/logo.png"
      data-firm-phone="+27 11 789 1234"
      data-firm-email="info@smithlaw.co.za"
      data-emergency-phone="+27 82 555 0123"
      data-office-hours="Monday - Friday: 8:00 AM - 6:00 PM, Saturday: 9:00 AM - 1:00 PM"
      data-position="bottom-right"
      data-theme="light"
      data-color="#2563EB">
    </script>
</body>
</html>
```

### Example 2: Minimal Integration

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Your Law Firm</title>
</head>
<body>
    <h1>Legal Services</h1>
    
    <!-- Simple widget integration -->
    <script 
      src="http://localhost:5173/verdict360-widget.js" 
      data-auto-embed="true"
      data-firm-name="Your Law Firm"
      data-firm-phone="+27 11 123 4567">
    </script>
</body>
</html>
```

### Example 3: Custom Container

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Legal Consultation</title>
</head>
<body>
    <div class="consultation-page">
        <h1>Legal Consultation</h1>
        
        <!-- Custom widget container -->
        <div id="legal-widget-container"></div>
    </div>
    
    <!-- Load widget without auto-embed -->
    <script src="http://localhost:5173/verdict360-widget.js"></script>
    <script>
        // Initialize widget in custom container
        Verdict360Widget.init('legal-widget-container');
    </script>
</body>
</html>
```

## JavaScript API

### Manual Control

```javascript
// Initialize widget manually
Verdict360Widget.init('container-id');

// Open widget programmatically
Verdict360Widget.open();

// Close widget programmatically
Verdict360Widget.close();

// Send message programmatically
Verdict360Widget.sendMessage('I need help with contract law');

// Access configuration
console.log(Verdict360Widget.config);
```

### Event Handling

```javascript
// Listen for widget events (if needed for analytics)
window.addEventListener('verdict360-widget-opened', function() {
    console.log('Widget opened');
    // Track analytics
});

window.addEventListener('verdict360-widget-closed', function() {
    console.log('Widget closed');
});

window.addEventListener('verdict360-message-sent', function(event) {
    console.log('Message sent:', event.detail.message);
});
```

## Styling & Customization

### Custom CSS Overrides

```html
<style>
/* Custom widget styling */
.verdict360-widget-container {
    /* Override default positioning */
    bottom: 30px !important;
    right: 30px !important;
}

.verdict360-widget-button {
    /* Custom button colors */
    background: #DC2626 !important; /* Red theme */
}

.verdict360-widget-panel {
    /* Custom panel styling */
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
}

.verdict360-widget-header {
    /* Custom header background */
    background: linear-gradient(135deg, #DC2626, #B91C1C) !important;
}
</style>
```

### Dark Theme Customization

```html
<script 
  src="http://localhost:5173/verdict360-widget.js" 
  data-auto-embed="true"
  data-theme="dark"
  data-color="#EF4444">
</script>

<style>
.verdict360-widget-container.dark .verdict360-widget-panel {
    background: #0F172A !important;
    border: 1px solid #334155 !important;
}
</style>
```

## Mobile Responsiveness

The widget automatically adapts to mobile devices:

- **Desktop**: 380px × 500px panel
- **Mobile**: Full-width responsive design
- **Tablet**: Optimized for touch interactions

### Custom Mobile Styling

```css
@media (max-width: 768px) {
    .verdict360-widget-container {
        /* Custom mobile positioning */
        bottom: 10px !important;
        left: 10px !important;
        right: 10px !important;
    }
    
    .verdict360-widget-panel {
        /* Custom mobile dimensions */
        width: calc(100vw - 20px) !important;
        height: calc(100vh - 120px) !important;
        max-height: 600px !important;
    }
}
```

## Integration Testing

### Test Widget Functionality

1. **Basic Integration Test**
   ```html
   <!-- Create test file: test-widget.html -->
   <!DOCTYPE html>
   <html>
   <head><title>Widget Test</title></head>
   <body>
       <h1>Widget Integration Test</h1>
       <script src="http://localhost:5173/verdict360-widget.js" data-auto-embed="true"></script>
   </body>
   </html>
   ```

2. **Open test file in browser**
3. **Verify widget appears in bottom-right**
4. **Test chat functionality with legal questions**

### API Testing

```javascript
// Test API connectivity
fetch('http://localhost:8000/api/v1/simple-chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Test legal question' })
})
.then(response => response.json())
.then(data => console.log('API Response:', data))
.catch(error => console.error('API Error:', error));
```

## Troubleshooting

### Common Issues

1. **Widget Not Appearing**
   ```javascript
   // Check if script loaded
   console.log(window.Verdict360Widget);
   
   // Check for console errors
   // Open browser DevTools > Console
   ```

2. **AI Not Responding**
   ```javascript
   // Verify API connectivity
   fetch('http://localhost:8000/health')
   .then(response => response.json())
   .then(data => console.log('API Health:', data));
   ```

3. **CORS Issues**
   - Ensure your domain is added to FastAPI CORS settings
   - Check `api-python/app/core/config.py` for allowed origins

4. **Styling Issues**
   ```css
   /* Reset any conflicting styles */
   .verdict360-widget-container * {
       box-sizing: border-box !important;
   }
   ```

### Debug Mode

```html
<script>
// Enable debug mode
window.VERDICT360_DEBUG = true;
</script>
<script src="http://localhost:5173/verdict360-widget.js" data-auto-embed="true"></script>
```

## Security Considerations

### HTTPS Requirements

For production deployments:

```html
<!-- Use HTTPS URLs -->
<script src="https://your-domain.com/verdict360-widget.js"></script>
```

### Content Security Policy

Add to your CSP headers:

```
script-src 'self' https://your-verdict360-domain.com;
connect-src 'self' https://your-verdict360-api.com;
frame-src 'self' https://your-verdict360-domain.com;
```

### Data Privacy (POPIA Compliance)

The widget automatically handles:
- ✅ User consent management
- ✅ Data encryption in transit
- ✅ Session management
- ✅ Audit trail logging

## Performance Optimization

### Lazy Loading

```html
<!-- Load widget only when needed -->
<script>
function loadWidget() {
    const script = document.createElement('script');
    script.src = 'http://localhost:5173/verdict360-widget.js';
    script.setAttribute('data-auto-embed', 'true');
    document.head.appendChild(script);
}

// Load when user interacts with page
document.addEventListener('click', loadWidget, { once: true });
</script>
```

### Preload Resources

```html
<link rel="preload" href="http://localhost:5173/verdict360-widget.js" as="script">
<link rel="preconnect" href="http://localhost:8000">
```

## Analytics & Tracking

### Google Analytics Integration

```javascript
// Track widget interactions
window.addEventListener('verdict360-widget-opened', function() {
    gtag('event', 'widget_opened', {
        'event_category': 'Legal Widget',
        'event_label': 'User Engagement'
    });
});

window.addEventListener('verdict360-message-sent', function(event) {
    gtag('event', 'legal_question_asked', {
        'event_category': 'Legal Widget',
        'event_label': 'Client Inquiry'
    });
});
```

## Production Deployment

### Environment Variables

Update widget source URLs for production:

```html
<!-- Production widget integration -->
<script 
  src="https://widget.verdict360.co.za/verdict360-widget.js" 
  data-auto-embed="true">
</script>
```

### CDN Integration

```html
<!-- CDN delivery for better performance -->
<script 
  src="https://cdn.verdict360.co.za/widget/v1.0/verdict360-widget.min.js" 
  data-auto-embed="true">
</script>
```

## Support & Contact

- **Technical Support**: dev@verdict360.co.za
- **Business Inquiries**: sales@verdict360.co.za
- **Documentation Updates**: https://docs.verdict360.co.za
- **GitHub Issues**: https://github.com/verdict360/widget-issues

---

**Last Updated**: 2025-01-23  
**Widget Version**: 1.0.0  
**API Version**: v1  
**Compatibility**: All modern browsers (Chrome 70+, Firefox 65+, Safari 12+, Edge 79+)