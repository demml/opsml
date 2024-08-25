<script lang="ts">
    import FileView from "$lib/card/FileView.svelte";
    import { type DataCardMetadata, type Card } from "$lib/scripts/types";
  
  
    
  /** @type {import('./$types').LayoutData} */
    export let data;
    
    let metadata: DataCardMetadata;
    $: metadata = data.metadata;

    let registry: string;
    $: registry = data.registry;

    let card: Card;
    $: card = data.card;
  
    
    </script>
  
    <FileView
      name="Data Splits"
      modifiedAt=""
      viewType="code"
      content={metadata.data_splits}
      suffix="json"
      uri={undefined}
      registry={registry}
      repository={card.repository}
      version={card.version}
      cardName={card.name}
    />