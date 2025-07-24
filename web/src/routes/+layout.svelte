<script lang="ts">
  import '../app.css';
  import Navigation from '$lib/components/ui/Navigation.svelte';
  
  export let data;
</script>

<div class="min-h-screen bg-legal-gray-50">
  <Navigation />
  <slot />
</div>