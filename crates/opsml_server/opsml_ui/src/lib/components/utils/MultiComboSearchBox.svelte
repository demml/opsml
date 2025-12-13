<script lang="ts">
  import type { ChangeEventHandler, KeyboardEventHandler } from 'svelte/elements';

  let {
    boxId,
    label,
    parentStyle = "mb-4 text-black flex flex-col items-center w-full relative",
    inputHeight = "h-full",
    filteredItems = $bindable([] as string[]),
    optionWidth = "w-full",
    defaultSelected = [] as string[],
    onItemsChange = undefined,
  } =
    $props<{
      boxId: string;
      label: string;
      parentStyle?: string;
      inputHeight?: string;
      filteredItems: string[];
      optionWidth?: string;
      defaultSelected?: string[];
      onItemsChange?: (items: string[]) => void;
  }>();

  // --- Internal State ---
  let currentInputValue = $state('');

  // --- Initialization Effect (Equivalent to onMount) ---
  $effect.pre(() => {
    // Run once on mount to set the initial state from the prop
    if (defaultSelected.length > 0 && filteredItems.length === 0) {
      filteredItems = defaultSelected;
    }
  });

  const handleInputChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    currentInputValue = event.currentTarget.value.trim();
  };

  const handleKeydown: KeyboardEventHandler<HTMLInputElement> = (event) => {
    // 1. Check for 'Enter' key and non-empty input
    if (event.key === 'Enter' && currentInputValue) {
      event.preventDefault();

      const valueToAdd = currentInputValue.trim();

      // 2. Check for existence (case-insensitive check is good practice)
      if (!filteredItems.map((item: string) => item.toLowerCase()).includes(valueToAdd.toLowerCase())) {

        // 3. Update the bound prop directly. This triggers reactivity in the parent.
        filteredItems = [...filteredItems, valueToAdd];
        onItemsChange?.(filteredItems);
      }

      // 4. Clear the input field for the next entry
      currentInputValue = '';
    }
  };

  function deselectItem(itemToDeselect: string) {
    // Update the bound prop by filtering out the deselected item
    filteredItems = filteredItems.filter((item: string) => item !== itemToDeselect);
    onItemsChange?.(filteredItems);
  }

</script>

<div class={parentStyle}>
  <div class="flex flex-col items-start {optionWidth}">
    <label for={boxId} class="text-primary-800 mb-1">{label}</label>
    <input
      id={boxId}
      type="text"
      bind:value={currentInputValue}
      oninput={handleInputChange}
      onkeydown={handleKeydown}
      class="combobox-input bg-primary-400 text-black border-black border-2 rounded-lg w-full focus:outline-none focus:ring-0 focus:ring-primary-500 {inputHeight}"
      aria-label={`Select options ${label}`}
    />
  </div>

  <div class="mt-2 flex flex-wrap gap-2 items-start {optionWidth}">
    {#each filteredItems as item (item)}
      <button
        class="badge bg-primary-100 text-primary-800 flex items-center gap-1 px-2 py-1"
        onclick={() => deselectItem(item)}
        aria-label={`Deselect item ${item}`}
        type="button"
      >
        <span>{item}</span>
        <span class="ml-1 text-lg font-bold leading-none">&times;</span>
      </button>
    {/each}
  </div>
</div>