<script lang="ts">
  import Card from '$lib/components/card/Card.svelte';
  import type { RecentCards } from '$lib/components/home/utils';
  import type { SpaceRecord} from '$lib/components/space/types';
  import { BrainCircuit, Table, NotebookText, FlaskConical } from 'lucide-svelte';
  import type { PageProps } from './$types';
  import { updateUser } from '$lib/components/user/utils';
  import { userStore } from '$lib/components/user/user.svelte';

  let { data }: PageProps = $props();
  let spaceRecord: SpaceRecord= data.spaceRecord;
  let cards: RecentCards = data.recentCards;
  let badgeColor = "#40328b";
  let iconColor = "#40328b"; // Default icon color, can be customized

  async function favoriteSpace() {
    let userFavoriteSpaces = userStore.favorite_spaces;
    userFavoriteSpaces.push(spaceRecord.space);

    let updatedUser = await updateUser({ favorite_spaces: userFavoriteSpaces });
    userStore.setFavoriteSpaces(updatedUser.favorite_spaces);
  }

  async function unfavoriteSpace() {
    let userFavoriteSpaces = userStore.favorite_spaces;
    userFavoriteSpaces = userFavoriteSpaces.filter(space => space !== spaceRecord.space);

    let updatedUser = await updateUser({ favorite_spaces: userFavoriteSpaces });
    userStore.setFavoriteSpaces(updatedUser.favorite_spaces);
  }


</script>

<div class="flex-none pt-20 border-b-2 border-black bg-surface-100 pb-2">
  <div class="flex justify-center items-center w-11/12 mx-auto gap-4">
    <h1 class="text-lg">
      <div class="font-bold text-primary-800">{spaceRecord.space}</div>
    </h1>
    {#if userStore.favorite_spaces.includes(spaceRecord.space)}
      <button class="btn text-sm bg-primary-500 rounded-lg justify-self-center text-black mb-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border reverse-shadow-hover" 
        onclick={unfavoriteSpace}>Unfavorite
      </button>
    {:else}
      <button class="btn text-sm bg-surface-50 rounded-lg justify-self-center text-black mb-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow shadow-hover" 
        onclick={favoriteSpace}>Favorite
      </button>
    {/if}
    
  </div>
</div>

{#await cards}
  <p>Loading...</p>
{:then cards}
  <!-- Cards loaded successfully -->
<div class="flex-1 mx-auto w-9/12 justify-center px-4 pb-10 pt-10">

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 w-full">

      <div class="col-span-1 lg:col-span-4 flex flex-col h-auto gap-y-4">

        <div class="rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 pb-4 px-4">
          <div class="flex flex-row items-center gap-2 py-4">
            <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
              <BrainCircuit color={iconColor} />
            </div>
            <a class="font-bold text-primary-800 text-xl" href="/opsml/model/card/{spaceRecord.space}">Models</a>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-4">
            
              {#each cards.modelcards as card}
              <div class="flex justify-center w-full">
                <Card 
                  iconColor={iconColor} 
                  badgeColor={badgeColor}
                  card={card}
                />
                </div>
              {/each}
            
          </div>
        </div>

        <div class="rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 pb-4 px-4">
          <div class="flex flex-row items-center gap-2 py-4">
            <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
              <Table color={iconColor} />
            </div>
            <a class="font-bold text-primary-800 text-xl" href="/opsml/data/card/{spaceRecord.space}">Data</a>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-4">

              {#each cards.datacards as card}
              <div class="flex justify-center w-full">
                <Card 
                  iconColor={iconColor} 
                  badgeColor={badgeColor}
                  card={card}
                />
                </div>
              {/each}
            
          </div>
        </div>

        <div class="rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 pb-4 px-4">
          <div class="flex flex-row items-center gap-2 py-4">
            <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
              <NotebookText color={iconColor} />
            </div>
            <a class="font-bold text-primary-800 text-xl" href="/opsml/prompt/card/{spaceRecord.space}">Prompts</a>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-4">

              {#each cards.promptcards as card}
              <div class="flex justify-center w-full">
                <Card 
                  iconColor={iconColor} 
                  badgeColor={badgeColor}
                  card={card}
                />
                </div>
              {/each}
            
          </div>
        </div>


        <div class="rounded-base border-primary-500 border-2 shadow-primary bg-surface-50 pb-4 px-4">
          <div class="flex flex-row items-center gap-2 py-4">
            <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
              <FlaskConical color={iconColor} />
            </div>
            <a class="font-bold text-primary-800 text-xl" href="/opsml/experiment/card/{spaceRecord.space}">Experiments</a>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-4">

              {#each cards.experimentcards as card}
              <div class="flex justify-center w-full">
                <Card 
                  iconColor={iconColor} 
                  badgeColor={badgeColor}
                  card={card}
                />
                </div>
              {/each}
            
          </div>
        </div>
      </div>

    </div>

   

</div>
{/await}