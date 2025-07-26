<script lang="ts">
  import { Send, Phone, Loader2 } from 'lucide-svelte';
  import Button from '@/lib/components/ui/Button.svelte';
  import Card from '@/lib/components/ui/Card.svelte';
  import ChatMessage from './ChatMessage.svelte';
  
  export let isEmbedded = false;
  export let firmName = '';
  export let firmPhone = '';
  export let firmEmail = '';
  export let emergencyPhone = '';
  export let officeHours = 'Monday - Friday: 8:00 AM - 5:00 PM';
  
  let messages: Array<{id: string, content: string, type: 'user' | 'assistant', timestamp: Date}> = [];
  let currentMessage = '';
  let isLoading = false;
  let messagesContainer: HTMLDivElement;
  
  // Create enhanced error message with contact information
  function createErrorMessage(userMessage: string = '') {
    let contactInfo = '';
    
    // Build contact information if available
    if (firmPhone || firmEmail) {
      contactInfo += '\n\n**Contact us directly:**';
      
      if (firmPhone) {
        contactInfo += `\n📞 **Phone:** ${firmPhone}`;
      }
      
      if (firmEmail) {
        contactInfo += `\n📧 **Email:** ${firmEmail}`;
      }
      
      // Show emergency contact for urgent matters
      if (emergencyPhone && (userMessage.toLowerCase().includes('emergency') || userMessage.toLowerCase().includes('urgent'))) {
        contactInfo += `\n🚨 **Emergency:** ${emergencyPhone}`;
      }
      
      if (officeHours) {
        contactInfo += `\n⏰ **Office Hours:** ${officeHours}`;
      }
    }
    
    const baseMessage = firmName ? 
      `I apologize, but I'm currently experiencing technical difficulties. Please try again in a moment, or contact ${firmName} directly:${contactInfo}` :
      `I apologize, but I'm currently experiencing technical difficulties. Please try again in a moment, or contact our support team directly:${contactInfo}`;
    
    return baseMessage || 'I apologize, but I\'m currently experiencing technical difficulties. Please try again or contact our support team.';
  }
  
  // Auto-scroll to bottom of messages
  function scrollToBottom() {
    if (messagesContainer) {
      setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }, 100);
    }
  }

  async function sendMessage() {
    if (!currentMessage.trim()) return;
    
    const userMessage = {
      id: crypto.randomUUID(),
      content: currentMessage,
      type: 'user' as const,
      timestamp: new Date()
    };
    
    messages = [...messages, userMessage];
    scrollToBottom();
    
    const userInput = currentMessage;
    currentMessage = '';
    isLoading = true;
    
    try {
      // Connect to FastAPI backend simple chat endpoint
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/simple-chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
      });
      
      const data = await response.json();
      
      const assistantMessage = {
        id: crypto.randomUUID(),
        content: data.response || 'I apologize, but I\'m having trouble connecting to our legal database. Please try again.',
        type: 'assistant' as const,
        timestamp: new Date()
      };
      
      messages = [...messages, assistantMessage];
      scrollToBottom();
    } catch (error) {
      const errorMessage = {
        id: crypto.randomUUID(),
        content: createErrorMessage(userInput),
        type: 'assistant' as const,
        timestamp: new Date()
      };
      messages = [...messages, errorMessage];
      scrollToBottom();
    } finally {
      isLoading = false;
    }
  }
  
  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<Card class="h-full flex flex-col">
  <!-- Header -->
  <div class="flex items-center justify-between p-4 border-b border-legal-gray-200 flex-shrink-0">
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 bg-legal-primary rounded-full flex items-center justify-center">
        <span class="text-white font-semibold text-sm">V</span>
      </div>
      <div>
        <h3 class="font-semibold text-legal-gray-900">Legal Assistant</h3>
        <p class="text-xs text-legal-gray-500">Professional legal guidance</p>
      </div>
    </div>
    
    <Button variant="accent" size="sm" class="flex items-center space-x-1">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
      </svg>
      <span class="text-xs">Call</span>
    </Button>
  </div>
  
  <!-- Messages -->
  <div bind:this={messagesContainer} class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
    {#if messages.length === 0}
      <div class="text-center text-legal-gray-500 py-8">
        <p class="mb-2">Welcome to Verdict360 Legal Assistant</p>
        <p class="text-sm">Ask me any legal question</p>
      </div>
    {/if}
    
    {#each messages as message (message.id)}
      <ChatMessage {message} />
    {/each}
    
    {#if isLoading}
      <div class="flex items-center space-x-2 text-legal-gray-500">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="animate-spin">
          <path d="M21 12a9 9 0 11-6.219-8.56"/>
        </svg>
        <span class="text-sm">Legal assistant is thinking...</span>
      </div>
    {/if}
  </div>
  
  <!-- Input -->
  <div class="p-4 border-t border-legal-gray-200 flex-shrink-0">
    <div class="flex space-x-2">
      <textarea
        bind:value={currentMessage}
        placeholder="Ask any legal question..."
        rows="2"
        class="flex-1 resize-none textarea-legal text-sm"
        on:keydown={handleKeyPress}
        disabled={isLoading}
      ></textarea>
      <Button 
        variant="primary" 
        size="md"
        disabled={!currentMessage.trim() || isLoading}
        on:click={sendMessage}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="white" stroke="none">
          <path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/>
        </svg>
      </Button>
    </div>
    
    <p class="text-xs text-legal-gray-400 mt-2 leading-relaxed">
      Press Enter to send, Shift+Enter for new line
    </p>
  </div>
</Card>