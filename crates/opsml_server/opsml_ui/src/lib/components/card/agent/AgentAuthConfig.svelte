<script lang="ts">
  import { X, Key, Lock, AlertCircle } from 'lucide-svelte';
  import type { SecurityScheme } from './types';

  let {
    securitySchemes,
    authConfig,
    onClose,
    onSave,
  } = $props<{
    securitySchemes: Record<string, SecurityScheme>;
    authConfig: Record<string, string>;
    onClose: () => void;
    onSave: (config: Record<string, string>) => void;
  }>();

  let localConfig = $state<Record<string, string>>({ ...authConfig });

  function handleSave() {
    onSave(localConfig);
  }

  function getSchemeType(scheme: SecurityScheme): string {
    if ('location' in scheme && 'name' in scheme) return 'apiKey';
    if ('scheme' in scheme) {
      if (scheme.scheme === 'bearer') return 'bearer';
      if (scheme.scheme === 'basic') return 'basic';
      return 'http';
    }
    if ('flows' in scheme) return 'oauth2';
    if ('openIdConnectUrl' in scheme) return 'openIdConnect';
    return 'unknown';
  }

  function getSchemeDescription(scheme: SecurityScheme): string {
    if ('description' in scheme && scheme.description) {
      return scheme.description;
    }

    const type = getSchemeType(scheme);
    switch (type) {
      case 'apiKey':
        return 'API Key Authentication';
      case 'bearer':
        return 'Bearer Token Authentication';
      case 'basic':
        return 'Basic Authentication (username:password)';
      case 'oauth2':
        return 'OAuth 2.0 Authentication';
      case 'openIdConnect':
        return 'OpenID Connect Authentication';
      default:
        return 'Authentication Required';
    }
  }

  function getPlaceholder(schemeName: string, scheme: SecurityScheme): string {
    const type = getSchemeType(scheme);
    switch (type) {
      case 'apiKey':
        return 'Enter your API key';
      case 'bearer':
        return 'Enter your bearer token';
      case 'basic':
        return 'Enter username:password';
      case 'oauth2':
        return 'Enter access token';
      case 'openIdConnect':
        return 'Enter ID token';
      default:
        return 'Enter authentication value';
    }
  }
</script>

<!-- Overlay -->
<div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
  <!-- Modal -->
  <div class="bg-surface-50 rounded-lg border-2 border-black shadow-primary max-w-2xl w-full max-h-[90vh] overflow-y-auto">
    
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b-2 border-black bg-gradient-primary">
      <div class="flex items-center gap-2">
        <div class="p-2 bg-white rounded-lg border-2 border-black shadow-small">
          <Lock class="w-5 h-5 text-primary-800" />
        </div>
        <div>
          <h3 class="text-lg text-primary-800 font-bold">Authentication Configuration</h3>
          <p class="text-xs text-primary-800">Configure authentication for agent access</p>
        </div>
      </div>

      <button
        onclick={onClose}
        class="p-2 bg-white text-gray-700 hover:bg-gray-100 rounded-lg border-2 border-black shadow-small transition-all"
        aria-label="Close"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- Info Notice -->
    <div class="p-4 border-b-2 border-black bg-tertiary-100">
      <div class="flex items-start gap-2">
        <AlertCircle class="w-5 h-5 text-tertiary-900 flex-shrink-0 mt-0.5" />
        <div>
          <p class="text-sm font-bold text-tertiary-950">Security Information</p>
          <p class="text-xs text-tertiary-900 mt-1">
            Your authentication credentials are stored locally in your browser and are never sent to our servers.
            They are only used to communicate directly with the agent's API endpoints.
          </p>
        </div>
      </div>
    </div>

    <!-- Security Schemes -->
    <div class="p-4 space-y-4">
      {#if Object.keys(securitySchemes).length === 0}
        <div class="text-center py-8">
          <Key class="w-12 h-12 mx-auto mb-3 text-gray-400" />
          <p class="text-sm text-gray-600">No authentication required for this agent</p>
        </div>
      {:else}
        {#each Object.keys(securitySchemes) as schemeName}
          {@const scheme = securitySchemes[schemeName]}
          <div class="p-4 bg-white rounded-lg border-2 border-black shadow-small">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0 mt-1">
                <Key class="w-5 h-5 text-primary-800" />
              </div>

              <div class="flex-1 min-w-0">
                <!-- Scheme Name & Description -->
                <div class="mb-3">
                  <h4 class="text-sm font-bold text-gray-900">{schemeName}</h4>
                  <p class="text-xs text-gray-600 mt-1">{getSchemeDescription(scheme)}</p>
                </div>

                <!-- Input Field -->
                <div>
                  <label for={`auth-${schemeName}`} class="text-xs font-bold text-gray-700 mb-1 block">
                    {#if getSchemeType(scheme) === 'apiKey' && 'name' in scheme}
                      {scheme.name}:
                    {:else}
                      Credential:
                    {/if}
                  </label>
                  <input
                    id={`auth-${schemeName}`}
                    type="password"
                    bind:value={localConfig[schemeName]}
                    placeholder={getPlaceholder(schemeName, scheme)}
                    class="w-full px-3 py-2 border-2 border-black rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                  />
                </div>

                <!-- Additional Info for API Key -->
                {#if getSchemeType(scheme) === 'apiKey' && 'location' in scheme}
                  <p class="text-xs text-gray-500 mt-1">
                    Location: <span class="font-bold">{scheme.location}</span>
                  </p>
                {/if}

                <!-- OAuth2 Flows Info -->
                {#if getSchemeType(scheme) === 'oauth2' && 'flows' in scheme}
                  <div class="mt-2 p-2 bg-surface-100 rounded border border-gray-300">
                    <p class="text-xs font-bold text-gray-700">Available OAuth2 Flows:</p>
                    <ul class="text-xs text-gray-600 mt-1 space-y-0.5 list-disc list-inside">
                      {#if scheme.flows.authorizationCode}
                        <li>Authorization Code</li>
                      {/if}
                      {#if scheme.flows.clientCredentials}
                        <li>Client Credentials</li>
                      {/if}
                      {#if scheme.flows.deviceCode}
                        <li>Device Code</li>
                      {/if}
                      {#if scheme.flows.implicit}
                        <li>Implicit Flow</li>
                      {/if}
                      {#if scheme.flows.password}
                        <li>Password Flow</li>
                      {/if}
                    </ul>
                    <p class="text-xs text-gray-500 mt-1 italic">
                      Enter the access token you've obtained through one of these flows
                    </p>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      {/if}
    </div>

    <!-- Actions -->
    <div class="p-4 border-t-2 border-black bg-surface-100 flex justify-end gap-2">
      <button
        onclick={onClose}
        class="px-4 py-2 bg-white text-gray-700 font-bold rounded-lg border-2 border-black shadow-small hover:shadow-hover transition-all"
      >
        Cancel
      </button>
      <button
        onclick={handleSave}
        class="px-4 py-2 bg-primary-500 text-white font-bold rounded-lg border-2 border-black shadow-small hover:shadow-hover transition-all"
      >
        Save Configuration
      </button>
    </div>
  </div>
</div>
