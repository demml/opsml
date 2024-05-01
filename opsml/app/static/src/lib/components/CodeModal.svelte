
<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import Highlight, { LineNumbers } from "svelte-highlight";
  	import python from "svelte-highlight/languages/python";
	import { getModalStore } from '@skeletonlabs/skeleton';

	import { clipboard } from '@skeletonlabs/skeleton';

	// Props
	/** Exposes parent props to this component. */
	export let parent: SvelteComponent;
	let code = "hello";

	const modalStore = getModalStore();

	const cButton = 'fixed top-4 right-4 z-50 font-bold shadow-xl';

	export let uid: string;
	export let registry: string;

	let copied = false;

	function onClickHandler(): void {
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 1000);
	}

	const codeBlock: string=`
from opsml import CardRegistries
# load the card
registries = CardRegistries()
${registry}card = registries.${registry}.load_card(uid="${uid}")

# load the model
${registry}card.load_${registry}()
`


</script>

{#if $modalStore[0]}

  <div class="modal block overflow-y-auto bg-surface-100-800-token w-fit h-auto p-4 space-y-4 rounded-container-token shadow-xl">
    <header class="modal-header text-2xl font-bold text-darkpurple">Usage</header> 
    <article class="modal-body max-h-[200px] overflow-hidden">Paste the following code into your Python script to load the card.</article> 
      <Highlight language={python}  
        code={codeBlock} 
        let:highlighted>
      </Highlight>
    <footer class="modal-footer flex justify-end space-x-2">
      <button use:clipboard={codeBlock} class="btn variant-filled" on:click={onClickHandler} disabled={copied}>
        {copied ? 'Copied 👍' : 'Copy'}
      </button>
    </footer>
  </div>

{/if}

