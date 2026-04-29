<script lang="ts">
  let {
    label,
    count,
    selected,
    onSelect,
  } = $props<{
    label: string;
    count?: number;
    selected: boolean;
    onSelect: () => void;
  }>();
</script>

<button
  type="button"
  onclick={onSelect}
  class="w-full flex items-center justify-between px-2 py-1 text-xs rounded-base transition-colors duration-100
    {selected ? 'bg-primary-200 text-primary-900 font-bold' : 'hover:bg-primary-100 text-black'}"
>
  <span class="flex items-center gap-2 truncate">
    <span
      class="w-3 h-3 border-2 border-black rounded-full flex-shrink-0
        {selected ? 'bg-primary-700' : 'bg-white'}"
    ></span>
    <span class="truncate font-mono">{label}</span>
  </span>
  {#if count !== undefined && count > 0}
    <span class="text-[10px] text-gray-500 font-mono ml-2">{count}</span>
  {/if}
</button>
