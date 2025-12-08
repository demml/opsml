<script lang="ts">
  import TraceDashboard from "$lib/components/card/trace/TraceDashboard.svelte";

  let { data }: PageProps = $props();
</script>

<TraceDashboard
  space={data.space}
  name={data.name}
  version={data.version}
  trace_page={data.trace_page}
  trace_metrics={data.trace_metrics}
/>
