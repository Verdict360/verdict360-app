<script lang="ts">
  import { Send, Phone, Loader2, Mic, MicOff, PhoneOff } from 'lucide-svelte';
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
  
  // Voice functionality
  let isCallActive = false;
  let isListening = false;
  let isSpeaking = false;
  let recognition: any = null;
  let speechSynthesis: any = null;
  let currentUtterance: any = null;
  
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

  
  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  // Voice functionality
  function initializeVoice() {
    if (typeof window !== 'undefined') {
      // Initialize Speech Recognition
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-ZA'; // South African English
        
        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          currentMessage = transcript;
          isListening = false;
          // Automatically send the voice message
          setTimeout(() => sendMessage(), 500);
        };
        
        recognition.onerror = () => {
          isListening = false;
        };
        
        recognition.onend = () => {
          isListening = false;
        };
      }
      
      // Initialize Speech Synthesis
      speechSynthesis = window.speechSynthesis;
    }
  }

  function startCall() {
    initializeVoice();
    isCallActive = true;
    
    // Welcome message when call starts
    const welcomeMessage = firmName 
      ? `Hello! You've reached ${firmName}'s AI legal assistant. How can I help you with your legal matter today?`
      : "Hello! You've reached our AI legal assistant. How can I help you with your legal matter today?";
    
    speakText(welcomeMessage);
    
    // Add welcome message to chat
    const welcomeMsg = {
      id: crypto.randomUUID(),
      content: welcomeMessage,
      type: 'assistant' as const,
      timestamp: new Date()
    };
    messages = [...messages, welcomeMsg];
    scrollToBottom();
  }

  function endCall() {
    isCallActive = false;
    isListening = false;
    isSpeaking = false;
    
    if (recognition) {
      recognition.stop();
    }
    
    if (currentUtterance) {
      speechSynthesis.cancel();
      currentUtterance = null;
    }
  }

  function toggleListening() {
    if (!recognition) {
      initializeVoice();
    }
    
    if (isListening) {
      recognition.stop();
      isListening = false;
    } else {
      if (isSpeaking) {
        speechSynthesis.cancel();
        isSpeaking = false;
      }
      recognition.start();
      isListening = true;
    }
  }

  function speakText(text: string) {
    if (!speechSynthesis) return;
    
    // Stop any current speech
    speechSynthesis.cancel();
    
    // Clean text for speech (remove markdown and buttons)
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
      .replace(/\*(.*?)\*/g, '$1') // Remove italic markdown
      .replace(/\[SCHEDULE_CONSULTATION\]/g, 'You can schedule a consultation')
      .replace(/\[CONTACT_FIRM\]/g, 'or contact our firm directly')
      .replace(/#{1,6}\s/g, '') // Remove headers
      .replace(/^\s*[\-\*\+]\s/gm, '') // Remove bullet points
      .replace(/^\s*\d+\.\s/gm, '') // Remove numbered lists
      .trim();
    
    if (cleanText) {
      currentUtterance = new SpeechSynthesisUtterance(cleanText);
      
      // Try to use South African English voice, fallback to any English voice
      const voices = speechSynthesis.getVoices();
      const saVoice = voices.find(voice => voice.lang.includes('en-ZA')) ||
                      voices.find(voice => voice.lang.includes('en-GB')) ||
                      voices.find(voice => voice.lang.includes('en'));
      
      if (saVoice) {
        currentUtterance.voice = saVoice;
      }
      
      currentUtterance.rate = 0.9; // Slightly slower for legal content
      currentUtterance.pitch = 1.0;
      currentUtterance.volume = 0.8;
      
      currentUtterance.onstart = () => {
        isSpeaking = true;
      };
      
      currentUtterance.onend = () => {
        isSpeaking = false;
        currentUtterance = null;
      };
      
      currentUtterance.onerror = () => {
        isSpeaking = false;
        currentUtterance = null;
      };
      
      speechSynthesis.speak(currentUtterance);
    }
  }

  // Override sendMessage to add voice functionality
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
      
      // If in call mode, speak the response
      if (isCallActive && assistantMessage.content) {
        speakText(assistantMessage.content);
      }
      
    } catch (error) {
      const errorMessage = {
        id: crypto.randomUUID(),
        content: createErrorMessage(userInput),
        type: 'assistant' as const,
        timestamp: new Date()
      };
      messages = [...messages, errorMessage];
      scrollToBottom();
      
      // If in call mode, speak the error message
      if (isCallActive) {
        speakText(errorMessage.content);
      }
    } finally {
      isLoading = false;
    }
  }
</script>

<Card class="h-[96%] flex flex-col">
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
    
{#if !isCallActive}
      <Button variant="accent" size="sm" class="flex items-center space-x-1" on:click={startCall}>
        <Phone class="h-3 w-3" />
        <span class="text-xs">Call</span>
      </Button>
    {:else}
      <Button variant="destructive" size="sm" class="flex items-center space-x-1" on:click={endCall}>
        <PhoneOff class="h-3 w-3" />
        <span class="text-xs">End Call</span>
      </Button>
    {/if}
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
    {#if isCallActive}
      <!-- Voice Call Controls -->
      <div class="text-center space-y-3">
        <div class="bg-legal-success/10 border border-legal-success/20 rounded-legal p-3">
          <div class="flex items-center justify-center space-x-2 mb-2">
            <div class="w-2 h-2 bg-legal-success rounded-full animate-pulse"></div>
            <span class="text-sm font-medium text-legal-success">Call Active</span>
          </div>
          
          {#if isSpeaking}
            <p class="text-xs text-legal-gray-600">AI is speaking...</p>
          {:else if isListening}
            <p class="text-xs text-legal-gray-600">Listening... speak now</p>
          {:else}
            <p class="text-xs text-legal-gray-600">Press the microphone to speak</p>
          {/if}
        </div>
        
        <div class="flex justify-center space-x-4">
          <Button 
            variant={isListening ? "destructive" : "primary"}
            size="lg"
            class="rounded-full w-16 h-16 flex items-center justify-center"
            on:click={toggleListening}
            disabled={isSpeaking}
          >
            {#if isListening}
              <MicOff class="h-6 w-6" />
            {:else}
              <Mic class="h-6 w-6" />
            {/if}
          </Button>
        </div>
        
        <p class="text-xs text-legal-gray-400">
          Tap microphone to speak your legal question
        </p>
      </div>
    {:else}
      <!-- Regular Text Input -->
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
          <Send class="h-4 w-4" />
        </Button>
      </div>
      
      <p class="text-xs text-legal-gray-400 mt-2 leading-relaxed">
        Press Enter to send, Shift+Enter for new line
      </p>
    {/if}
  </div>
</Card>