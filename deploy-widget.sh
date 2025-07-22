#!/bin/bash

# Verdict360 Widget Deployment Script
# Deploys the chatbot widget for production use

set -e

echo "🚀 Deploying Verdict360 Legal Chatbot Widget"
echo "=============================================="

# Configuration
WIDGET_DIR="web/static"
BACKEND_URL="http://localhost:8000"  # Will be replaced with production URL
WIDGET_VERSION="1.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if backend is running
check_backend() {
    print_status "Checking backend API status..."
    
    if curl -f -s ${BACKEND_URL}/api/v1/health > /dev/null; then
        print_success "Backend API is running at ${BACKEND_URL}"
    else
        print_warning "Backend API not accessible at ${BACKEND_URL}"
        print_warning "Widget will use fallback responses for demo purposes"
    fi
}

# Start backend if needed
start_backend() {
    print_status "Starting Verdict360 backend API..."
    
    cd api-python
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_status "Activated virtual environment"
    fi
    
    # Start FastAPI server in background
    if ! pgrep -f "uvicorn.*main:app" > /dev/null; then
        print_status "Starting FastAPI server..."
        nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
        BACKEND_PID=$!
        
        # Wait for backend to start
        sleep 5
        
        if curl -f -s ${BACKEND_URL}/api/v1/health > /dev/null; then
            print_success "Backend started successfully (PID: ${BACKEND_PID})"
            echo $BACKEND_PID > ../backend.pid
        else
            print_error "Failed to start backend API"
            exit 1
        fi
    else
        print_success "Backend API is already running"
    fi
    
    cd ..
}

# Start frontend development server
start_frontend() {
    print_status "Starting SvelteKit frontend..."
    
    cd web
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start development server in background
    if ! pgrep -f "vite.*dev" > /dev/null; then
        print_status "Starting SvelteKit dev server..."
        nohup npm run dev > ../frontend.log 2>&1 &
        FRONTEND_PID=$!
        
        # Wait for frontend to start
        sleep 8
        
        if curl -f -s http://localhost:5173 > /dev/null; then
            print_success "Frontend started successfully (PID: ${FRONTEND_PID})"
            echo $FRONTEND_PID > ../frontend.pid
        else
            print_warning "Frontend may still be starting up..."
        fi
    else
        print_success "Frontend development server is already running"
    fi
    
    cd ..
}

# Test widget functionality
test_widget() {
    print_status "Testing widget functionality..."
    
    # Test API endpoints
    echo "Testing API endpoints:"
    
    # Health check
    if curl -f -s "${BACKEND_URL}/api/v1/health" > /dev/null; then
        print_success "✅ Health check endpoint"
    else
        print_warning "⚠️  Health check endpoint not available"
    fi
    
    # Chat endpoint
    CHAT_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/v1/chat/" \
        -H "Content-Type: application/json" \
        -d '{"message":"Test message","session_id":"test_session"}' \
        -w "%{http_code}" -o /tmp/chat_response.json)
    
    if [ "${CHAT_RESPONSE}" = "200" ]; then
        print_success "✅ Chat endpoint working"
    else
        print_warning "⚠️  Chat endpoint returned HTTP ${CHAT_RESPONSE}"
    fi
    
    # Analytics endpoint
    if curl -f -s "${BACKEND_URL}/api/v1/analytics/health" > /dev/null; then
        print_success "✅ Analytics endpoint"
    else
        print_warning "⚠️  Analytics endpoint not available"
    fi
    
    # Calendar endpoint
    if curl -f -s "${BACKEND_URL}/api/v1/calendar/health" > /dev/null; then
        print_success "✅ Calendar endpoint"
    else
        print_warning "⚠️  Calendar endpoint not available"
    fi
}

# Generate production widget script
generate_production_widget() {
    print_status "Generating production widget script..."
    
    # Update API URL in widget script for production
    sed "s|http://localhost:8000/api/v1|${BACKEND_URL}/api/v1|g" \
        web/static/verdict360-widget.js > web/static/verdict360-widget-production.js
    
    # Minify for production (if uglify-js is available)
    if command -v uglifyjs &> /dev/null; then
        print_status "Minifying widget script..."
        uglifyjs web/static/verdict360-widget-production.js \
            --compress --mangle \
            --output web/static/verdict360-widget.min.js
        print_success "Created minified widget: verdict360-widget.min.js"
    else
        print_warning "uglify-js not found, skipping minification"
        cp web/static/verdict360-widget-production.js web/static/verdict360-widget.min.js
    fi
}

