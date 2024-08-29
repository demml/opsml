

<script lang="ts">
    export let title: string;
    export let uids: string[];
    export let type: string;
  
  </script>
  
  
  <div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit h-7 bg-primary-50">
    <div class="border-r border-darkpurple px-2 text-darkpurple bg-primary-50 italic">{title}</div> 
    <div class="flex px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
        <div class="flex flex-col">
            {#each uids as uid}
              <div>
                <a href="/opsml/{type}/card?uid={uid}" class="badge border text-primary-500 bg-surface-100 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 overflow-auto">
                  {uid.slice(0, 7)}
                </a>
              </div>
            {/each}
        </div>
    </div>
  </div>
  
  