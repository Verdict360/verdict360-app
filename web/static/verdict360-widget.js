/**
 * Verdict360 Legal Chatbot Widget
 * Embeddable legal AI assistant for South African law firm websites
 *
 * Usage: Add this script to any website to embed the legal chatbot
 * <script src="https://your-domain.com/verdict360-widget.js"></script>
 * <div id="verdict360-widget"></div>
 *
 * Or use the auto-embed version:
 * <script src="https://your-domain.com/verdict360-widget.js" data-auto-embed="true"></script>
 */

(function () {
  'use strict';

  // Configuration
  const config = {
    apiUrl: 'http://localhost:8000/api/v1', // Will be replaced with production URL
    widgetUrl: 'http://localhost:5173/widget', // SvelteKit widget URL
    version: '1.0.0',
    autoEmbed: false,
    position: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
    theme: 'light', // light, dark, custom
    primaryColor: '#1E40AF', // Legal blue
    firmName: '', // Will be customized per firm
    firmLogo: '', // Optional firm logo URL
    firmPhone: '', // Law firm's phone number
    firmEmail: '', // Law firm's email address
    emergencyPhone: '', // Emergency contact number
    officeHours: 'Monday - Friday: 8:00 AM - 5:00 PM', // Business hours
    enableVoiceCall: true,
    enableConsultationBooking: true,
  };

  // Get configuration from script tag attributes
  const scriptTag =
    document.currentScript || document.querySelector('script[src*="verdict360-widget"]');
  if (scriptTag) {
    config.autoEmbed = scriptTag.getAttribute('data-auto-embed') === 'true';
    config.position = scriptTag.getAttribute('data-position') || config.position;
    config.theme = scriptTag.getAttribute('data-theme') || config.theme;
    config.primaryColor = scriptTag.getAttribute('data-color') || config.primaryColor;
    config.firmName = scriptTag.getAttribute('data-firm-name') || config.firmName;
    config.firmLogo = scriptTag.getAttribute('data-firm-logo') || config.firmLogo;
    config.firmPhone = scriptTag.getAttribute('data-firm-phone') || config.firmPhone;
    config.firmEmail = scriptTag.getAttribute('data-firm-email') || config.firmEmail;
    config.emergencyPhone = scriptTag.getAttribute('data-emergency-phone') || config.emergencyPhone;
    config.officeHours = scriptTag.getAttribute('data-office-hours') || config.officeHours;
    config.enableVoiceCall = scriptTag.getAttribute('data-voice-call') !== 'false';
    config.enableConsultationBooking = scriptTag.getAttribute('data-consultation') !== 'false';
  }

  // Widget state
  let isOpen = false;
  let isLoading = false;
  let messages = [];
  let sessionId = null;

  // Initialize session
  function initSession() {
    sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    // Send welcome message
    addMessage({
      id: 'welcome_' + Date.now(),
      content: config.firmName
        ? `Welcome to ${config.firmName}'s legal assistant. I'm here to help with your legal questions and provide professional legal guidance.`
        : "Welcome to Verdict360 Legal Assistant. I'm here to help with your legal questions and provide professional legal guidance.",
      type: 'assistant',
      timestamp: new Date(),
    });
  }

  // Create widget HTML structure
  function createWidgetHTML() {
    return `
        <div id="verdict360-chat-widget" class="verdict360-widget-container ${config.position} ${config.theme}">
            <!-- Widget Button (when closed) -->
            <div id="verdict360-widget-button" class="verdict360-widget-button">
                <div class="verdict360-button-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white" stroke="none">
                        <path d="M20 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4l4 4 4-4h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
                        <circle cx="8" cy="12" r="1" fill="${config.primaryColor}"/>
                        <circle cx="12" cy="12" r="1" fill="${config.primaryColor}"/>
                        <circle cx="16" cy="12" r="1" fill="${config.primaryColor}"/>
                    </svg>
                </div>
                <div class="verdict360-button-pulse"></div>
            </div>
            
            <!-- Widget Chat Panel (when open) -->
            <div id="verdict360-widget-panel" class="verdict360-widget-panel" style="display: none;">
                <!-- Header -->
                <div class="verdict360-widget-header">
                    <div class="verdict360-header-info">
                        ${
                          config.firmLogo
                            ? `<img src="${config.firmLogo}" alt="Logo" class="verdict360-header-logo">`
                            : '<div class="verdict360-header-avatar">V</div>'
                        }
                        <div class="verdict360-header-text">
                            <h3>Legal Assistant</h3>
                            <p>Professional legal guidance</p>
                        </div>
                    </div>
                    <div class="verdict360-header-actions">
                        ${
                          config.enableVoiceCall
                            ? '<button id="verdict360-voice-call" class="verdict360-action-btn" title="Voice Call"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></button>'
                            : ''
                        }
                        <button id="verdict360-close-btn" class="verdict360-close-btn" title="Close">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/>
                                <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <!-- Messages Container -->
                <div id="verdict360-messages" class="verdict360-messages">
                    <div class="verdict360-typing" id="verdict360-typing" style="display: none;">
                        <div class="verdict360-typing-dots">
                            <span></span><span></span><span></span>
                        </div>
                        <span class="verdict360-typing-text">Legal assistant is thinking...</span>
                    </div>
                </div>
                
                <!-- Input Area -->
                <div class="verdict360-widget-input">
                    <div class="verdict360-input-container">
                        <textarea 
                            id="verdict360-message-input" 
                            placeholder="Ask any legal question..."
                            rows="1"
                        ></textarea>
                        <button id="verdict360-send-btn" class="verdict360-send-btn" disabled>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="white" stroke="none">
                                <path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="verdict360-input-footer">
                        <span class="verdict360-help-text">Press Enter to send • Shift+Enter for new line</span>
                        ${
                          config.enableConsultationBooking
                            ? '<button id="verdict360-book-consultation" class="verdict360-book-btn"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>Book Consultation</button>'
                            : ''
                        }
                    </div>
                </div>
            </div>
        </div>`;
  }

  // Create widget CSS
  function createWidgetCSS() {
    const css = `
        .verdict360-widget-container {
            position: fixed;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }
        
        .verdict360-widget-container.bottom-right {
            bottom: 20px;
            right: 20px;
        }
        
        .verdict360-widget-container.bottom-left {
            bottom: 20px;
            left: 20px;
        }
        
        .verdict360-widget-container.top-right {
            top: 20px;
            right: 20px;
        }
        
        .verdict360-widget-container.top-left {
            top: 20px;
            left: 20px;
        }
        
        /* Widget Button */
        .verdict360-widget-button {
            position: relative;
            width: 60px;
            height: 60px;
            background: ${config.primaryColor};
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
        }
        
        .verdict360-widget-button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        }
        
        .verdict360-button-pulse {
            position: absolute;
            top: -4px;
            left: -4px;
            right: -4px;
            bottom: -4px;
            border: 2px solid ${config.primaryColor};
            border-radius: 50%;
            animation: pulse 2s infinite;
            opacity: 0;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.7; }
            70% { transform: scale(1.1); opacity: 0; }
            100% { transform: scale(1.1); opacity: 0; }
        }
        
        /* Widget Panel */
        .verdict360-widget-panel {
            width: 380px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transform: translateY(20px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .verdict360-widget-panel.open {
            transform: translateY(0);
            opacity: 1;
        }
        
        /* Header */
        .verdict360-widget-header {
            background: ${config.primaryColor};
            color: white;
            padding: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .verdict360-header-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .verdict360-header-avatar {
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }
        
        .verdict360-header-logo {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .verdict360-header-text h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
        }
        
        .verdict360-header-text p {
            margin: 2px 0 0 0;
            font-size: 12px;
            opacity: 0.9;
        }
        
        .verdict360-header-actions {
            display: flex;
            gap: 8px;
        }
        
        .verdict360-action-btn, .verdict360-close-btn {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .verdict360-action-btn:hover, .verdict360-close-btn:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .verdict360-close-btn {
            font-size: 20px;
            line-height: 1;
        }
        
        /* Messages */
        .verdict360-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .verdict360-message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .verdict360-message.user {
            background: ${config.primaryColor};
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        
        .verdict360-message.assistant {
            background: #f1f5f9;
            color: #334155;
            align-self: flex-start;
        }
        
        .verdict360-typing {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #64748b;
            font-size: 13px;
        }
        
        .verdict360-typing-dots {
            display: flex;
            gap: 2px;
        }
        
        .verdict360-typing-dots span {
            width: 4px;
            height: 4px;
            background: #64748b;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        
        .verdict360-typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .verdict360-typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
            30% { opacity: 1; transform: translateY(-4px); }
        }
        
        /* Input */
        .verdict360-widget-input {
            border-top: 1px solid #e2e8f0;
            background: white;
        }
        
        .verdict360-input-container {
            display: flex;
            padding: 16px;
            gap: 12px;
            align-items: flex-end;
        }
        
        .verdict360-input-container textarea {
            flex: 1;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 14px;
            font-family: inherit;
            resize: none;
            outline: none;
            min-height: 20px;
            max-height: 80px;
        }
        
        .verdict360-input-container textarea:focus {
            border-color: ${config.primaryColor};
        }
        
        .verdict360-send-btn {
            background: ${config.primaryColor};
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .verdict360-send-btn:hover:not(:disabled) {
            background: ${config.primaryColor}dd;
            transform: scale(1.05);
        }
        
        .verdict360-send-btn:disabled {
            background: #cbd5e1;
            cursor: not-allowed;
        }
        
        .verdict360-input-footer {
            padding: 8px 16px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .verdict360-help-text {
            font-size: 11px;
            color: #64748b;
        }
        
        .verdict360-book-btn {
            background: none;
            border: 1px solid ${config.primaryColor};
            color: ${config.primaryColor};
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .verdict360-book-btn:hover {
            background: ${config.primaryColor};
            color: white;
        }
        
        /* Mobile responsive */
        @media (max-width: 480px) {
            .verdict360-widget-panel {
                width: calc(100vw - 40px);
                height: calc(100vh - 100px);
                max-height: 600px;
            }
            
            .verdict360-widget-container.bottom-right,
            .verdict360-widget-container.bottom-left {
                bottom: 10px;
                left: 10px;
                right: 10px;
            }
        }
        
        /* Dark theme */
        .verdict360-widget-container.dark .verdict360-widget-panel {
            background: #1e293b;
            color: white;
        }
        
        .verdict360-widget-container.dark .verdict360-message.assistant {
            background: #334155;
            color: #f1f5f9;
        }
        
        .verdict360-widget-container.dark .verdict360-widget-input {
            background: #1e293b;
            border-color: #334155;
        }
        
        .verdict360-widget-container.dark .verdict360-input-container textarea {
            background: #334155;
            border-color: #475569;
            color: white;
        }`;

    // Inject CSS
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }

  // Add message to chat
  function addMessage(message) {
    messages.push(message);
    renderMessage(message);
    scrollToBottom();
  }

  // Render a message
  function renderMessage(message) {
    const messagesContainer = document.getElementById('verdict360-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `verdict360-message ${message.type}`;
    messageDiv.innerHTML = formatMessageContent(message.content);

    // Insert before typing indicator if it exists
    const typingIndicator = document.getElementById('verdict360-typing');
    if (typingIndicator) {
      messagesContainer.insertBefore(messageDiv, typingIndicator);
    } else {
      messagesContainer.appendChild(messageDiv);
    }
  }

  // Format message content (handle links, basic formatting)
  function formatMessageContent(content) {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
      .replace(/\n/g, '<br>');
  }

  // Generate enhanced error message with contact information
  function createErrorMessage(type = 'technical') {
    let baseMessage = '';
    let contactInfo = '';

    // Build contact information if available
    if (config.firmPhone || config.firmEmail) {
      contactInfo += '\n\n**Contact us directly:**';

      if (config.firmPhone) {
        contactInfo += `\n📞 **Phone:** [${config.firmPhone}](tel:${config.firmPhone.replace(/\s/g, '')})`;
      }

      if (config.firmEmail) {
        contactInfo += `\n📧 **Email:** [${config.firmEmail}](mailto:${config.firmEmail})`;
      }

      if (config.emergencyPhone && type === 'urgent') {
        contactInfo += `\n🚨 **Emergency:** [${config.emergencyPhone}](tel:${config.emergencyPhone.replace(/\s/g, '')})`;
      }

      if (config.officeHours) {
        contactInfo += `\n⏰ **Office Hours:** ${config.officeHours}`;
      }
    }

    // Different messages based on error type
    switch (type) {
      case 'urgent':
        baseMessage = `I apologize, but I'm currently experiencing technical difficulties. For urgent legal matters, please contact us directly using the information below:${contactInfo}`;
        break;
      case 'connection':
        baseMessage = `I'm having trouble connecting to our legal database. Please try again in a moment, or contact our office directly:${contactInfo}`;
        break;
      case 'technical':
      default:
        baseMessage = config.firmName
          ? `I apologize, but I'm currently experiencing technical difficulties. Please try again in a moment, or contact ${config.firmName} directly:${contactInfo}`
          : `I apologize, but I'm currently experiencing technical difficulties. Please try again in a moment, or contact our support team directly:${contactInfo}`;
        break;
    }

    return (
      baseMessage ||
      "I apologize, but I'm currently experiencing technical difficulties. Please try again in a moment."
    );
  }

  // Scroll to bottom of messages
  function scrollToBottom() {
    const messagesContainer = document.getElementById('verdict360-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Send message to API
  async function sendMessage(content) {
    const userMessage = {
      id: 'user_' + Date.now(),
      content: content,
      type: 'user',
      timestamp: new Date(),
    };

    addMessage(userMessage);
    showTyping();

    try {
      const response = await fetch(`${config.apiUrl}/simple-chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors', // Explicitly enable CORS
        credentials: 'omit', // Don't send credentials for cross-origin
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
          context: {
            firm_name: config.firmName,
            widget_version: config.version,
            page_url: window.location.href,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      const assistantMessage = {
        id: 'assistant_' + Date.now(),
        content:
          data.response ||
          "I apologize, but I'm having trouble processing your request. Please try again.",
        type: 'assistant',
        timestamp: new Date(),
      };

      addMessage(assistantMessage);

      // Check if consultation booking should be offered
      if (
        data.should_offer_consultation ||
        content.toLowerCase().includes('consultation') ||
        content.toLowerCase().includes('appointment')
      ) {
        setTimeout(() => {
          showConsultationOffer();
        }, 1000);
      }
    } catch (error) {
      console.error('Verdict360 Widget Error:', error);

      // Determine error type for appropriate message
      let errorType = 'technical';
      if (error.message && error.message.includes('fetch')) {
        errorType = 'connection';
      }
      if (content.toLowerCase().includes('emergency') || content.toLowerCase().includes('urgent')) {
        errorType = 'urgent';
      }

      const errorMessage = {
        id: 'error_' + Date.now(),
        content: createErrorMessage(errorType),
        type: 'assistant',
        timestamp: new Date(),
      };

      addMessage(errorMessage);
    } finally {
      hideTyping();
    }
  }

  // Show/hide typing indicator
  function showTyping() {
    document.getElementById('verdict360-typing').style.display = 'flex';
    scrollToBottom();
  }

  function hideTyping() {
    document.getElementById('verdict360-typing').style.display = 'none';
  }

  // Show consultation booking offer
  function showConsultationOffer() {
    if (!config.enableConsultationBooking) return;

    const offerMessage = {
      id: 'consultation_offer_' + Date.now(),
      content:
        'Would you like to **schedule a consultation** with one of our qualified attorneys? I can help you find an available appointment time that works for your schedule.',
      type: 'assistant',
      timestamp: new Date(),
    };

    addMessage(offerMessage);
  }

  // Handle voice call
  function handleVoiceCall() {
    if (!config.enableVoiceCall) return;

    // This would integrate with the voice calling system
    const voiceMessage = {
      id: 'voice_' + Date.now(),
      content:
        '📞 **Voice consultation feature** is being set up for you. Our system supports professional voice calls with qualified legal experts. This feature will be available shortly.',
      type: 'assistant',
      timestamp: new Date(),
    };

    addMessage(voiceMessage);
  }

  // Handle consultation booking
  function handleConsultationBooking() {
    if (!config.enableConsultationBooking) return;

    const bookingMessage = {
      id: 'booking_' + Date.now(),
      content:
        '📅 **Consultation scheduling** is being prepared for you. I can help you find available appointment times with our qualified attorneys. What type of legal matter would you like to discuss?',
      type: 'assistant',
      timestamp: new Date(),
    };

    addMessage(bookingMessage);
  }

  // Toggle widget open/closed
  function toggleWidget() {
    const button = document.getElementById('verdict360-widget-button');
    const panel = document.getElementById('verdict360-widget-panel');

    if (isOpen) {
      // Close widget
      panel.classList.remove('open');
      setTimeout(() => {
        panel.style.display = 'none';
        button.style.display = 'flex';
      }, 300);
      isOpen = false;
    } else {
      // Open widget
      button.style.display = 'none';
      panel.style.display = 'flex';
      setTimeout(() => {
        panel.classList.add('open');
        document.getElementById('verdict360-message-input').focus();
      }, 10);
      isOpen = true;

      // Initialize session if not already done
      if (!sessionId) {
        initSession();
      }
    }
  }

  // Auto-resize textarea
  function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 80) + 'px';
  }

  // Initialize widget
  function initWidget(containerId = null) {
    // Create CSS
    createWidgetCSS();

    // Create widget container
    const container = document.createElement('div');
    container.innerHTML = createWidgetHTML();

    // Append to specified container or body
    if (containerId) {
      const targetContainer = document.getElementById(containerId);
      if (targetContainer) {
        targetContainer.appendChild(container.firstElementChild);
      } else {
        console.error(`Verdict360: Container with ID '${containerId}' not found`);
        return;
      }
    } else {
      document.body.appendChild(container.firstElementChild);
    }

    // Add event listeners
    document.getElementById('verdict360-widget-button').addEventListener('click', toggleWidget);
    document.getElementById('verdict360-close-btn').addEventListener('click', toggleWidget);

    const messageInput = document.getElementById('verdict360-message-input');
    const sendBtn = document.getElementById('verdict360-send-btn');

    // Send button click
    sendBtn.addEventListener('click', () => {
      const message = messageInput.value.trim();
      if (message && !isLoading) {
        sendMessage(message);
        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendBtn.disabled = true;
      }
    });

    // Input event handling
    messageInput.addEventListener('input', (e) => {
      autoResize(e.target);
      sendBtn.disabled = !e.target.value.trim();
    });

    // Enter key handling
    messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
      }
    });

    // Voice call button
    const voiceCallBtn = document.getElementById('verdict360-voice-call');
    if (voiceCallBtn) {
      voiceCallBtn.addEventListener('click', handleVoiceCall);
    }

    // Book consultation button
    const bookConsultationBtn = document.getElementById('verdict360-book-consultation');
    if (bookConsultationBtn) {
      bookConsultationBtn.addEventListener('click', handleConsultationBooking);
    }

    console.log('Verdict360 Legal Widget initialized successfully');
  }

  // Public API
  window.Verdict360Widget = {
    init: initWidget,
    open: () => !isOpen && toggleWidget(),
    close: () => isOpen && toggleWidget(),
    sendMessage: sendMessage,
    config: config,
  };

  // Auto-embed if configured
  if (config.autoEmbed) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => initWidget());
    } else {
      initWidget();
    }
  }
})();
