<script lang="ts">

  import { Combobox } from "melt/builders";
  import { onMount } from "svelte";
  const options = [  /* ... */  ] as const;
  // @ts-ignore
  type Option = (typeof options)[string];
  let {
    boxId,
    label,
    parentStyle = "mb-4 text-black flex flex-col items-center w-full relative",
    inputHeight = "h-full",
    filteredItems = $bindable([] as string[]),
    availableOptions = [] as string[],
    optionWidth = "w-full",
    defaultSelected = [] as string[],
  } =
    $props<{
      boxId:string,
      label:string,
      parentStyle?:string,
      inputHeight?:string,
      filteredItems:string[],
      availableOptions:string[],
      optionWidth?:string,
      defaultSelected?:string[],
  }>();

  let searchTimeout: ReturnType<typeof setTimeout> | null = null;
  let availableItems: string[] = $state(availableOptions);

  const combobox = new Combobox<string>({
    // @ts-ignore
    multiple: true,
    onValueChange: onChange,
    onInputValueChange: onInputChange
  });

  function onChange() {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      //@ts-ignore
      filteredItems = [...combobox.value] as string[];
    }, 100);
  }

  function onInputChange() {
    // Filter availableItems based on inputValue
    // @ts-ignore
    availableItems = availableOptions.filter(option =>
      option.toLowerCase().includes(combobox.inputValue.toLowerCase())
    );
  }

  // onMount, set initial selected values
  onMount(() => {
    if (defaultSelected.length > 0) {
      // @ts-ignore
      defaultSelected.forEach(item => {
        combobox.select(item);
      });
      filteredItems = [...combobox.value] as string[];
    }
    availableItems = availableOptions;
  });

</script>

<div class={parentStyle}>
  <div class="flex flex-col items-start {optionWidth}">
    <label {...combobox.label} class="text-primary-800 mb-1">{label}</label>
    <input
      {...combobox.input}
      id={boxId}
      class="combobox-input bg-primary-400 text-black border-black border-2 rounded-lg w-full focus:outline-none focus:ring-0 focus:ring-primary-500 {inputHeight}"
      aria-label={`Select options ${label}`}
    />
  </div>
  <!-- Dropdown content -->
  <div
    {...combobox.content}
    class="bg-primary-400 text-black border-black border-2 rounded-lg max-h-60 overflow-auto px-1 py-1 {optionWidth}"
  >
    {#each availableItems as option (option)}
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
  <div class="mt-2 flex flex-wrap gap-1 items-start">
    {#each filteredItems as item}
    <button
      class="badge bg-primary-100 text-primary-800 flex items-center gap-1 px-2 py-1"
      onclick={() => combobox.select(item)}
      aria-label={`Deselect space ${item}`}
      type="button"
    >
      <span>{item}</span>
      <span class="ml-1 text-lg font-bold">&times;</span>
    </button>
    {/each}
  </div>
</div>

