<script lang="ts">
  import Readme from "$lib/card/Readme.svelte"


  /** @type {import('./$types').PageData} */
  export let data;

  let status: string;
  $: status = data.status;

  let tabSet = data.status;

  let registry: string = data.registry;
  let repository: string = data.repository;
  let name: string = data.name;
  let version: string = data.version;
  let content: string;
  $: content = data.content;


</script>

<Readme
  content={content}
  name={name}
  registry={registry}
  repository={repository}
  version={version}
  tabSet={tabSet}
  status={status}
/>


