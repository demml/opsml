<script lang="ts">

  import { Combobox } from "melt/builders";
  
  const options = [  /* ... */  ] as const;
  // @ts-ignore
  type Option = (typeof options)[string];
  let {
    boxId,  
    defaultValue = $bindable(),
    boxOptions,
    optionWidth = "w-full",
    inputValue = $bindable('')
  } = 
    $props<{
      boxId:String, 
      defaultValue:string, 
      boxOptions:string[],
      optionWidth?:string,
      inputValue?:string
  }>();

  function onChange() {
    defaultValue = combobox.value;
  }

  const combobox = new Combobox<Option>({ onValueChange: onChange });

 
  const filtered = $derived.by(() => {
    if (!combobox.touched) return boxOptions;
    // @ts-ignore
    return boxOptions.filter((o) =>
      o.toLowerCase().includes(combobox.inputValue.trim().toLowerCase()),
    );
  });

 

  function handleClose() {
    // When dropdown closes, move focus to input
    document.getElementById(boxId)?.focus();
  }

  $effect(() => {
    if (!combobox.open) handleClose();
  });

  $effect(() => {
    inputValue = combobox.inputValue;
  });


</script>

<div class="flex flex-col gap-1">

  <div class="relative">
    <input
      {...combobox.input}
      id={boxId}
      class="w-full rounded-lg border-2 border-black bg-primary-400 py-1 px-2 text-black placeholder-black focus:outline-none focus:ring-0 focus:ring-primary-500"
      aria-label="Select time interval"
      value={defaultValue}
    />
    <!-- Trigger button (right side) -->
    <button
      {...combobox.trigger}
      class="absolute right-3 top-1/2 -translate-y-1/2 grid place-items-center rounded-md bg-primary-400 hover:bg-primary-200 active:bg-primary-300"
      tabindex="-1"
    >
      <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  </div>
  <!-- Dropdown content -->
  <div
    {...combobox.content}
    class="bg-primary-400 text-black border-black border-2 rounded-lg max-h-60 overflow-auto px-1 py-1 {optionWidth}"
  >
    {#each filtered as option (option)}
      <div
        {...combobox.getOption(option)} class="px-2 text-left border-2 border-transparent hover:border-black rounded-lg transition-colors text-black cursor-pointer whitespace-nowrap">
          {option}
        {#if combobox.isSelected(option)}
          ✓
        {/if}
      </div>
    {:else}
      <span class="text-black">No results found</span>
    {/each}
  </div>
</div>

