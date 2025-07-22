<script lang="ts">
  import { User, Scale } from 'lucide-svelte';
  
  export let message: {
    id: string;
    content: string;
    type: 'user' | 'assistant';
    timestamp: Date;
  };
  
  function formatTime(date: Date) {
    return date.toLocaleTimeString('en-ZA', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }
</script>

<div class="flex {message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4">
  <div class="flex max-w-sm space-x-2 {message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}">
    <!-- Avatar -->
    <div class="flex-shrink-0">
      <div class="w-8 h-8 rounded-full flex items-center justify-center {message.type === 'user' ? 'bg-legal-primary' : 'bg-legal-accent'}">
        {#if message.type === 'user'}
          <User class="h-4 w-4 text-white" />
        {:else}
          <Scale class="h-4 w-4 text-white" />
        {/if}
      </div>
    </div>
    
    <!-- Message Content -->
    <div class="flex flex-col {message.type === 'user' ? 'items-end' : 'items-start'}">
      <div class="{message.type === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}">
        <p class="text-sm whitespace-pre-wrap">{message.content}</p>
      </div>
      
      <span class="text-xs text-legal-gray-400 mt-1">
        {formatTime(message.timestamp)}
      </span>
    </div>
  </div>
</div>