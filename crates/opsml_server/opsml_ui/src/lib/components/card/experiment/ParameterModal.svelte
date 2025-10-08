<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import type { Parameter } from '../card_interfaces/experimentcard';
  import type { ParameterValue } from '../card_interfaces/experimentcard';
  import "$lib/styles/hljs.css";


  let { parameters } = $props<{parameters: Parameter[]}>();
  let openState = $state(false);
  let copied = $state(false);

  let timeoutId: number = 0;


  function modalClose() {
      openState = false;
  }
  
  function getParameterValue(paramValue: ParameterValue): string | number {
    if ('Int' in paramValue) return paramValue.Int;
    if ('Float' in paramValue) return paramValue.Float;
    if ('Str' in paramValue) return paramValue.Str;
    return '';
  }

  async function copyToClipboard() {
      try {
        // parameter map
        let parameterMap = parameters.map((param: { name: any; value: ParameterValue; }) => ({
          name: param.name,
          value: getParameterValue(param.value)
        }));
        await navigator.clipboard.writeText(JSON.stringify(parameterMap, null, 2));
        copied = true;
        
        // Reset the copied state after 2 seconds
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          copied = false;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text:', err);
      }
    }


  
  
  </script>
  
 
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-sm"
  contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-lg max-h-[40rem] overflow-auto"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}Parameters{/snippet}
  {#snippet content()}
    <div class="mx-auto rounded-2xl bg-surface-50 p-4 md:px-5 flex flex-col">

      <div class="flex flex-row pb-2 justify-between items-center">
        <header class="text-lg font-bold text-primary-800">Parameters</header> 
        <button class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={copyToClipboard} disabled={copied}>
          {copied ? 'Copied 👍' : 'Copy'}
        </button>
      </div>
      <div class="overflow-auto w-full">
        <table class="text-black border-collapse text-sm bg-white w-full">
          <thead class="sticky top-0 z-10 bg-white" style="box-shadow: 0 2px 0 0 #000;">
            <tr>
              <th class="p-3 font-heading pl-6 text-left text-black">
                <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                  Name
                </span>
              </th>
              <th class="p-3 font-heading">
                <span class='px-2 py-1 rounded-full bg-primary-100 text-primary-800'>
                  Value
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            {#each parameters as parameter, i}
              <tr class={`border-b-2 border-black hover:bg-primary-300 py-2 ${i % 2 === 0 ? 'bg-gray-100' : 'bg-white'}`}>
                <td class="p-3 pl-8">{parameter.name}</td>
                <td class="p-3 text-center">
                  <span class='px-2 py-1 rounded-full border border-black text-xs font-medium bg-primary-100 text-primary-80'>
                    {getParameterValue(parameter.value)}
                  </span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>

    <footer class="flex justify-end gap-4 p-2">
      <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>   
    </footer>
  {/snippet}
  </Modal>
  