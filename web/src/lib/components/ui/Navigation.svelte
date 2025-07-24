<script lang="ts">
  import { page } from '$app/stores';
  
  $: currentPath = $page.url.pathname;
  
  const navigationItems = [
    { href: '/', label: 'Home', icon: 'home' },
    { href: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { href: '/chatbot', label: 'AI Assistant', icon: 'chat' },
    { href: '/consultation', label: 'Consultations', icon: 'calendar' },
    { href: '/widget', label: 'Widget Demo', icon: 'widget' }
  ];
  
  function isActive(href: string): boolean {
    if (href === '/') {
      return currentPath === '/';
    }
    return currentPath.startsWith(href);
  }
</script>

<nav class="bg-white border-b border-legal-gray-200">
  <div class="legal-container">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <div class="flex items-center space-x-4">
        <a href="/" class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-legal-primary rounded-lg flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
              <path d="M14 9V5a3 3 0 0 0-6 0v4"/>
              <rect x="2" y="11" width="20" height="11" rx="2" ry="2"/>
            </svg>
          </div>
          <span class="text-xl font-bold text-legal-gray-900">Verdict360</span>
        </a>
      </div>
      
      <!-- Main Navigation -->
      <div class="hidden md:block">
        <div class="flex items-center space-x-1">
          {#each navigationItems as item}
            <a 
              href={item.href}
              class="px-3 py-2 text-sm font-medium rounded-legal transition-colors {isActive(item.href) 
                ? 'bg-legal-primary text-white' 
                : 'text-legal-gray-600 hover:text-legal-gray-900 hover:bg-legal-gray-100'}"
            >
              <div class="flex items-center space-x-2">
                {#if item.icon === 'home'}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                    <polyline points="9,22 9,12 15,12 15,22"/>
                  </svg>
                {:else if item.icon === 'dashboard'}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="7" height="7"/>
                    <rect x="14" y="3" width="7" height="7"/>
                    <rect x="14" y="14" width="7" height="7"/>
                    <rect x="3" y="14" width="7" height="7"/>
                  </svg>
                {:else if item.icon === 'chat'}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4l4 4 4-4h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
                  </svg>
                {:else if item.icon === 'calendar'}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                {:else if item.icon === 'widget'}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="6" height="6" rx="1"/>
                    <rect x="15" y="3" width="6" height="6" rx="1"/>
                    <rect x="3" y="15" width="6" height="6" rx="1"/>
                    <rect x="15" y="15" width="6" height="6" rx="1"/>
                  </svg>
                {/if}
                <span>{item.label}</span>
              </div>
            </a>
          {/each}
        </div>
      </div>
      
      <!-- Right side actions -->
      <div class="flex items-center space-x-4">
        <button class="p-2 text-legal-gray-600 hover:text-legal-gray-900 hover:bg-legal-gray-100 rounded-legal">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
        </button>
        
        <button class="p-2 text-legal-gray-600 hover:text-legal-gray-900 hover:bg-legal-gray-100 rounded-legal">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </button>
        
        <!-- Profile dropdown placeholder -->
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-legal-gray-300 rounded-full"></div>
          <span class="text-sm font-medium text-legal-gray-900">Law Firm</span>
        </div>
      </div>
      
      <!-- Mobile menu button -->
      <div class="md:hidden">
        <button class="p-2 text-legal-gray-600 hover:text-legal-gray-900">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</nav>