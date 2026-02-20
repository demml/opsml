<script lang="ts">
  import type { SkillFormat, AgentSkill, AgentSkillStandard } from "./types";
  import { BookOpen, Hash, Tags, Shield, FileText, Wrench } from 'lucide-svelte';

  let { skills } = $props<{ skills: SkillFormat[] }>();

  function isStandardSkill(skill: SkillFormat): skill is AgentSkillStandard & { format: "standard" } {
    return skill.format === "standard";
  }

  function isA2ASkill(skill: SkillFormat): skill is AgentSkill & { format: "a2a" } {
    return skill.format === "a2a";
  }
</script>

<div class="rounded-lg border-2 border-black shadow-small bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-2 bg-secondary-100 rounded-lg border-2 border-black">
      <Wrench class="w-5 h-5 text-secondary-900" />
    </div>
    <h3 class="text-lg font-bold text-primary-950">Skills ({skills.length})</h3>
  </div>

  {#if skills.length === 0}
    <div class="text-center py-8 text-gray-500">
      <BookOpen class="w-12 h-12 mx-auto mb-2 opacity-50" />
      <p class="text-sm">No skills configured</p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each skills as skill}
        {#if isStandardSkill(skill)}
          <!-- Standard Skill -->
          <div class="p-4 rounded-lg border-2 border-black bg-white">
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="badge text-tertiary-950 border-tertiary-950 border-1 bg-tertiary-100 text-xs">
                    STANDARD
                  </span>
                  <h4 class="text-sm font-bold text-gray-900">{skill.name}</h4>
                </div>
                <p class="text-xs text-gray-600 mt-1">{skill.description}</p>
              </div>
            </div>

            <div class="flex flex-wrap gap-2 mt-3">
              {#if skill.license}
                <span class="badge text-gray-700 border-gray-400 border-1 bg-surface-100 text-xs">
                  📄 {skill.license}
                </span>
              {/if}
              
              {#if skill.compatibility}
                <span class="badge text-gray-700 border-gray-400 border-1 bg-surface-100 text-xs">
                  🔧 {skill.compatibility}
                </span>
              {/if}

              {#if skill.allowedTools && skill.allowedTools.length > 0}
                <span class="badge text-primary-900 border-primary-800 border-1 bg-primary-100 text-xs">
                  🛠️ {skill.allowedTools.length} tools
                </span>
              {/if}
            </div>

            {#if skill.metadata}
              <details class="mt-3">
                <summary class="text-xs font-bold text-gray-700 cursor-pointer hover:text-primary-800">
                  View Metadata
                </summary>
                <div class="mt-2 p-2 bg-surface-100 rounded border border-gray-300">
                  {#each Object.entries(skill.metadata) as [key, value]}
                    <div class="flex gap-2 text-xs py-1">
                      <span class="font-bold text-gray-700">{key}:</span>
                      <span class="text-gray-600">{value}</span>
                    </div>
                  {/each}
                </div>
              </details>
            {/if}

            {#if skill.body}
              <details class="mt-3">
                <summary class="text-xs font-bold text-gray-700 cursor-pointer hover:text-primary-800">
                  View Skill Body
                </summary>
                <div class="mt-2 p-3 bg-surface-100 rounded border border-gray-300 prose prose-sm max-w-none">
                  <pre class="text-xs overflow-x-auto whitespace-pre-wrap">{skill.body}</pre>
                </div>
              </details>
            {/if}
          </div>

        {:else if isA2ASkill(skill)}
          <!-- A2A Skill -->
          <div class="p-4 rounded-lg border-2 border-black bg-white">
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="badge text-secondary-900 border-secondary-800 border-1 bg-secondary-100 text-xs">
                    A2A
                  </span>
                  <h4 class="text-sm font-bold text-gray-900">{skill.name}</h4>
                  <span class="text-xs text-gray-500 font-mono">#{skill.id}</span>
                </div>
                <p class="text-xs text-gray-600 mt-1">{skill.description}</p>
              </div>
            </div>

            <!-- Tags -->
            {#if skill.tags.length > 0}
              <div class="flex flex-wrap gap-1 mt-3">
                {#each skill.tags as tag}
                  <span class="badge text-gray-700 border-gray-400 border-1 bg-surface-100 text-xs">
                    {tag}
                  </span>
                {/each}
              </div>
            {/if}

            <!-- Input/Output Modes -->
            <div class="grid grid-cols-2 gap-3 mt-3">
              {#if skill.inputModes && skill.inputModes.length > 0}
                <div class="space-y-1">
                  <span class="text-xs font-bold text-gray-600 uppercase">Input Modes</span>
                  <div class="flex flex-wrap gap-1">
                    {#each skill.inputModes as mode}
                      <span class="badge text-primary-900 border-black border-1 shadow-small bg-primary-100 text-xs">
                        {mode}
                      </span>
                    {/each}
                  </div>
                </div>
              {/if}

              {#if skill.outputModes && skill.outputModes.length > 0}
                <div class="space-y-1">
                  <span class="text-xs font-bold text-gray-600 uppercase">Output Modes</span>
                  <div class="flex flex-wrap gap-1">
                    {#each skill.outputModes as mode}
                      <span class="badge text-secondary-900 border-black border-1 shadow-small bg-secondary-100 text-xs">
                        {mode}
                      </span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>

            <!-- Examples -->
            {#if skill.examples.length > 0}
              <details class="mt-3">
                <summary class="text-xs font-bold text-gray-700 cursor-pointer hover:text-primary-800">
                  View Examples ({skill.examples.length})
                </summary>
                <div class="mt-2 space-y-2">
                  {#each skill.examples as example, idx}
                    <div class="p-2 bg-surface-100 rounded border border-gray-300">
                      <span class="text-xs font-bold text-gray-600">Example {idx + 1}:</span>
                      <pre class="text-xs mt-1 text-black whitespace-pre-wrap">{example}</pre>
                    </div>
                  {/each}
                </div>
              </details>
            {/if}

            <!-- Security Requirements -->
            {#if skill.securityRequirements && skill.securityRequirements.length > 0}
              <div class="mt-3 p-2 bg-warning-100 border-2 border-warning-600 rounded-lg">
                <div class="flex items-center gap-2">
                  <Shield class="w-4 h-4 text-warning-800" />
                  <span class="text-xs font-bold text-warning-900">
                    Security Required: {skill.securityRequirements.map(r => r.schemes.join(', ')).join('; ')}
                  </span>
                </div>
              </div>
            {/if}
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>
