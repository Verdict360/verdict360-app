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
<div class="p-4 bg-legal-gray-50 min-h-screen">
  <ChatWidget {isEmbedded} />
</div>

<style>
  :global(body) {
    margin: 0;
    overflow: hidden;
  }
</style>