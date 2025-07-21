<script lang="ts">
  import { cn } from '@/lib/utils';
  
  export let padding = true;
  export let hover = false;
</script>

<div 
  class={cn(
    'card-legal',
    padding && 'p-6',
    hover && 'hover:shadow-legal-lg transition-shadow duration-200',
    $$props.class
  )}
>
  <slot />
</div>