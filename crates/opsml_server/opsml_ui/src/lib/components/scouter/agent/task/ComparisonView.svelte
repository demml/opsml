<script lang="ts">
  import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

  let { expected, actual } = $props<{
    expected: unknown;
    actual: unknown;
  }>();

  const isStacked = $derived(
    (typeof expected === 'object' && expected !== null) ||
    (typeof actual === 'object' && actual !== null) ||
    typeof expected === 'string' ||
    typeof actual === 'string'
  );

  function isObject(val: unknown): val is object {
    return typeof val === 'object' && val !== null;
  }

  function getTypeHint(val: unknown): string {
    if (val === null || val === undefined) return 'null';
    if (Array.isArray(val)) return `array - ${val.length} items`;
    if (typeof val === 'object') return `object - ${Object.keys(val as Record<string, unknown>).length} keys`;
    return typeof val;
  }

  function formatValue(val: unknown): string {
    if (typeof val === 'object' && val !== null) {
      return JSON.stringify(val, null, 2);
    }
    return String(val);
  }
</script>

{#if !isStacked}
  <div class="grid grid-cols-2 gap-3">
    <div class="flex flex-col gap-1.5">
      <div class="flex items-center gap-2">
        <span class="text-xs font-black uppercase tracking-wide text-primary-700">Expected</span>
        <span class="text-xs font-mono text-primary-500">{getTypeHint(expected)}</span>
      </div>
      <div class="bg-surface-50 rounded-base border-2 border-black p-3 shadow-small">
        <span class="text-sm font-mono text-primary-950">{formatValue(expected)}</span>
      </div>
    </div>

    <div class="flex flex-col gap-1.5">
      <div class="flex items-center gap-2">
        <span class="text-xs font-black uppercase tracking-wide text-primary-700">Actual</span>
        <span class="text-xs font-mono text-primary-500">{getTypeHint(actual)}</span>
      </div>
      <div class="bg-surface-50 rounded-base border-2 border-black p-3 shadow-small">
        <span class="text-sm font-mono text-primary-950">{formatValue(actual)}</span>
      </div>
    </div>
  </div>
{:else}
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-1.5">
      <div class="flex items-center gap-2">
        <span class="text-xs font-black uppercase tracking-wide text-primary-700">Expected</span>
        <span class="text-xs font-mono text-primary-500">{getTypeHint(expected)}</span>
      </div>
      {#if isObject(expected)}
        <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs overflow-hidden">
          <CodeBlock
            code={formatValue(expected)}
            showLineNumbers={false}
            lang="json"
            prePadding="p-1"
            classes="h-full"
          />
        </div>
      {:else}
        <div class="bg-surface-50 rounded-base border-2 border-black p-3 shadow-small">
          <span class="text-sm font-mono text-primary-950 whitespace-pre-wrap break-words">{formatValue(expected)}</span>
        </div>
      {/if}
    </div>

    <div class="border-t-2 border-black/10"></div>

    <div class="flex flex-col gap-1.5">
      <div class="flex items-center gap-2">
        <span class="text-xs font-black uppercase tracking-wide text-primary-700">Actual</span>
        <span class="text-xs font-mono text-primary-500">{getTypeHint(actual)}</span>
      </div>
      {#if isObject(actual)}
        <div class="bg-surface-50 rounded-base border-2 border-black p-1 shadow-small text-xs overflow-hidden">
          <CodeBlock
            code={formatValue(actual)}
            showLineNumbers={false}
            lang="json"
            prePadding="p-1"
            classes="h-full"
          />
        </div>
      {:else}
        <div class="bg-surface-50 rounded-base border-2 border-black p-3 shadow-small">
          <span class="text-sm font-mono text-primary-950 whitespace-pre-wrap break-words">{formatValue(actual)}</span>
        </div>
      {/if}
    </div>
  </div>
{/if}
