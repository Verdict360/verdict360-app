<script lang="ts">
  import { onMount } from 'svelte';
  import { MessageSquare, Users, BarChart3, Settings, FileText, Phone } from 'lucide-svelte';
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
            <Phone class="h-4 w-4" />
            <span>Emergency Consult</span>
          </Button>
          
          <Button variant="outline" size="md">
            <Settings class="h-5 w-5" />
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
            <MessageSquare class="h-8 w-8 text-legal-primary" />
          </div>
          <div class="text-2xl font-bold text-legal-gray-900">{stats.totalChats}</div>
          <div class="text-sm text-legal-gray-600">Total Legal Chats</div>
        </Card>
        
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <Users class="h-8 w-8 text-legal-accent" />
          </div>
          <div class="text-2xl font-bold text-legal-gray-900">{stats.activeClients}</div>
          <div class="text-sm text-legal-gray-600">Active Clients</div>
        </Card>
        
        <Card class="text-center">
          <div class="flex items-center justify-center mb-3">
            <BarChart3 class="h-8 w-8 text-legal-gold" />
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
              <MessageSquare class="h-5 w-5 text-legal-primary mr-3" />
              <div>
                <div class="font-medium text-legal-gray-900">Legal Chat Assistant</div>
                <div class="text-sm text-legal-gray-600">Get AI legal guidance with SA law citations</div>
              </div>
            </a>
            
            <a href="/consultation" class="flex items-center p-3 bg-legal-gray-50 rounded-legal hover:bg-legal-gray-100 transition-colors">
              <Users class="h-5 w-5 text-legal-accent mr-3" />
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