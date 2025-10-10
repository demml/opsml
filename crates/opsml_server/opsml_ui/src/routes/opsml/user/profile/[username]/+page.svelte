<script lang="ts">
  import type { UserResponse } from "$lib/components/user/types";
  import type { PageProps } from './$types';
  import Pill from "$lib/components/utils/Pill.svelte";
  import { Cog, ShieldEllipsis, Star } from 'lucide-svelte';
  import { userStore } from "$lib/components/user/user.svelte";
  

  let { data }: PageProps = $props();
  let userInfo: UserResponse = $state(data.userInfo);

</script>

<div class="col-span-12 md:col-start-5 md:col-span-4 flex items-center justify-center px-4">

  <div class="rounded-2xl bg-surface-50 border-black border-2 shadow p-4 w-lg md:w-xl lg:w-2xl md:px-5">

    <div class="flex flex-row items-center py-2">
      <Cog color="#8059b6"/>
      <header class="pl-2 text-primary-950 font-bold">User Profile</header>
    </div>

    <div class="flex flex-col gap-2 mb-1">
      <Pill key="Username" value={userInfo.username} textSize="text-sm"/>
      <Pill key="Email" value={userInfo.email} textSize="text-sm"/>
      <div class="flex items-center justify-between">
        <Pill key="Password" value="********" textSize="text-sm"/>
        <a type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" href="/opsml/user/reset">Reset</a>
      </div>
    </div>

    <div class="flex flex-row items-center pt-2 mb-2 border-b-2 border-black">
      <ShieldEllipsis color="#8059b6"/>
      <header class="pl-2 text-primary-900 text-smd font-bold">Permissions</header>
    </div>

    <div class="flex flex-wrap gap-2">
      {#each userStore.getPermissions() as perm}
        <Pill key={perm[0]} value={perm[1]} textSize="text-sm"/>
      {/each}
    </div>

    <div class="flex flex-row items-center pt-2 mb-2 border-b-2 border-black">
      <ShieldEllipsis color="#8059b6"/>
      <header class="pl-2 text-primary-900 text-smd font-bold">Group Permissions</header>
    </div>

    <div class="flex flex-wrap gap-2">
      {#each userStore.group_permissions as perm}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border-2 border-primary-800 text-sm w-fit px-2 text-primary-900">
          {perm}
        </div>
      {/each}
    </div>


    <div class="flex flex-row items-center pt-2 mb-2 border-b-2 border-black">
      <Star fill="#8059b6"/>
      <header class="pl-2 text-primary-900 text-smd font-bold">Spaces</header>
    </div>
    
    {#if userStore.favorite_spaces.length >= 0}
      <div class="flex flex-wrap gap-2">
        {#each userStore.favorite_spaces as space}
          <a type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" href={`/opsml/space/${space}`}>{space}</a>
        {/each}
      </div>
    {/if}

  </div>
</div>