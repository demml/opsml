<script lang="ts">
  import type { UserResponse } from "$lib/components/user/types";
  import type { PageProps } from './$types';
  import Pill from "$lib/components/utils/Pill.svelte";
  import { Cog, ShieldEllipsis } from 'lucide-svelte';
  import { userStore } from "$lib/components/user/user.svelte";
  

  let { data }: PageProps = $props();
  let userInfo: UserResponse = $state(data.userInfo);

</script>

<div class="flex pt-24 justify-center w-full px-4">

  <div class="mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-96 md:px-5">

    <div class="flex flex-row items-center pt-2">
      <Cog color="#8059b6"/>
      <header class="pl-2 text-primary-950 text-2xl font-bold">User Profile</header>
    </div>

    <div class="flex flex-col space-y-1 text-base mb-1">
      <Pill key="Username" value={userInfo.username} textSize="text-base"/>
      <Pill key="Email" value={userInfo.email} textSize="text-base"/>
    </div>

    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <ShieldEllipsis color="#8059b6"/>
      <header class="pl-2 text-primary-900 text-lg font-bold">Permissions</header>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each userStore.getPermissions() as perm}
        <Pill key={perm[0]} value={perm[1]} textSize="text-base"/>
      {/each}
    </div>

    <div class="flex flex-row items-center mb-1 border-b-2 border-black">
      <ShieldEllipsis color="#8059b6"/>
      <header class="pl-2 text-primary-900 text-lg font-bold">Group Permissions</header>
    </div>

    <div class="flex flex-wrap gap-1">
      {#each userStore.group_permissions as perm}
        <div class="inline-flex items-center overflow-hidden rounded-lg bg-primary-100 border border-primary-800 text-sm w-fit px-2 text-primary-900">
          {perm}
        </div>
      {/each}
    </div>

  </div>
</div>