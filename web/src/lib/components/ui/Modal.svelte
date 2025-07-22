<script lang="ts">
  import { X } from 'lucide-svelte';
  import Button from './Button.svelte';
  
  export let isOpen = false;
  export let title = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
  
  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md', 
    lg: 'max-w-lg',
    xl: 'max-w-xl'
  };
  
  function closeModal() {
    isOpen = false;
  }
  
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      closeModal();
    }
  }
</script>

{#if isOpen}
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
    on:click={closeModal}
    on:keydown={handleKeydown}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <div 
      class="card-legal w-full {sizes[size]} max-h-screen overflow-y-auto"
      on:click|stopPropagation
      role="document"
    >
      {#if title}
        <div class="flex items-center justify-between p-6 border-b border-legal-gray-200">
          <h3 class="text-lg font-semibold text-legal-gray-900">{title}</h3>
          <Button variant="outline" size="sm" on:click={closeModal}>
            <X class="h-4 w-4" />
          </Button>
        </div>
      {/if}
      
      <div class="p-6">
        <slot />
      </div>
    </div>
  </div>
{/if}