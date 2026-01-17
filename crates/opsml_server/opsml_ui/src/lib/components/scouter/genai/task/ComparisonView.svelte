<script lang="ts">
  import { FileJson, AlignLeft } from 'lucide-svelte';
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

  let { expected, actual, label = "Assertion Comparison" } = $props<{
    expected: any;
    actual: any;
    label?: string;
  }>();

  function formatValue(val: any): string {
    if (typeof val === 'object' && val !== null) {
      return JSON.stringify(val, null, 2);
    }
    return String(val);
  }

  const isJson = typeof expected === 'object' || typeof actual === 'object';
</script>

<section class="flex flex-col h-full min-h-0">
  <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
    {#if isJson}
      <FileJson class="text-primary-600 w-5 h-5"/>
    {:else}
      <AlignLeft class="text-primary-600 w-5 h-5"/>
    {/if}
    <header class="pl-2 text-primary-950 text-sm font-bold uppercase tracking-wide">{label}</header>
  </div>

  <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
    <div class="flex flex-col gap-2">
      <span class="text-xs font-bold text-gray-500 uppercase">Expected</span>
      <div class="bg-surface-50 rounded-lg border-2 border-dashed border-gray-400 overflow-hidden h-full">
        <CodeBlock
          code={formatValue(expected)}
          showLineNumbers={false}
          lang="json"
          prePadding="p-3"
          classes="h-full text-xs"
        />
      </div>
    </div>

    <div class="flex flex-col gap-2">
      <span class="text-xs font-bold text-gray-500 uppercase">Actual</span>
      <div class="bg-white rounded-lg border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] overflow-hidden h-full">
        <CodeBlock
          code={formatValue(actual)}
          showLineNumbers={false}
          lang="json"
          prePadding="p-3"
          classes="h-full text-xs"
        />
      </div>
    </div>
  </div>
</section>