<script lang="ts">

    import { type ModelMetadata , type Card, type DataCardMetadata } from "$lib/scripts/types";
    import Fa from 'svelte-fa'
    import { faTag, faSquareCheck, faFileContract, faCircleInfo, faCheck } from '@fortawesome/free-solid-svg-icons'
    import icon from '$lib/images/opsml-green.ico'
    import { goto } from '$app/navigation';
    import atomOneLight from "svelte-highlight/styles/atom-one-light";
    import Markdown from "$lib/card/Markdown.svelte";
    import FileView from "$lib/card/FileView.svelte";
    import CardHomepage from "$lib/card/CardHomepage.svelte";
    import Metadata from "$lib/card/data/Metadata.svelte";

  
      /** @type {import('./$types').LayoutData} */
      export let data;
  
    let hasReadme: boolean;
    $: hasReadme = data.hasReadme;
  
    let readme: string;
    $: readme = data.readme;
  
    let card: Card;
    $: card = data.card;

    let metadata: DataCardMetadata;
    $: metadata = data.metadata;

    let registry: string;
    $: registry = data.registry
  

</script>

<svelte:head>
  {@html atomOneLight}
</svelte:head>

<div class="flex flex-wrap bg-white min-h-screen">
  <CardHomepage
    hasReadme={hasReadme}
    name={metadata.name}
    repository={metadata.repository}
    version={metadata.version}
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

