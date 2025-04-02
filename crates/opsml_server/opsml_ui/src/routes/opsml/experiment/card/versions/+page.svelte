<script lang="ts">
  
    import CardsSearch from "$lib/components/card/CardsSearch.svelte";
  import type { VersionPageResponse } from "$lib/components/card/types";
    import type { PageProps } from './$types';
  
    let { data }: PageProps = $props();
    let page:  VersionPageResponse  = data.versionPage;
  
  </script>
  
  <div class="mx-auto w-9/12 pt-20 pb-10 m500:pt-14 lg:pt-[100px] flex justify-center px-4">
  
  </div>