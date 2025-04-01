<script lang="ts">
  import { KeySquare } from "lucide-svelte";
  import Dropdown from "$lib/components/utils/Dropdown.svelte";

  let { 
    features
  } = $props<{
    features: string[];
  }>();
  let selectedFeature = $state('choose feature');

</script>



<div class="flex flex-col justify-center p-4 bg-white p-4 md:col-span-2 rounded-lg border-2 border-black shadow min-h-[160px]">
  <div class="flex flex-row flex-wrap gap-2 items-center justify-center">
    <div class="items-center text-xl mr-2 font-bold text-primary-800">Data Profile:</div>
    <div class="flex items-center gap-2 pr-2">
      <div class="self-center" aria-label="Time Interval">
        <KeySquare color="#5948a3" />
      </div>

      <Dropdown 
        bind:selectedValue={selectedFeature}
        bind:values={features}
        width='w-48'
        py="py-2"
      />
    </div>
  </div>
</div>


