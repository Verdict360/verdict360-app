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
  let autoListenTimeout: any = null;
  let silenceTimeout: any = null;
  
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
        recognition.continuous = true; // Keep listening
        recognition.interimResults = true; // Show interim results
        recognition.lang = 'en-ZA'; // South African English
        
        recognition.onresult = (event: any) => {
          let finalTranscript = '';
          let interimTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }
          
          if (finalTranscript) {
            currentMessage = finalTranscript.trim();
            // Clear any existing silence timeout
            if (silenceTimeout) {
              clearTimeout(silenceTimeout);
            }
            // Stop listening and send message
            stopListening();
            setTimeout(() => sendMessage(), 300);
          } else {
            // Show interim results
            currentMessage = interimTranscript.trim();
          }
        };
        
        recognition.onerror = (event: any) => {
          console.log('Speech recognition error:', event.error);
          if (isCallActive && event.error !== 'no-speech') {
            // Restart listening after error (except for no-speech)
            setTimeout(() => startListening(), 1000);
          }
        };
        
        recognition.onend = () => {
          isListening = false;
          // If call is still active and we're not speaking, restart listening
          if (isCallActive && !isSpeaking) {
            setTimeout(() => startListening(), 500);
          }
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
    
    // Clear any timeouts
    if (autoListenTimeout) clearTimeout(autoListenTimeout);
    if (silenceTimeout) clearTimeout(silenceTimeout);
    
    if (recognition) {
      recognition.stop();
    }
    
    if (currentUtterance) {
      speechSynthesis.cancel();
      currentUtterance = null;
    }
  }

  function startListening() {
    if (!recognition || !isCallActive) return;
    
    if (isSpeaking) {
      // Wait for speaking to finish
      setTimeout(() => startListening(), 500);
      return;
    }
    
    try {
      isListening = true;
      recognition.start();
    } catch (error) {
      console.log('Recognition start error:', error);
      isListening = false;
    }
  }

  function stopListening() {
    if (recognition && isListening) {
      isListening = false;
      recognition.stop();
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
        
        // Automatically start listening after AI finishes speaking (if in call)
        if (isCallActive) {
          autoListenTimeout = setTimeout(() => {
            startListening();
          }, 1000); // Give 1 second pause after AI stops speaking
        }
      };
      
      currentUtterance.onerror = () => {
        isSpeaking = false;
        currentUtterance = null;
        
        // Start listening even after speech error
        if (isCallActive) {
          autoListenTimeout = setTimeout(() => {
            startListening();
          }, 1000);
        }
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
      <!-- Voice Call Interface -->
      <div class="text-center space-y-4">
        <div class="bg-legal-success/10 border border-legal-success/20 rounded-legal p-4">
          <div class="flex items-center justify-center space-x-2 mb-3">
            <div class="w-3 h-3 bg-legal-success rounded-full animate-pulse"></div>
            <span class="text-sm font-semibold text-legal-success">Voice Call Active</span>
          </div>
          
          {#if isSpeaking}
            <div class="flex items-center justify-center space-x-2">
              <div class="flex space-x-1">
                <div class="w-2 h-6 bg-legal-primary rounded-full animate-pulse"></div>
                <div class="w-2 h-4 bg-legal-primary rounded-full animate-pulse" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-8 bg-legal-primary rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
                <div class="w-2 h-3 bg-legal-primary rounded-full animate-pulse" style="animation-delay: 0.3s"></div>
                <div class="w-2 h-6 bg-legal-primary rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
              </div>
            </div>
            <p class="text-sm text-legal-gray-700 mt-2">AI Assistant is speaking...</p>
          {:else if isListening}
            <div class="flex items-center justify-center space-x-2">
              <Mic class="h-5 w-5 text-legal-primary animate-pulse" />
              <div class="flex space-x-1">
                <div class="w-2 h-4 bg-legal-accent rounded-full animate-bounce"></div>
                <div class="w-2 h-6 bg-legal-accent rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-4 bg-legal-accent rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
            </div>
            <p class="text-sm text-legal-gray-700 mt-2">Listening... please speak</p>
            {#if currentMessage}
              <p class="text-xs text-legal-gray-500 mt-1 italic">"{currentMessage}"</p>
            {/if}
          {:else}
            <div class="flex items-center justify-center">
              <Phone class="h-5 w-5 text-legal-primary" />
            </div>
            <p class="text-sm text-legal-gray-700 mt-2">Ready for your question</p>
          {/if}
        </div>
        
        <p class="text-xs text-legal-gray-500 leading-relaxed">
          Speak naturally - the AI will automatically listen after responding
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