<script lang="ts">
  import DataProfile from "$lib/components/card/data/DataProfile.svelte";
  import { Accordion } from '@skeletonlabs/skeleton-svelte';
  import { CirclePlus, Plus, Minus } from 'lucide-svelte';
  let { data }: PageProps = $props();

  let dataProfile: DataProfile = $state(data.dataProfile);

  let lorem = `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut`;
  let value = $state(['club']);

</script>

<div class="mx-auto w-11/12 pb-10 flex justify-center pt-4">

  <Accordion {value} onValueChange={(e) => (value = e.value)} multiple>
      {#snippet iconOpen()}<Minus size={20} strokeWidth={3} color="#8059b6"/>{/snippet}
      {#snippet iconClosed()}<Plus size={20} strokeWidth={3} color="#8059b6"/>{/snippet}
    <Accordion.Item 
      value="feature" 
      base="bg-surface-50 rounded-base border-black border-2 shadow"
      controlHover="none"
      >
      <!-- Control -->
   
      {#snippet control()}
        <div class="flex flex-row items-center text-primary-800 text-xl">
          Blah
        </div>
      {/snippet}
      <!-- Panel -->
      {#snippet panel()}
      {lorem}
      {/snippet}
    </Accordion.Item> 
  </Accordion>
</div>