<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import { onMount } from 'svelte';
  import Highlight, { LineNumbers } from "svelte-highlight";
  import python from "svelte-highlight/languages/python";

  let { code, language } = $props<{code: string; language: string}>();
  let openState = $state(false);
  let copied = $state(false);
  let timeoutId: number = 0;


  function modalClose() {
      openState = false;
  }


	function onClickHandler(): void {
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 1000);
	}

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(code);
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
triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2"
contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-xl"
backdropClasses="backdrop-blur-sm"
>
{#snippet trigger()}Use this card{/snippet}
{#snippet content()}
  <div class="flex flex-row pb-3 justify-between items-center">
    <header class="pl-2 text-xl font-bold text-black">Usage</header> 
    <button class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 mr-3 mt-1" onclick={copyToClipboard} disabled={copied}>
      {copied ? 'Copied 👍' : 'Copy'}
    </button>
  </div>
  <article class="pl-2 max-h-[200px] overflow-hidden text-black">Paste the following code into your Python script to load the card</article>
  <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[600px]">
    <Highlight language={python}  
        code={code} 
        let:highlighted>
    </Highlight>
  </div>
  <footer class="flex justify-end gap-4 p-2">
    <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
    <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Confirm</button>
  </footer>
{/snippet}
</Modal>


