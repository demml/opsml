<script lang="ts">
    let { children } = $props();
    import { page } from '$app/state';
</script>

<div>
  {#key page.params.registry}
    {@render children()}
  {/key}
</div>
