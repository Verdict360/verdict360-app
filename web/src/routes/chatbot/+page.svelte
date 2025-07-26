<script lang="ts">
  import ChatWidget from '@/lib/components/chatbot/ChatWidget.svelte';
  import { ArrowLeft } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Legal Chatbot - Verdict360</title>
  <meta name="description" content="AI-powered legal assistance for South African law" />
</svelte:head>

<div class="min-h-screen bg-legal-gray-50">
  <!-- Header -->
  <header class="bg-white border-b border-legal-gray-200">
    <div class="legal-container py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <a href="/" class="flex items-center text-legal-gray-600 hover:text-legal-primary">
            <ArrowLeft class="h-5 w-5 mr-2" />
            Back to Home
          </a>
        </div>
        
        <div class="text-center">
          <h1 class="text-xl font-semibold text-legal-gray-900">Legal Chatbot Demo</h1>
          <p class="text-sm text-legal-gray-500">Professional AI legal assistance</p>
        </div>
        
        <div class="w-24"></div> <!-- Spacer for centering -->
      </div>
    </div>
  </header>
  
  <!-- Main Content -->
  <main class="py-8">
    <div class="legal-container">
      <div class="max-w-4xl mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Chat Interface -->
          <div class="lg:col-span-2 h-[calc(100vh-12rem)]">
            <ChatWidget />
          </div>
          
          <!-- Information Sidebar -->
          <div class="space-y-6">
            <!-- Features -->
            <div class="card-legal p-6">
              <h3 class="font-semibold text-legal-gray-900 mb-4">Legal AI Features</h3>
              <ul class="space-y-3 text-sm text-legal-gray-600">
                <li class="flex items-start">
                  <span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  SA legal citation verification
                </li>
                <li class="flex items-start">
                  <span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Constitutional Court references
                </li>
                <li class="flex items-start">
                  <span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  POPIA compliance guidance
                </li>
                <li class="flex items-start">
                  <span class="w-2 h-2 bg-legal-primary rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Professional legal drafting
                </li>
              </ul>
            </div>
            
            <!-- Support -->
            <div class="card-legal p-6">
              <h3 class="font-semibold text-legal-gray-900 mb-4">Need Help?</h3>
              <p class="text-sm text-legal-gray-600 mb-4">
                Our legal experts are available for consultations
              </p>
              <a href="/consultation" class="btn-legal-accent w-full text-center block">
                Book Consultation
              </a>
            </div>
            
            <!-- Disclaimer -->
            <div class="bg-legal-warning/10 border border-legal-warning/20 rounded-legal p-4">
              <p class="text-xs text-legal-gray-600">
                <strong>Disclaimer:</strong> This AI provides general legal information only. 
                Always consult with qualified legal professionals for specific legal advice.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</div>