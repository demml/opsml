
<script lang="ts">
    let { children } = $props();
</script>

<div class="min-h-screen bg-gradient-to-b from-surface-300 via-primary-100 via-70% to-primary-100">
    {@render children()}
</div>