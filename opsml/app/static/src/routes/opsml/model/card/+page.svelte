<script lang="ts">

  import { type ModelMetadata , type Card } from "$lib/scripts/types";
  import icon from '$lib/images/opsml-green.ico'
  import atomOneLight from "svelte-highlight/styles/atom-one-light";
  import CardHomepage from "$lib/card/CardHomepage.svelte";
  import Metadata from "$lib/card/model/Metadata.svelte";

	/** @type {import('./$types').LayoutData} */
	export let data;

  let hasReadme: boolean;
  $: hasReadme = data.hasReadme;

  let readme: string;
  $: readme = data.readme;

  let metadata: ModelMetadata;
  $: metadata = data.metadata;

  let card: Card;
  $: card = data.card;

  let uid: string;
  $: uid = card.uid;

  let registry: string;
  $: registry = data.registry

  
</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>

<div class="flex flex-wrap bg-white min-h-screen mb-8">
  <CardHomepage
    hasReadme={hasReadme}
    name={metadata.model_name}
    repository={metadata.model_repository}
    version={metadata.model_version}
    registry={registry}
    icon={icon}
    readme={readme}
  />
  <div class="flex flex-col w-full md:w-1/3">
    <div class="p-4">
      <Metadata 
        metadata={metadata} 
        card={card} 
      />
    </div>
  </div>
</div>
        

       

  