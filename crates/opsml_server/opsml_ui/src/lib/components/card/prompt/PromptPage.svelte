<script lang="ts">
  import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
  import CardReadMe from '$lib/components/card/CardReadMe.svelte';
  import NoReadme from '$lib/components/readme/NoReadme.svelte';
  import Metadata from '$lib/components/card/prompt/Metadata.svelte';

  let { data }  = $props();
  let card: PromptCard = data.metadata;

</script>


<div class="mx-auto w-full max-w-8xl px-4 py-6 sm:px-6 lg:px-8">

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-3 lg:gap-8">
    
    <div class="lg:col-span-2">
      {#if data.readme.exists}
        <div class="rounded-base border-black border-3 shadow bg-surface-50 w-full">
          <CardReadMe
            name={card.name}
            space={card.space}
            registryType={data.registryType}
            version={card.version}
            readMe={data.readme}
          />
        </div>
      {:else}
        <div class="rounded-base border-black border-3 shadow bg-primary-100 w-full min-h-[200px] flex items-center justify-center">
          <NoReadme
            name={card.name}
            space={card.space}
            registryType={data.registryType}
            version={card.version}
          />
        </div>
      {/if}
    </div>

      <div class="lg:col-span-1">
        <div class="rounded-base bg-surface-50 border-primary-800 border-3 shadow-primary p-4">
        <Metadata 
          card={card} 
          modelSettings={card.prompt.model_settings} 
        />
      </div>
    </div>
  </div>  
</div>