# Create integration examples
create_examples() {
    print_status "Creating integration examples..."
    
    # Create examples directory
    mkdir -p integration-examples
    
    # WordPress plugin example
    cat > integration-examples/verdict360-wordpress-plugin.php << 'EOF'
<?php
/**
 * Plugin Name: Verdict360 Legal Chatbot
 * Description: Adds Verdict360 AI legal assistant to your law firm website
 * Version: 1.0.0
 * Author: Verdict360
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class Verdict360Widget {
    
    public function __construct() {
        add_action('wp_footer', array($this, 'add_widget_script'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
    }
    
    public function add_widget_script() {
        $firm_name = get_option('verdict360_firm_name', get_bloginfo('name'));
        $primary_color = get_option('verdict360_primary_color', '#1E40AF');
        $position = get_option('verdict360_position', 'bottom-right');
        ?>
        <script src="https://verdict360.com/verdict360-widget.js" 
                data-auto-embed="true"
                data-firm-name="<?php echo esc_attr($firm_name); ?>"
                data-color="<?php echo esc_attr($primary_color); ?>"
                data-position="<?php echo esc_attr($position); ?>"></script>
        <?php
    }
    
    public function add_admin_menu() {
        add_options_page(
            'Verdict360 Settings',
            'Legal Chatbot',
            'manage_options',
            'verdict360-settings',
            array($this, 'settings_page')
        );
    }
    
    public function settings_page() {
        if (isset($_POST['submit'])) {
            update_option('verdict360_firm_name', sanitize_text_field($_POST['firm_name']));
            update_option('verdict360_primary_color', sanitize_hex_color($_POST['primary_color']));
            update_option('verdict360_position', sanitize_text_field($_POST['position']));
            echo '<div class="notice notice-success"><p>Settings saved!</p></div>';
        }
        
        $firm_name = get_option('verdict360_firm_name', get_bloginfo('name'));
        $primary_color = get_option('verdict360_primary_color', '#1E40AF');
        $position = get_option('verdict360_position', 'bottom-right');
        ?>
        <div class="wrap">
            <h1>Verdict360 Legal Chatbot Settings</h1>
            <form method="post" action="">
                <table class="form-table">
                    <tr>
                        <th scope="row">Law Firm Name</th>
                        <td><input type="text" name="firm_name" value="<?php echo esc_attr($firm_name); ?>" /></td>
                    </tr>
                    <tr>
                        <th scope="row">Primary Color</th>
                        <td><input type="color" name="primary_color" value="<?php echo esc_attr($primary_color); ?>" /></td>
                    </tr>
                    <tr>
                        <th scope="row">Widget Position</th>
                        <td>
                            <select name="position">
                                <option value="bottom-right" <?php selected($position, 'bottom-right'); ?>>Bottom Right</option>
                                <option value="bottom-left" <?php selected($position, 'bottom-left'); ?>>Bottom Left</option>
                                <option value="top-right" <?php selected($position, 'top-right'); ?>>Top Right</option>
                                <option value="top-left" <?php selected($position, 'top-left'); ?>>Top Left</option>
                            </select>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
}

new Verdict360Widget();
EOF

    print_success "Created WordPress plugin example"
    
    # HTML integration examples
    cat > integration-examples/simple-integration.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Simple Verdict360 Integration</title>
</head>
<body>
    <h1>My Law Firm Website</h1>
    <p>Welcome to our legal practice...</p>
    
    <!-- Verdict360 Legal Chatbot - One Line Integration -->
    <script src="https://verdict360.com/verdict360-widget.js" 
            data-auto-embed="true"
            data-firm-name="Your Law Firm Name"
            data-color="#1a365d"></script>
</body>
</html>
EOF

    print_success "Created HTML integration examples"
}

# Main deployment function
deploy() {
    print_status "Starting Verdict360 widget deployment..."
    
    # Check dependencies
    print_status "Checking dependencies..."
    
    # Start services
    start_backend
    start_frontend
    
    # Check backend status
    check_backend
    
    # Test functionality
    test_widget
    
    # Generate production files
    generate_production_widget
    
    # Create integration examples
    create_examples
    
    print_success "🎉 Widget deployment completed successfully!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "======================"
    echo "• Backend API: ${BACKEND_URL}"
    echo "• Frontend: http://localhost:5173"
    echo "• Widget script: web/static/verdict360-widget.js"
    echo "• Minified script: web/static/verdict360-widget.min.js"
    echo "• Test page: test-widget-integration.html"
    echo "• Integration guide: WIDGET_INTEGRATION_GUIDE.md"
    echo ""
    echo "🧪 Quick Test:"
    echo "Open test-widget-integration.html in your browser"
    echo "Look for the blue chat icon in the bottom-right corner"
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Open http://localhost:5173 to access the SvelteKit app"
    echo "2. Test the widget on the sample website"
    echo "3. Copy integration code to your law firm's website"
    echo "4. Customize branding and colors as needed"
    echo ""
    echo "📖 For detailed integration instructions, see:"
    echo "   WIDGET_INTEGRATION_GUIDE.md"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up deployment files..."
    
    # Stop services if they were started by this script
    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
    fi
    
    print_success "Cleanup completed"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "cleanup")
        cleanup
        ;;
    "test")
        check_backend
        test_widget
        ;;
    *)
        echo "Usage: $0 [deploy|cleanup|test]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the widget (default)"
        echo "  cleanup  - Stop services and clean up"
        echo "  test     - Test widget functionality"
        exit 1
        ;;
esac