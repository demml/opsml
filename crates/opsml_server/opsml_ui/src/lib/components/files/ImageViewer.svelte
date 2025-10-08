<script lang="ts">
  interface Props {
    mimeType: string;
    content: string;
  }
  let { mimeType, content }: Props = $props();
</script>


<div class="flex justify-center p-4">
  <img 
    src={`data:${mimeType};base64,${content}`} 
    alt="File preview"
    class="max-w-full h-auto rounded-lg"
  />
</div>