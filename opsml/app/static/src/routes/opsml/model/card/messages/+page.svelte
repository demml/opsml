<script lang="ts">

    import ChatThread from "$lib/card/chat/ChatThread.svelte";

    /** @type {import('./$types').PageData} */
	export let data;

  let name: string = data.name;

  let registry: string = data.registry;

  let repository: string = data.repository;

  let version: string = data.version;


</script>

<div class="flex flex-wrap justify-center bg-white min-h-screen mb-8">
  <div class="flex flex-col w-full md:w-3/4 pl-2">
      <ChatThread
          registry={registry}
          repository={repository}
          name={name}
          version={version}
      />
  </div>
</div>