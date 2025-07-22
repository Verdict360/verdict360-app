<script lang="ts">
  import { cn } from '@/lib/utils';
  
  export let variant: 'primary' | 'secondary' | 'accent' | 'outline' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let disabled = false;
  export let type: 'button' | 'submit' | 'reset' = 'button';
  
  const variants = {
    primary: 'btn-legal-primary',
    secondary: 'btn-legal-secondary', 
    accent: 'btn-legal-accent',
    outline: 'border border-legal-primary text-legal-primary hover:bg-legal-primary hover:text-white'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
</script>

<button 
  {type}
  {disabled}
  class={cn(
    'font-medium rounded-legal transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-legal-primary focus:ring-offset-2',
    variants[variant],
    sizes[size],
    disabled && 'opacity-50 cursor-not-allowed',
    $$props.class
  )}
  on:click
>
  <slot />
</button>