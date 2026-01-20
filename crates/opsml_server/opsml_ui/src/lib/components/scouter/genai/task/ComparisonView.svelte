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

<section>
  <div class="flex flex-row items-center pb-2 mb-3 border-b-2 border-black">
    {#if isJson}
      <FileJson color="#8059b6"/>
    {:else}
      <AlignLeft color="#8059b6"/>
    {/if}
    <header class="pl-2 text-primary-950 text-sm font-bold">{label}</header>
  </div>

  <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
    <div class="flex flex-col gap-1">
      <span class="text-xs font-bold text-gray-500 uppercase ml-1">Expected</span>
      <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs overflow-hidden h-full">
        <CodeBlock
          code={formatValue(expected)}
          showLineNumbers={false}
          lang="json"
          prePadding="p-1"
          classes="h-full"
        />
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <span class="text-xs font-bold text-gray-500 uppercase ml-1">Actual</span>
      <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs overflow-hidden h-full">
        <CodeBlock
          code={formatValue(actual)}
          showLineNumbers={false}
          lang="json"
          prePadding="p-1"
          classes="h-full"
        />
      </div>
    </div>
  </div>
</section>