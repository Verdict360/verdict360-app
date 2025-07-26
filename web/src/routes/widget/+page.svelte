<script lang="ts">
  import ChatWidget from '@/lib/components/chatbot/ChatWidget.svelte';
  
  // This page is designed to be embedded as an iframe
  export let isEmbedded = true;
</script>

<svelte:head>
  <title>Legal Chatbot Widget - Verdict360</title>
  <meta name="description" content="Embeddable legal chatbot widget for law firm websites" />
  <meta name="robots" content="noindex, nofollow" />
</svelte:head>

<!-- Minimal layout for embedding -->
<div class="h-screen flex flex-col bg-legal-gray-50 p-2">
  <div class="flex-1 flex flex-col min-h-0">
    <ChatWidget {isEmbedded} />
  </div>
</div>

<style>
  :global(body) {
    margin: 0;
    overflow: hidden;
  }
</style>