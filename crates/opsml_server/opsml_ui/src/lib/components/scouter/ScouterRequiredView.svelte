<script lang="ts">
  import { AlertCircle, Settings, ArrowLeft } from 'lucide-svelte';
  import { browser } from '$app/environment';
  import logo from '$lib/images/scouter-logo-small.webp';
  
  
  /**
   * Generic component for displaying when a feature requires Scouter to be enabled.
   * Provides clear messaging and navigation options to enable Scouter or return home.
   */
  
  interface Props {
    /**
     * Name of the feature that requires Scouter (e.g., "Model Monitoring", "Drift Detection")
     */
    featureName: string;
    
    /**
     * Optional custom description of what the feature does
     */
    featureDescription?: string;
    
    /**
     * Optional custom icon component from lucide-svelte
     */
    icon?: typeof AlertCircle;

  }
  
  let { 
    featureName, 
    featureDescription, 
    icon: Icon = AlertCircle,
  }: Props = $props();
  
  let timestamp = $state<string>('');
  
  $effect(() => {
    if (browser) {
      timestamp = new Date().toLocaleString();
    }
  });
  
  const defaultDescription = `${featureName} provides advanced monitoring and observability capabilities powered by Scouter. Enable Scouter in your settings to access this feature.`;
</script>

<div class="mx-auto w-full max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
  <div class="mb-4">
    <h1 class="text-2xl font-bold text-primary-800">
      {featureName}
    </h1>
  </div>

  <div class="pb-1 pr-1">
    <div class="bg-white border-2 border-black rounded-lg shadow">
      <div class="p-8 sm:p-12">
        <div class="flex flex-col items-center text-center">
          <!-- Icon -->
          <div class="mb-6 relative">
            <img alt="Scouter logo" class="mx-auto mb-2 w-20" src={logo}>
          </div>

          <!-- Title -->
          <h2 class="text-3xl sm:text-4xl font-bold text-black mb-4 tracking-tight text-error-600">
            Scouter Required
          </h2>

          <!-- Description -->
          <p class="text-lg text-gray-700 mb-8 max-w-2xl">
            This feature requires Scouter to be enabled
          </p>

          <!-- Info Box -->
          <div class="w-full max-w-xl mb-8 bg-primary-50 border-2 border-primary-500 p-6 text-left rounded-lg">
            <h3 class="text-lg font-bold text-black mb-3 flex items-center gap-2">
              <Icon size={20} class="text-primary-500" />
              About {featureName}
            </h3>
            <p class="text-sm text-gray-700 mb-3">
              {featureDescription || defaultDescription}
            </p>
            <p class="text-sm text-gray-600">
              Navigate to Settings to enable Scouter and unlock this feature.
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/opsml/home"
              class="
                inline-flex items-center justify-center gap-2 px-6 py-3
                text-black font-bold text-base
                border-2 border-black rounded-lg shadow
                shadow-hover bg-primary-500
              "
            >
              <ArrowLeft size={20} />
              <span>Return to Home</span>
            </a>
          </div>
        </div>
      </div>

      <!-- Timestamp Footer -->
      {#if browser && timestamp}
        <div class="border-t-2 border-black bg-gray-50 px-8 py-4 rounded-b-lg">
          <p class="text-center text-sm text-gray-600 font-mono">
            Viewed at {timestamp}
          </p>
        </div>
      {/if}
    </div>
  </div>
</div>