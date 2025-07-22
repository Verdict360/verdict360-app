<script lang="ts">
  import { Scale, MessageSquare, Users, BarChart3 } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Verdict360 - AI Legal Chatbot Platform</title>
  <meta name="description" content="Professional AI legal assistance for South African law firms" />
</svelte:head>

<!-- Hero Section -->
<div class="relative bg-white overflow-hidden">
  <div class="legal-container">
    <div class="relative z-10 pt-16 pb-20 sm:pt-24 sm:pb-32 lg:pt-32 lg:pb-40">
      <div class="text-center">
        <div class="flex justify-center mb-8">
          <Scale class="h-16 w-16 text-legal-primary" />
        </div>
        
        <h1 class="text-4xl font-bold tracking-tight text-legal-gray-900 sm:text-5xl lg:text-6xl">
          <span class="legal-text-gradient">Verdict360</span><br />
          AI Legal Chatbot Platform
        </h1>
        
        <p class="mt-6 max-w-2xl mx-auto text-xl text-legal-gray-600">
          Professional AI legal assistance designed specifically for South African law firms. 
          Get accurate legal guidance with verified citations and POPIA compliance.
        </p>
        
        <div class="mt-10 flex justify-center gap-4">
          <a href="/dashboard" class="btn-legal-primary text-lg px-8 py-3">
            Start Free Trial
          </a>
          <a href="/chatbot" class="btn-legal-secondary text-lg px-8 py-3">
            Try Demo
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Features Section -->
<div class="py-20 bg-legal-gray-50">
  <div class="legal-container">
    <div class="text-center mb-16">
      <h2 class="text-3xl font-bold text-legal-gray-900">
        Built for South African Law Firms
      </h2>
      <p class="mt-4 text-xl text-legal-gray-600">
        Professional legal intelligence with R5,000-R10,000 monthly value
      </p>
    </div>
    
    <div class="legal-grid">
      <!-- Legal Chat Feature -->
      <div class="card-legal p-8 text-center">
        <MessageSquare class="h-12 w-12 text-legal-primary mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-legal-gray-900 mb-3">
          AI Legal Chat
        </h3>
        <p class="text-legal-gray-600">
          Intelligent legal assistance with verified SA legal citations and case law references.
        </p>
      </div>

      <!-- Client Management -->  
      <div class="card-legal p-8 text-center">
        <Users class="h-12 w-12 text-legal-accent mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-legal-gray-900 mb-3">
          Client Management
        </h3>
        <p class="text-legal-gray-600">
          Streamlined client consultations with professional intake forms and scheduling.
        </p>
      </div>

      <!-- Analytics -->
      <div class="card-legal p-8 text-center">
        <BarChart3 class="h-12 w-12 text-legal-gold mx-auto mb-4" />
        <h3 class="text-xl font-semibold text-legal-gray-900 mb-3">
          Legal Analytics
        </h3>
        <p class="text-legal-gray-600">
          Comprehensive analytics and reporting for law firm performance optimization.
        </p>
      </div>
    </div>
  </div>
</div>

<!-- CTA Section -->
<div class="bg-legal-secondary py-16">
  <div class="legal-container text-center">
    <h2 class="text-3xl font-bold text-white mb-4">
      Ready to Transform Your Legal Practice?
    </h2>
    <p class="text-xl text-legal-gray-300 mb-8 max-w-2xl mx-auto">
      Join the growing number of SA law firms using AI to enhance their legal services
    </p>
    <a href="/consultation" class="btn-legal-accent text-lg px-8 py-3">
      Book Consultation
    </a>
  </div>
</div>