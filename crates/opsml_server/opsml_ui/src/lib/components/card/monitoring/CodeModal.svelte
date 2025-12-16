<script lang="ts">
    import { Modal } from '@skeletonlabs/skeleton-svelte';
    import "$lib/styles/hljs.css";
    import CodeBlock from '$lib/components/codeblock/CodeBlock.svelte';

    let { name, code } = $props<{name: string; code: string; }>();
    let openState = $state(false);
    let copied = $state(false);
    let timeoutId: ReturnType<typeof setTimeout>;


    function formatExtraBody(body: any): string {
      return JSON.stringify(body, null, 2);
    }


    function modalClose() {
        openState = false;
    }

    async function copyToClipboard() {
      try {
        await navigator.clipboard.writeText(formatExtraBody(code));
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
  contentBase="card p-4 bg-slate-100 border-2 border-black shadow max-w-screen-lg"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}{name}{/snippet}
  {#snippet content()}
    <div class="flex flex-row pb-3 justify-between items-center">
      <header class="pl-2 text-lg font-bold text-black">Details</header>
      <button class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2 mr-2" onclick={copyToClipboard} disabled={copied}>
        {copied ? 'Copied 👍' : 'Copy'}
      </button>
    </div>
      <div class="flex flex-col gap-2">
        <div>
          <div class="rounded-lg border-2 border-black overflow-y-scroll max-h-[32rem] text-sm">
            <CodeBlock lang="json" code={formatExtraBody(code)} showLineNumbers={false} />
          </div>
        </div>
      </div>
    <footer class="flex justify-end gap-4 p-2">
      <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Close</button>    </footer>
  {/snippet}
  </Modal>


