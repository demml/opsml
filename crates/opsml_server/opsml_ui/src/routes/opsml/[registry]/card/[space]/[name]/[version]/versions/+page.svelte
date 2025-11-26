<script lang="ts">
  import type { PageProps } from './$types';
  import VersionPage from "$lib/components/card/VersionPage.svelte";

  let { data }: PageProps = $props();
 

  </script>

  <VersionPage
    registry={data.registryType}
    versionPage={data.versionPage}
    cardRegistryStats={data.versionStats}
  />
