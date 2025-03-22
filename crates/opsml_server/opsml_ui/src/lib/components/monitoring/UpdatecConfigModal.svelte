<script lang="ts">
    import { Modal } from '@skeletonlabs/skeleton-svelte';
  
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
  
  
  </script>
  
  <Modal
  open={openState}
  onOpenChange={(e) => (openState = e.open)}
  triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2"
  contentBase="card p-2 bg-surface-50 border-2 border-black shadow max-w-screen-md"
  backdropClasses="backdrop-blur-sm"
  >
  {#snippet trigger()}Update{/snippet}
  {#snippet content()}
    <div class="flex flex-row justify-between">
      <header class="pl-2 text-xl font-bold text-primary-800">Update</header> 
    </div>
    <article class="pl-2 max-h-[200px] overflow-hidden text-black">Update the following config elements</article>
    <footer class="flex justify-end gap-4 p-2">
      <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
      <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Submit</button>
    </footer>
  {/snippet}
  </Modal>
  
  
  