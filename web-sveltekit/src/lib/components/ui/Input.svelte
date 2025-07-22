<script lang="ts">
  import { cn } from '@/lib/utils';

  export let type: 'text' | 'email' | 'password' | 'tel' | 'url' = 'text';
  export let value = '';
  export let placeholder = '';
  export let disabled = false;
  export let required = false;
  export let label = '';
  export let error = '';
  export let id = '';
</script>

<div class="space-y-1">
  {#if label}
    <label for={id} class="block text-sm font-medium text-legal-gray-700">
      {label}
      {#if required}
        <span class="text-legal-error">*</span>
      {/if}
    </label>
  {/if}

  <input
    {id}
    {placeholder}
    {disabled}
    {required}
    bind:value
    class={cn(
      'input-legal',
      error && 'border-legal-error focus:border-legal-error focus:ring-legal-error',
      $$props.class
    )}
    on:input
    on:change
    on:focus
    on:blur
  />

  {#if error}
    <p class="text-sm text-legal-error">{error}</p>
  {/if}
</div>
