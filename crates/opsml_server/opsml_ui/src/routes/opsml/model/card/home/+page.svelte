<script lang="ts">
  // version $props() in +page.svelte

  import HomePage from '$lib/components/model/HomePage.svelte';
  import type { ModelCard } from '$lib/components/card/card_interfaces/modelcard';
  import type { PageProps } from './$types';
  import { onMount } from 'svelte';

  let { data }: PageProps = $props();
  let metadata: ModelCard = data.metadata;

</script>

<HomePage 
  name={metadata.name}
  repository={metadata.repository}
  registry={data.registry}
  version={metadata.version}
  content={data.content}
/>
  


  