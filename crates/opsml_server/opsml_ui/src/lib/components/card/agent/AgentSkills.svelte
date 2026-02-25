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

<div class="rounded-base border-2 border-black shadow bg-surface-50 p-4">
  <div class="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
    <div class="p-1.5 bg-secondary-300 border-2 border-black rounded-base">
      <Wrench class="w-4 h-4 text-black" />
    </div>
    <h3 class="font-black text-primary-950 uppercase tracking-wide text-sm">Skills</h3>
    <span class="badge bg-primary-100 text-primary-800 border border-black text-xs font-bold shadow-small px-2">{skills.length}</span>
  </div>

  {#if skills.length === 0}
    <div class="text-center py-8 text-black/40">
      <BookOpen class="w-10 h-10 mx-auto mb-2 opacity-40" />
      <p class="text-sm font-bold">No skills configured</p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each skills as skill}
        {#if isStandardSkill(skill)}
          <!-- Standard Skill -->
          <div class="p-4 rounded-base border-2 border-black bg-surface-50 shadow-small">
            <div class="flex items-start gap-3 mb-3">
              <span class="mt-0.5 px-2 py-0.5 bg-tertiary-100 text-tertiary-950 border-2 border-black text-xs font-black uppercase tracking-wider shadow-small flex-shrink-0 rounded-base">
                STD
              </span>
              <div class="flex-1">
                <h4 class="text-sm font-black text-primary-950">{skill.name}</h4>
                <p class="text-xs text-black/60 mt-0.5">{skill.description}</p>
              </div>
            </div>

            <div class="flex flex-wrap gap-2">
              {#if skill.license}
                <span class="badge text-black border border-black bg-surface-200 text-xs font-bold shadow-small">
                  {skill.license}
                </span>
              {/if}
              {#if skill.compatibility}
                <span class="badge text-black border border-black bg-surface-200 text-xs font-bold shadow-small">
                  {skill.compatibility}
                </span>
              {/if}
              {#if skill.allowedTools && skill.allowedTools.length > 0}
                <span class="badge text-primary-900 border border-black bg-primary-100 text-xs font-bold shadow-small">
                  {skill.allowedTools.length} tools
                </span>
              {/if}
            </div>

            {#if skill.metadata}
              <details class="mt-3 rounded-base border border-black overflow-hidden">
                <summary class="px-3 py-1.5 text-xs font-bold text-primary-700 cursor-pointer hover:bg-primary-50 transition-colors duration-100">View Metadata</summary>
                <div class="p-2 bg-surface-100 border-t border-black">
                  {#each Object.entries(skill.metadata) as [key, value]}
                    <div class="flex gap-2 text-xs py-1">
                      <span class="font-black text-primary-700">{key}:</span>
                      <span class="text-black/70">{value}</span>
                    </div>
                  {/each}
                </div>
              </details>
            {/if}

            {#if skill.body}
              <details class="mt-3 rounded-base border border-black overflow-hidden">
                <summary class="px-3 py-1.5 text-xs font-bold text-primary-700 cursor-pointer hover:bg-primary-50 transition-colors duration-100">View Skill Body</summary>
                <pre class="p-3 bg-surface-100 text-xs overflow-x-auto whitespace-pre-wrap font-mono border-t border-black">{skill.body}</pre>
              </details>
            {/if}
          </div>

        {:else if isA2ASkill(skill)}
          <!-- A2A Skill -->
          <div class="p-4 rounded-base border-2 border-black bg-surface-50 shadow-small">
            <div class="flex items-start gap-3 mb-3">
              <span class="mt-0.5 px-2 py-0.5 bg-secondary-300 text-black border-2 border-black text-xs font-black uppercase tracking-wider shadow-small flex-shrink-0 rounded-base">
                A2A
              </span>
              <div class="flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <h4 class="text-sm font-black text-black">{skill.name}</h4>
                  <span class="text-xs text-primary-600 font-mono">#{skill.id}</span>
                </div>
                <p class="text-xs text-black/60 mt-0.5">{skill.description}</p>
              </div>
            </div>

            <!-- Tags -->
            {#if skill.tags.length > 0}
              <div class="flex flex-wrap gap-1 mb-3">
                {#each skill.tags as tag}
                  <span class="badge text-black border border-black bg-surface-200 text-xs font-bold">{tag}</span>
                {/each}
              </div>
            {/if}

            <!-- Input/Output Modes -->
            <div class="grid grid-cols-2 gap-3">
              {#if skill.inputModes && skill.inputModes.length > 0}
                <div class="space-y-1">
                  <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Input</span>
                  <div class="flex flex-wrap gap-1">
                    {#each skill.inputModes as mode}
                      <span class="badge text-primary-900 border border-black shadow-small bg-primary-100 text-xs font-bold">{mode}</span>
                    {/each}
                  </div>
                </div>
              {/if}
              {#if skill.outputModes && skill.outputModes.length > 0}
                <div class="space-y-1">
                  <span class="text-xs font-black text-primary-700 uppercase tracking-wide">Output</span>
                  <div class="flex flex-wrap gap-1">
                    {#each skill.outputModes as mode}
                      <span class="badge text-black border border-black shadow-small bg-secondary-100 text-xs font-bold">{mode}</span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>

            <!-- Examples -->
            {#if skill.examples.length > 0}
              <details class="mt-3 rounded-base border border-black overflow-hidden">
                <summary class="px-3 py-1.5 text-xs font-bold text-primary-800 cursor-pointer hover:bg-primary-50 transition-colors duration-100">
                  Examples ({skill.examples.length})
                </summary>
                <div class="p-2 space-y-2 bg-surface-100 border-t border-black">
                  {#each skill.examples as example, idx}
                    <div class="p-2 bg-surface-50 rounded-base border border-black">
                      <span class="text-xs font-black text-primary-800">#{idx + 1}</span>
                      <pre class="text-xs mt-1 text-black/80 whitespace-pre-wrap font-mono">{example}</pre>
                    </div>
                  {/each}
                </div>
              </details>
            {/if}

            <!-- Security Requirements -->
            {#if skill.securityRequirements && skill.securityRequirements.length > 0}
              <div class="mt-3 p-2 warn-color border-2 border-black rounded-base shadow-small">
                <div class="flex items-center gap-2">
                  <Shield class="w-4 h-4 text-black flex-shrink-0" />
                  <span class="text-xs font-black text-black uppercase tracking-wide">
                    Security: {skill.securityRequirements.map(r => r.schemes.join(', ')).join('; ')}
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
