<script lang="ts">
  import { Send, Phone, Loader2 } from 'lucide-svelte';
  import Button from '@/lib/components/ui/Button.svelte';
  import Card from '@/lib/components/ui/Card.svelte';
  import ChatMessage from './ChatMessage.svelte';
  
  export let isEmbedded = false;
  
  let messages: Array<{id: string, content: string, type: 'user' | 'assistant', timestamp: Date}> = [];
  let currentMessage = '';
  let isLoading = false;
  
  async function sendMessage() {
    if (!currentMessage.trim()) return;
    
    const userMessage = {
      id: crypto.randomUUID(),
      content: currentMessage,
      type: 'user' as const,
      timestamp: new Date()
    };
    
    messages = [...messages, userMessage];
    const userInput = currentMessage;
    currentMessage = '';
    isLoading = true;
    
    try {
      // This would connect to your FastAPI backend
      const response = await fetch('/api/chat', {
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
    } catch (error) {
      const errorMessage = {
        id: crypto.randomUUID(),
        content: 'I apologize, but I\'m currently experiencing technical difficulties. Please try again or contact our support team.',
        type: 'assistant' as const,
        timestamp: new Date()
      };
      messages = [...messages, errorMessage];
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

<Card class={isEmbedded ? 'h-96' : 'h-128'}>
  <!-- Header -->
  <div class="flex items-center justify-between p-4 border-b border-legal-gray-200">
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
      <Phone class="h-3 w-3" />
      <span class="text-xs">Call</span>
    </Button>
  </div>
  
  <!-- Messages -->
  <div class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
    {#if messages.length === 0}
      <div class="text-center text-legal-gray-500 py-8">
        <p class="mb-2">Welcome to Verdict360 Legal Assistant</p>
        <p class="text-sm">Ask me any South African legal question</p>
      </div>
    {/if}
    
    {#each messages as message (message.id)}
      <ChatMessage {message} />
    {/each}
    
    {#if isLoading}
      <div class="flex items-center space-x-2 text-legal-gray-500">
        <Loader2 class="h-4 w-4 animate-spin" />
        <span class="text-sm">Legal assistant is thinking...</span>
      </div>
    {/if}
  </div>
  
  <!-- Input -->
  <div class="p-4 border-t border-legal-gray-200">
    <div class="flex space-x-2">
      <textarea
        bind:value={currentMessage}
        placeholder="Ask your legal question..."
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
        <Send class="h-4 w-4" />
      </Button>
    </div>
    
    <p class="text-xs text-legal-gray-400 mt-2">
      Press Enter to send, Shift+Enter for new line
    </p>
  </div>
</Card>