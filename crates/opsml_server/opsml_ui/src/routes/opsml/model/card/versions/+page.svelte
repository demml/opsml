<script lang="ts">
  import type { PageProps } from './$types';
  import VersionNewPage from "$lib/components/card/VersionNewPage.svelte";

  let { data }: PageProps = $props();
 

  </script>

  <VersionNewPage
    metadata={data.metadata}
    registry={data.registry}
    versionPage={data.versionPage}
    cardRegistryStats={data.versionStats}
  />
