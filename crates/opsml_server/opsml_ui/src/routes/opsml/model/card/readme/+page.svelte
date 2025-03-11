<script lang="ts">
   import type { PageProps } from './$types';
   import ReadMe from '$lib/components/readme/Readme.svelte';


  let { data }: PageProps = $props();


</script>

<ReadMe
  name={data.name}
  repository={data.repository}
  registry={data.registry}
  content={data.content}
/>
