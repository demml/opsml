<script lang="ts">
  import {
  type Files,
} from "$lib/scripts/types";

  /** @type {import('./$types').PageData} */
	export let data;

  let tabSet: string = "files";

  let fileInfo: Files;
  $: fileInfo = data.files;

  let modifiedAt: string;
  $: modifiedAt = data.modifiedAt;

  let name: string;
  $: name = data.name;


</script>

<div class="flex flex-wrap">
  <div class="w-full md-full px-4 pt-8 md:px-20">
    <div class="bg-gradient-to-b from-primary-50 to-white flex rounded-t-lg border border-gray px-3 py-2">
      <div class="flex flex-row justify-between gap-1 items-center">
        <div class="text-primary-500 font-semibold">Files for {name}</div>
        <div class="text-gray-500"> {modifiedAt}</div>
      </div>
    </div>
  </div>
</div>
