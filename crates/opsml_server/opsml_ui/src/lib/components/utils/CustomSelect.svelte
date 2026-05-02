<script lang="ts">
  import { ChevronDown } from 'lucide-svelte';

  let {
    label,
    options,
    value = null,
    disabled = false,
    placeholder = 'all',
    onChange,
  }: {
    label: string;
    options: { value: string; label: string }[];
    value?: string | null;
    disabled?: boolean;
    placeholder?: string;
    onChange: (value: string | null) => void;
  } = $props();

  let isOpen = $state(false);
  let wrapperEl: HTMLDivElement;

  // Optimistic local value so the trigger label updates immediately on click,
  // without waiting for the parent's async refetch to echo back applied_filters.
  let localValue = $state<string | null>(value ?? null);

  // Sync from parent whenever the confirmed applied value arrives.
  $effect(() => {
    localValue = value ?? null;
  });

  const selectedLabel = $derived(
    localValue === null
      ? placeholder
      : (options.find((o) => o.value === localValue)?.label ?? placeholder),
  );

  function toggle() {
    if (!disabled) isOpen = !isOpen;
  }

  function select(v: string | null) {
    localValue = v;
    onChange(v);
    isOpen = false;
  }

  function handleClickOutside(event: MouseEvent) {
    if (wrapperEl && !wrapperEl.contains(event.target as Node)) {
      isOpen = false;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      isOpen = false;
    }
  }

  $effect(() => {
    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  });
</script>

<div bind:this={wrapperEl} class="relative">
  <button
    type="button"
    onclick={toggle}
    onkeydown={handleKeydown}
    class="flex items-center gap-1 px-2 py-1 min-w-[5rem] border-2 border-primary-800 bg-surface-50 rounded-base font-mono text-xs text-primary-950 shadow-small transition-colors duration-100 hover:bg-primary-50
      {disabled ? 'opacity-60 cursor-not-allowed pointer-events-none' : 'cursor-pointer'}"
    aria-haspopup="listbox"
    aria-expanded={isOpen}
    aria-label={label}
    {disabled}
  >
    <span class="truncate max-w-[8rem]">{selectedLabel}</span>
    <ChevronDown class="w-3 h-3 flex-shrink-0 transition-transform duration-100 {isOpen ? 'rotate-180' : ''}" />
  </button>

  {#if isOpen}
    <div
      role="listbox"
      aria-label={label}
      class="absolute top-full left-0 mt-1 z-50 w-max min-w-[8rem] max-w-[14rem] bg-surface-50 border-2 border-primary-800 rounded-base shadow-primary overflow-hidden"
    >
      <button
        type="button"
        role="option"
        aria-selected={localValue === null}
        onclick={() => select(null)}
        class="w-full px-3 py-1.5 text-left text-xs font-mono text-primary-950 hover:bg-primary-300 transition-colors duration-100
          {localValue === null ? 'bg-primary-50 font-bold text-primary-800' : ''}"
      >
        {placeholder}
      </button>
      {#each options as opt (opt.value)}
        <button
          type="button"
          role="option"
          aria-selected={localValue === opt.value}
          onclick={() => select(opt.value)}
          class="w-full px-3 py-1.5 text-left text-xs font-mono text-primary-950 hover:bg-primary-300 transition-colors duration-100
            {localValue === opt.value ? 'bg-primary-50 font-bold text-primary-800' : ''}"
        >
          {opt.label}
        </button>
      {/each}
    </div>
  {/if}
</div>

