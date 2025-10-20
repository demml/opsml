<script lang="ts">
  import { type RegistryType, getRegistryPath} from "$lib/utils";
  import { onMount } from "svelte";
  import { createInternalApiClient } from "$lib/api/internalClient";
  import { type Card } from "../home/types";
  import { ServerPaths } from "$lib/components/api/routes";

  let {
    key,
    uid,
    registryType,
   } = $props<{
      key: string;
      uid: string;
      registryType: RegistryType;
   }>();

    function resolveUrl(): string{
      return `/opsml/${getRegistryPath(registryType)}/${uid}`;
    }

   let cardUrl = $state<string>(resolveUrl());

   onMount(async () => {
     let cards: Card[] = await createInternalApiClient().get(ServerPaths.CARD_FROM_UID, {
       registry_type: registryType,
       uid: uid,
     }).then(res => res.json()).then(data => data.cards ?? []);

     // Get the first card's details
     if (cards.length > 0) {
       let card = cards[0].data;
       cardUrl = `/opsml/${getRegistryPath(registryType)}/card/${card.space}/${card.name}/${card.version}/card`;
     }
   });


</script>

<div class="inline-flex items-stretch overflow-hidden rounded-lg border-2 border-primary-700 w-fit shadow-primary-small shadow-hover-small h-7 text-sm">
  <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic flex items-center justify-center">{key}</div> 
    <div class="px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950 flex items-center justify-center">
      <a 
        href={cardUrl}
        class="text-primary-900"
        data-sveltekit-preload-data="hover"
        >
        Link
      </a>
    </div>
</div>