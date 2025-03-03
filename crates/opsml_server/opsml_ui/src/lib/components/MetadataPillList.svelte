

<script lang="ts">
    export let title: string;
    export let uids: string[];
    export let type: string;
  
  </script>
  
  

  <div class="my-1 flex flex-row rounded-lg border border-darkpurple text-sm w-fit">
    <div class="px-2 rounded-l-lg text-darkpurple bg-primary-50 italic">{title}</div> 
    {#each uids as uid, index}
      {#if index !== uids.length - 1}
        <a href="/opsml/{type}/card/home?uid={uid}" class="px-2 border-l border-darkpurple text-darkpurple bg-surface-50 hover:bg-surface-200">{uid.slice(0, 7)}</a> 
      {:else}
        <a href="/opsml/{type}/card/home?uid={uid}" class="px-2 border-l border-darkpurple rounded-r-lg text-darkpurple bg-surface-50 hover:bg-surface-200">{uid.slice(0, 7)}</a> 
      {/if}
    {/each}
  </div>
  
