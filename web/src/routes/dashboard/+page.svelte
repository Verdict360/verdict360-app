<script lang="ts">
  import { onMount } from 'svelte';
  // Using flat SVG icons for better contrast and professional appearance
  import Card from '@/lib/components/ui/Card.svelte';
  import Button from '@/lib/components/ui/Button.svelte';
  
  let stats = {
    totalChats: 0,
    activeClients: 0,
    consultations: 0,
    satisfaction: 0
  };
  
  onMount(async () => {
    // Simulate loading dashboard data
    stats = {
      totalChats: 147,
      activeClients: 23,
      consultations: 12,
      satisfaction: 96
    };
  });
</script>

<svelte:head>
  <title>Dashboard - Verdict360</title>
  <meta name="description" content="Legal practice management dashboard" />
</svelte:head>

<div class="min-h-screen bg-legal-gray-50">
  <!-- Header -->
  <header class="bg-white border-b border-legal-gray-200">
    <div class="legal-container py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-legal-gray-900">Legal Dashboard</h1>
          <p class="text-legal-gray-600">Manage your legal practice with AI assistance</p>
        </div>
        
        <div class="flex items-center space-x-4">
          <Button variant="accent" size="md" class="flex items-center space-x-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
            <span>Emergency Consult</span>
          </Button>
          
          <Button variant="outline" size="md">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m5.636-5.636l4.242 4.242m4.243 4.243l4.242 4.242M7.757 16.243l4.242-4.242m4.243-4.243l4.242-4.242"/>
            </svg>
          </Button>
        </div>
      </div>
    </div>
  </header>
  
  <!-- Main Content -->
  <main class="py-8">
    <div class="legal-container">
      <!-- Stats Grid -->
      <div class="legal-grid mb-8">
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#1E40AF" stroke-width="2">
              <path d="M20 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4l4 4 4-4h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
            </svg>
          </div>
          <div class="text-2xl font-bold text-legal-gray-900">{stats.totalChats}</div>
          <div class="text-sm text-legal-gray-600">Total Legal Chats</div>
        </Card>
        
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <div class="text-2xl font-bold text-legal-gray-900">{stats.activeClients}</div>
          <div class="text-sm text-legal-gray-600">Active Clients</div>
        </Card>
        
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2">
              <line x1="12" y1="20" x2="12" y2="10"/>
              <line x1="18" y1="20" x2="18" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="16"/>
            </svg>
          </div>
          <div class="text-2xl font-bold text-legal-gray-900">{stats.consultations}</div>
          <div class="text-sm text-legal-gray-600">This Month</div>
        </Card>
      </div>
      
      <!-- Quick Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Legal Tools -->
        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Legal AI Tools</h3>
          <div class="space-y-3">
            <a href="/chatbot" class="flex items-center p-3 bg-legal-gray-50 rounded-legal hover:bg-legal-gray-100 transition-colors">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1E40AF" stroke-width="2" class="mr-3">
                <path d="M20 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4l4 4 4-4h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
              </svg>
              <div>
                <div class="font-medium text-legal-gray-900">Legal Chat Assistant</div>
                <div class="text-sm text-legal-gray-600">Get AI legal guidance with SA law citations</div>
              </div>
            </a>
            
            <a href="/consultation" class="flex items-center p-3 bg-legal-gray-50 rounded-legal hover:bg-legal-gray-100 transition-colors">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" class="mr-3">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              <div>
                <div class="font-medium text-legal-gray-900">Client Consultations</div>
                <div class="text-sm text-legal-gray-600">Schedule and manage client meetings</div>
              </div>
            </a>
            
            <div class="flex items-center p-3 bg-legal-gray-50 rounded-legal">
              <FileText class="h-5 w-5 text-legal-gold mr-3" />
              <div>
                <div class="font-medium text-legal-gray-900">Document Analysis</div>
                <div class="text-sm text-legal-gray-600">AI-powered legal document review</div>
              </div>
            </div>
          </div>
        </Card>
        
        <!-- Recent Activity -->
        <Card>
          <h3 class="text-lg font-semibold text-legal-gray-900 mb-4">Recent Activity</h3>
          <div class="space-y-3">
            <div class="flex items-center p-3 border-l-4 border-legal-primary bg-legal-primary/5">
              <div class="flex-1">
                <div class="font-medium text-legal-gray-900">Constitutional Law Query</div>
                <div class="text-sm text-legal-gray-600">Client asked about freedom of expression rights</div>
                <div class="text-xs text-legal-gray-500 mt-1">2 hours ago</div>
              </div>
            </div>
            
            <div class="flex items-center p-3 border-l-4 border-legal-accent bg-legal-accent/5">
              <div class="flex-1">
                <div class="font-medium text-legal-gray-900">New Client Consultation</div>
                <div class="text-sm text-legal-gray-600">Property law consultation scheduled</div>
                <div class="text-xs text-legal-gray-500 mt-1">4 hours ago</div>
              </div>
            </div>
            
            <div class="flex items-center p-3 border-l-4 border-legal-gold bg-legal-gold/5">
              <div class="flex-1">
                <div class="font-medium text-legal-gray-900">Document Processed</div>
                <div class="text-sm text-legal-gray-600">Contract analysis completed with 95% confidence</div>
                <div class="text-xs text-legal-gray-500 mt-1">6 hours ago</div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </main>
</div>