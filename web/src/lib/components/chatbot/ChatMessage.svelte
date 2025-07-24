<script lang="ts">
  import { User, Scale, Calendar, Phone } from 'lucide-svelte';
  import Button from '$lib/components/ui/Button.svelte';
  
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
  
  // Process message content to extract conversion buttons
  function processMessageContent(content: string) {
    // Extract text content and button actions
    const scheduleButtonPattern = /\[SCHEDULE_CONSULTATION\]/g;
    const contactButtonPattern = /\[CONTACT_FIRM\]/g;
    
    const hasScheduleButton = scheduleButtonPattern.test(content);
    const hasContactButton = contactButtonPattern.test(content);
    
    // Remove button placeholders from display text
    const cleanContent = content
      .replace(scheduleButtonPattern, '')
      .replace(contactButtonPattern, '')
      .trim();
    
    return {
      text: cleanContent,
      showScheduleButton: hasScheduleButton,
      showContactButton: hasContactButton
    };
  }
  
  $: processedMessage = processMessageContent(message.content);
  
  function handleScheduleConsultation() {
    // Navigate to consultation booking
    window.location.href = '/consultation';
  }
  
  function handleContactFirm() {
    // Open contact modal or navigate to contact page
    // For now, scroll to contact section or use tel: link
    window.location.href = 'tel:+27-11-123-4567';
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
        <p class="text-sm whitespace-pre-wrap">{processedMessage.text}</p>
        
        <!-- Conversion Buttons for Assistant Messages -->
        {#if message.type === 'assistant' && (processedMessage.showScheduleButton || processedMessage.showContactButton)}
          <div class="flex flex-col space-y-2 mt-3 pt-3 border-t border-legal-gray-200">
            {#if processedMessage.showScheduleButton}
              <Button 
                variant="primary" 
                size="sm" 
                class="flex items-center space-x-2 w-full justify-center"
                on:click={handleScheduleConsultation}
              >
                <Calendar class="h-4 w-4" />
                <span>Schedule Consultation</span>
              </Button>
            {/if}
            
            {#if processedMessage.showContactButton}
              <Button 
                variant="outline" 
                size="sm" 
                class="flex items-center space-x-2 w-full justify-center"
                on:click={handleContactFirm}
              >
                <Phone class="h-4 w-4" />
                <span>Contact Firm</span>
              </Button>
            {/if}
          </div>
        {/if}
      </div>
      
      <span class="text-xs text-legal-gray-400 mt-1">
        {formatTime(message.timestamp)}
      </span>
    </div>
  </div>
</div>