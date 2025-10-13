<script lang="ts">

  import { Combobox } from "melt/builders";
  
  const options = [  /* ... */  ] as const;
  // @ts-ignore
  type Option = (typeof options)[string];
  let {boxId,  box, inputPlaceholder, boxOptions } = $props<{boxId:String, box:Combobox<Option>, inputPlaceholder:string, boxOptions:string[] }>();


  const filtered = $derived.by(() => {
    if (!box.touched) return boxOptions;
    return boxOptions.filter((o) =>
      o.toLowerCase().includes(box.inputValue.trim().toLowerCase()),
    );
  });

  function handleClose() {
    // When dropdown closes, move focus to input
    document.getElementById(boxId)?.focus();
  }

  $effect(() => {
    if (!box.open) handleClose();
  });

</script>

<div class="flex flex-col gap-1">

  <div class="relative">

    <input
      {...box.input}
      id={boxId}
      class="w-full rounded-lg border-2 border-black bg-primary-500 py-1 px-2 text-black placeholder-black focus:outline-none focus:ring-2 focus:ring-primary-500"
      placeholder={inputPlaceholder}
      aria-label="Select time interval"
    />
    <!-- Trigger button (right side) -->
    <button
      {...box.trigger}
      class="absolute right-3 top-1/2 -translate-y-1/2 grid place-items-center rounded-md bg-primary-500 hover:bg-primary-200 active:bg-primary-300 border-2 border-black"
      tabindex="-1"
    >
      <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  </div>
  <!-- Dropdown content -->
  <div
    {...box.content}
    class="bg-primary-500 text-black border-black border-2 rounded-lg max-h-60 overflow-auto px-1 py-1 w-full"
  >
    {#each filtered as option (option)}
      <div
        {...box.getOption(option)} class="px-2 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black cursor-pointer whitespace-nowrap">
          {option}
        {#if box.isSelected(option)}
          ✓
        {/if}
      </div>
    {:else}
      <span class="text-black">No results found</span>
    {/each}
  </div>
</div>

