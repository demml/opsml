<script lang="ts">
  import FileView from "$lib/card/FileView.svelte";
  import { type ViewContent, type FileInfo } from "$lib/scripts/types";
  import { calculateTimeBetween } from "$lib/scripts/utils";


  
  /** @type {import('./$types').PageData} */
    export let data;
    
    let fileInfo: FileInfo;
    $: fileInfo = data.viewData.file_info;

    let content: ViewContent;
    $: content = data.viewData.content;

    let registry: string;
    $: registry = data.registry;
    
    let repository: string;
    $: repository = data.repository;

    let version: string;
    $: version = data.version;

    let cardName: string;
    $: cardName = data.cardName;

    let displayPath: string[];
    $: displayPath = data.displayPath;

  
  
  </script>


<FileView
  name={fileInfo.name}
  modifiedAt={calculateTimeBetween(fileInfo.mtime)}
  viewType={content.view_type}
  content={content.content}
  uri={fileInfo.uri}
  suffix={fileInfo.suffix.replace('.', '')}
  registry={registry}
  repository={repository}
  version={version}
  cardName={cardName}
  displayPath={displayPath}

/>