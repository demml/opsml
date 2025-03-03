<script lang="ts">
    import js from "jquery";
    export let name:string;
    export let searchType:string;
    export let active:string;


</script>

{#if active === ''}
    <a class='{searchType}-tag' on:click href="?{searchType}={name}">
        <span class="badge variant-ghost-secondary text-secondary-800 hover:bg-secondary-300" class:active={name === active}>{name}</span>
    </a>
{:else}
    {#if name === active}
        <a class='{searchType}-tag' on:click href="?{searchType}={name}">
            <span class="badge variant-ghost-secondary text-secondary-800 hover:bg-secondary-300" class:active={name === active}>{name}</span>
        </a>
    {:else}
        <a class='{searchType}-tag' on:click href="?{searchType}={name}">
            <span class="badge bg-slate-200 text-slate-800 hover:bg-slate-300" class:active={name === active}>{name}</span>
        </a>
    {/if}
   
{/if}





