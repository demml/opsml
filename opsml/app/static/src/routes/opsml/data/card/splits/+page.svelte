<script lang="ts">
    import FileView from "$lib/card/FileView.svelte";
    import { type DataCardMetadata } from "$lib/scripts/types";
  
    
  /** @type {import('./$types').LayoutData} */
    export let data;
    
    let metadata: DataCardMetadata;
    $: metadata = data.metadata;
  
    
    </script>
  
    <FileView
      name="Data Splits"
      modifiedAt=""
      viewType="code"
      content={metadata.data_splits}
      suffix="json"
      uri={undefined}
    />