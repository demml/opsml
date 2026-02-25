<script lang="ts">
  interface Props {
    mimeType: string;
    content: string;
  }
  let { mimeType, content }: Props = $props();
</script>


<div class="flex justify-center p-6">
  <div class="rounded-base border-2 border-black shadow-small overflow-hidden inline-block">
    <img 
      src={`data:${mimeType};base64,${content}`} 
      alt="File preview"
      class="max-w-full h-auto block"
    />
  </div>
</div>