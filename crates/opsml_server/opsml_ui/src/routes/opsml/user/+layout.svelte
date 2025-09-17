
<script lang="ts">
    let { children } = $props();
</script>

<div class="grid place-items-center min-h-[calc(100vh-3.5rem)]">
    {@render children()}
</div>