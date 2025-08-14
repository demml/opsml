<script lang="ts">
  import type { RawFile } from "$lib/components/files/types";
  let { figure } = $props<{ figure: RawFile }>();
</script>


<div class="bg-white p-4 border-2 border-black rounded-lg shadow">
  <div class="flex justify-center p-4">
    <img 
      src={`data:${figure.mime_type};base64,${figure.content}`} 
      alt="File preview"
      class="max-w-full h-auto rounded-lg"
    />
  </div>
</div>