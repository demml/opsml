<script lang="ts">
  import { BarChart2, Search } from "lucide-svelte";
  import type { TraceMode } from "./types";

  let { mode, onChange } = $props<{
    mode: TraceMode;
    onChange: (next: TraceMode) => void;
  }>();
</script>

<div class="inline-flex border-2 border-black rounded-base overflow-hidden shadow-small">
  <button
    type="button"
    onclick={() => onChange("search")}
    class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide transition-colors duration-100 ease-out
      {mode === 'search' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
  >
    <Search class="w-3.5 h-3.5" />
    Search
  </button>
  <button
    type="button"
    onclick={() => onChange("analytics")}
    class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black uppercase tracking-wide border-l-2 border-black transition-colors duration-100 ease-out
      {mode === 'analytics' ? 'bg-primary-800 text-white' : 'bg-surface-50 text-primary-800 hover:bg-primary-100'}"
  >
    <BarChart2 class="w-3.5 h-3.5" />
    Analytics
  </button>
</div>
