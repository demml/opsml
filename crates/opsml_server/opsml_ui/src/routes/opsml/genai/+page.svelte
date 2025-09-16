<script lang="ts">
  import { goto } from "$app/navigation";
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
      description: "Manage and version your AI prompts. Create, test, and deploy prompt templates for consistent AI interactions.",
      path: "/opsml/genai/prompt",
      icon: MessageSquare,
      color: "gradient-primary"
    },
    {
      title: "Agents", 
      description: "Build and deploy AI agents. Configure autonomous AI systems that can perform complex tasks and workflows.",
      path: "/opsml/genai/agent",
      icon: Bot,
      color: "gradient-success"
    },
    {
      title: "MCPs",
      description: "Model Context Protocols for enhanced AI capabilities. Connect your models with external tools and data sources.",
      path: "/opsml/genai/mcp", 
      icon: Puzzle,
      color: "gradient-error"
    }
  ];

  function handleCardClick(path: string) {
    goto(path);
  }

  function handleTutorialClick() {
    // Replace with your actual tutorial URL
    window.open("https://github.com/demml/opsml/tree/main/py-opsml/examples/llm", "_blank");
  }
</script>

<div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">

  <div class="text-center mb-16">
    <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl mb-6 neo-glow grain">
      <MessageSquare size={32} class="text-white" />
    </div>
    
    <h1 class="text-4xl font-bold text-gray-900 mb-4">
      Get started with Generative AI
    </h1>
    
    <p class="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
      To get started with GenAI, check out our tutorials. To explore prompts, MCPs, and agents, 
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

  <div class="max-w-6xl mx-auto">
    <h2 class="text-2xl font-bold text-gray-900 mb-8 text-center">
      Explore GenAI Registries
    </h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {#each registryCards as card}
        {@const IconComponent = card.icon}
        <div class="flex flex-col items-start bg-surface-50 border-primary-800 border-3 shadow-primary rounded-2xl p-8">

          <div class="flex items-center justify-center self-center w-12 h-12 bg-gradient-to-br {card.color} rounded-xl mb-6 neo-glow grain">
            <IconComponent size={24} class="text-white" />
          </div>
          
          <h3 class="text-xl font-bold text-gray-900 mb-4">
            {card.title}
          </h3>
          
          <p class="text-gray-600 text-left leading-relaxed mb-6">
            {card.description}
          </p>
          
          <button
            type="button"
            onclick={() => handleCardClick(card.path)}
            class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 px-4 py-2 gap-2 w-full"
          >
            Explore Registry
            <ExternalLink size={16} />
          </button>
        </div>
      {/each}
    </div>
  </div>

  <div class="max-w-4xl mx-auto mt-14 text-center">
    <div class="rounded-2xl p-8 bg-surface-50 border-black border-3 shadow">
      <h3 class="text-xl font-bold text-gray-900 mb-4">
        Need Help Getting Started?
      </h3>
      <p class="text-gray-600 mb-6 leading-relaxed">
        Our GenAI platform provides comprehensive tools for managing AI workflows. 
        From prompt engineering to agent deployment, we've got you covered.
      </p>
      <div class="flex flex-wrap justify-center gap-4">
        <button
          type="button"
          onclick={handleTutorialClick}
          class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 gap-2"
        >
          Documentation
        </button>
        <button
          type="button"
          onclick={() => goto("/opsml/genai/prompt")}
          class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 gap-2"
        >
          Quick Start
        </button>
      </div>
    </div>
  </div>
</div>