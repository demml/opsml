<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import { z } from "zod";
  import Warning from '../utils/Warning.svelte';
  import { createInternalApiClient } from '$lib/api/internalClient';
  import { ServerPaths } from '../api/routes';
  import type { CreateSpaceResponse } from './types';

  // Validation schema for space
  const spaceSchema = z.object({
    space: z.string(),
    description: z.string().optional(),
  });

  type ValidationResult<T> = {
  success: boolean;
  data?: T;
  errors?: Record<string, string>;
  };

  type UseSpaceSchema = z.infer<typeof spaceSchema>;

  let spaceErrors = $state<Partial<Record<keyof UseSpaceSchema, string>>>({});


  function validateSpaceSchema(
    space: string,
    description: string
  ): ValidationResult<UseSpaceSchema> {
    let parsed = spaceSchema.safeParse({ space, description });

    if (parsed.success) {
      return {
        success: true,
        data: parsed.data,
      };
    } else {
      let errors = parsed.error.errors.reduce<
        Record<keyof UseSpaceSchema, string>
      >((acc, curr) => {
        const path = curr.path[0] as keyof UseSpaceSchema;
        acc[path] = curr.message;
        return acc;
      }, {} as Record<keyof UseSpaceSchema, string>);
      return {
        success: false,
        errors,
      };
    }
  }

  let openState = $state(false);
  let showError = $state(false);
  let space = $state<string>('');
  let description = $state<string>('');
  let errorMessage: string = $state("Failed to create space");


  function modalClose() {
      openState = false;
  }

  async function createCardSpace() {
    let argsValid = validateSpaceSchema(space, description);

    if (argsValid.success) {

      let resp = await createInternalApiClient(fetch).post(ServerPaths.CREATE_SPACE, {
        space,
        description
      });

      let response = (await resp.json() as CreateSpaceResponse);

      if (!response.created) {
        showError = true;
        return;
      }
      modalClose();
    } else {
      console.error("Space arguments are invalid", argsValid.errors);
      showError = true;
    }
  }

</script>

<Modal
open={openState}
onOpenChange={(e) => (openState = e.open)}
triggerBase="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 text-smd"
contentBase="card p-4 bg-slate-100 border-2 border-black shadow min-w-[400px]"
backdropClasses="backdrop-blur-sm"
>
{#snippet trigger()}Create Space{/snippet}
{#snippet content()}
  <div class="flex flex-row pb-1 justify-between items-center">
    <header class="text-smd font-bold text-primary-800">Create a Space!</header> 
  </div>

  {#if showError}
    <Warning errorMessage={errorMessage}/>
  {/if}

   <div class="mb-8 grid grid-cols-1 gap-3">

    <label class="text-surface-950 text-sm">Space
      <input
          class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
          type="text" 
          placeholder=""
          bind:value={space}
      />
      {#if spaceErrors.space}
          <span class="text-red-500 text-sm">{spaceErrors.space}</span>
      {/if}
    </label>


    <label class="text-surface-950 text-sm">Description
      <textarea
          class="textarea text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800 w-full min-h-[100px] resize-y"
          placeholder="Provide a description for the space"
          bind:value={description}
      ></textarea>
      {#if spaceErrors.description}
          <span class="text-red-500 text-sm">{spaceErrors.description}</span>
      {/if}
    </label>
  </div>

  <footer class="flex justify-center gap-4 p-2">
    <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
    <button type="button" class="btn text-sm bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={createCardSpace}>Create</button>
  </footer>
{/snippet}
</Modal>


