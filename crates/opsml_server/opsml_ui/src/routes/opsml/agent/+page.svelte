<script lang="ts">
  import { MessageSquare, Bot, Puzzle, ExternalLink, BookOpen } from 'lucide-svelte';
  
  interface RegistryCard {
    title: string;
    description: string;
    path: string;
    icon: any;
    color: string;
  }

  const registryCards: RegistryCard[] = [
    {
      title: "Prompts",
      description: "Manage and version your prompts",
      path: "/opsml/agent/prompt",
      icon: MessageSquare,
      color: "gradient-primary"
    },
    {
      title: "Agents",
      description: "Coming soon: Manage agents",
      path: "/opsml/agent/agent",
      icon: Bot,
      color: "gradient-success"
    },
    {
      title: "MCPs",
      description: "Central registration hub for MCP servers",
      path: "/opsml/agent/mcp",
      icon: Puzzle,
      color: "gradient-error"
    }
  ];

  function handleTutorialClick() {
    // Replace with your actual tutorial URL
    window.open("https://github.com/demml/opsml/tree/main/py-opsml/examples/agent", "_blank");
  }
</script>

<section class="pt-16 px-4 pb-10 grid-background">
  <div class="justify-items-start mb-8 w-11/12 mx-auto">
    <h1 class="text-4xl md:text-5xl font-black text-black leading-tight mb-8">
      Get Started with
      <span class="agent-accent inline-block px-3 py-1 md:px-4 md:py-2 bg-primary-500 text-white border-4 border-black shadow-brutal -rotate-2 text-4xl md:text-5xl align-top">Agent</span>
    </h1>
    <p class="text-xl text-gray-600 max-w-3xl mb-8">
      To get started with Agent, check out our tutorials. To explore prompts, MCPs, and agents,
      click on any of the cards below to explore the registries.
    </p>
    <button
      type="button"
      onclick={handleTutorialClick}
      class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 px-4 py-6 gap-2"
    >
      <BookOpen size={20} />
      View Tutorials
      <ExternalLink size={16} />
    </button>
  </div>
</section>
<div class="w-full h-2 bg-black rounded"></div>

<section class="pt-8 px-4 pb-10 alt-grid-background">

  <div class="max-w-6xl mx-auto">
    <h2 class="text-2xl font-bold text-gray-900 mb-8 text-center">
      Explore Agent Registries
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {#each registryCards as card}
        <div class="flex flex-col items-start bg-surface-50 border-primary-800 border-3 shadow-primary rounded-base p-8">

          <h3 class="text-xl font-bold text-gray-900 mb-4">
            {card.title}
          </h3>

          <p class="text-gray-600 text-left leading-relaxed mb-6">
            {card.description}
          </p>

          <a
            href={card.path}
            data-sveltekit-preload-data="hover"
            class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 px-4 py-2 gap-2 w-full"
          >
            Explore Registry
            <ExternalLink size={16} />
          </a>
        </div>
      {/each}
    </div>
  </div>

</section>

<style>
  .grid-background {
    background-color: var(--grid-alt-bg, #f8f8f8);
    background-image:
      linear-gradient(to right, var(--grid-line, #CECBDB) 1px, transparent 1px),
      linear-gradient(to bottom, var(--grid-line, #CECBDB) 1px, transparent 1px);
    background-size: 60px 60px;
    background-attachment: fixed;
  }

  .alt-grid-background {
    background-color: var(--grid-bg, #E3DFF2);
    background-image:
      linear-gradient(to right, var(--grid-line, #CECBDB) 1px, transparent 1px),
      linear-gradient(to bottom, var(--grid-line, #CECBDB) 1px, transparent 1px);
    background-size: 60px 60px;
    background-attachment: fixed;
  }

  :global([data-theme='opsml'].theme-dark) .agent-accent {
    background-color: oklch(35% 0.15 295) !important;
    border-color: oklch(50% 0.18 295 / 0.7) !important;
    color: oklch(85% 0.12 295) !important;
    text-shadow: 0 0 10px oklch(65% 0.20 295 / 0.5);
    box-shadow: 4px 4px 0 oklch(30% 0.12 295 / 0.6);
  }
</style>