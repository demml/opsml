<script lang="ts">
  import { Modal } from '@skeletonlabs/skeleton-svelte';
  import type { CustomMetricAlertConfig, CustomMetricDriftConfig } from './custom';
  import { z } from 'zod';

  function stringToBoolean(str: string): boolean {
      return str
          .toLowerCase() === 'true';
  }

  const configSchema = z.object({
    schedule: z.string().default('0 0 0 * * *'),
    sample: z.coerce.boolean().default(true),
    sample_size: z.coerce.number().default(25),
  });

  type ConfigSchema = z.infer<typeof configSchema>;

  let { 
    config = $bindable(),
    alertConfig = $bindable(),
  } = $props<{
    config: CustomMetricDriftConfig
    alertConfig: CustomMetricAlertConfig
  }>();
  
    let openState = $state(false);
    let errors = $state<Partial<Record<keyof ConfigSchema, string>>>({});
 
    let schedule = $state(alertConfig.schedule);
    let sample = $state(config.sample);
    let sampleSize = $state(config.sample_size);
  
    function modalClose() {
        openState = false;
    }
  
    function validateForm(): boolean {

    try {
      configSchema.parse({
        schedule,
        sample,
        sample_size: Number(sampleSize)
      });

      errors = {};
 

      config.sample = stringToBoolean(sample);
      config.sample_size = Number(sampleSize);
      alertConfig.schedule = schedule;
      return true;

    } catch (error) {

      if (error instanceof z.ZodError) {
        errors = error.errors.reduce((acc, curr) => {
          const path = curr.path[0] as keyof ConfigSchema;
          acc[path] = curr.message;
          return acc;
        }, {} as Record<keyof ConfigSchema, string>);
      }
      return false;
    }
  }

  function updateConfig(event: Event) {
    event.preventDefault();


    
    if (!validateForm()) {
      return;
    }

    const formData = {
      schedule,
      sample,
      sample_size: Number(sampleSize)
    };

    console.log('Valid config:', formData);
    // TODO: Handle form submission
    modalClose();
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
    
    <form class="mx-auto rounded-2xl bg-surface-50 p-4 md:w-96 md:px-5" onsubmit={updateConfig}>
      <p class="mb-6 text-left text-surface-950">Update the following config elements</p>

      <div class="mb-8 grid grid-cols-1 gap-3">
        <label class="text-surface-950">Schedule
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="text" 
            placeholder={schedule}
            bind:value={schedule}
          />

          {#if errors.schedule}
            <span class="text-red-500 text-sm">{errors.schedule}</span>
          {/if}
        </label>
  
        <label class="text-surface-950">Sample
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="text" 
            placeholder={sample}
            bind:value={sample}
          />
          {#if errors.sample}
            <span class="text-red-500 text-sm">{errors.sample}</span>
          {/if}
        </label>

        <label class="text-surface-950">Sample Size
          <input
            class="input text-sm rounded-base bg-surface-50 text-black disabled:opacity-50 placeholder-surface-800 placeholder-text-sm focus-visible:ring-2 focus-visible:ring-primary-800"
            type="text" 
            placeholder={sampleSize}
            bind:value={sampleSize}
          />
          {#if errors.sample_size}
            <span class="text-red-500 text-sm">{errors.sample_size}</span>
          {/if}
        </label>
      </div>

      <footer class="flex justify-end gap-4 p-2">
        <button type="button" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2" onclick={modalClose}>Cancel</button>
        <button type="submit" class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2">Submit</button>
      </footer>

    </form>
  {/snippet}
  </Modal>
  
  
  