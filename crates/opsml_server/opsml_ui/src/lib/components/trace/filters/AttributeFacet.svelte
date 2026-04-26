<script lang="ts">
  import MultiComboSearchBox from "$lib/components/utils/MultiComboSearchBox.svelte";

  let { items, onChange } = $props<{
    items: string[];
    onChange: (next: string[]) => void;
  }>();
</script>

<MultiComboSearchBox
  boxId="trace-attribute-facet"
  label="key=value"
  filteredItems={items}
  onItemsChange={onChange}
/>
