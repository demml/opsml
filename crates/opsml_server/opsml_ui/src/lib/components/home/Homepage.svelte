<script lang="ts">
  import type { HomePageStats, RecentCards } from "$lib/components/home/utils";
  import HomeCard from "$lib/components/home/HomeCard.svelte";
  import { FlaskConical, Table, BrainCircuit, NotebookText, ExternalLink, BookOpen, Menu, Activity} from 'lucide-svelte';
  import { goto } from "$app/navigation";

  let { cards, stats } = $props<{
     cards: RecentCards;
     stats: HomePageStats;
  }>();

  // Registry metadata with descriptions and navigation
  const registryInfo = [
    {
      title: "Models",
      description: "Train, version, and manage machine learning models. Track model performance and manage the complete ML lifecycle.",
      icon: BrainCircuit,
      path: "/opsml/model",
      color: "gradient-primary"
    },
    {
      title: "Data", 
      description: "Manage datasets with versioning and lineage tracking. Process, validate, and share data.",
      icon: Table,
      path: "/opsml/data",
      color: "gradient-secondary"
    },
    {
      title: "Prompts",
      description: "Create, test, and version GenAI prompts. Build consistent prompt templates for reliable AI interactions.",
      icon: NotebookText, 
      path: "/opsml/genai/prompt",
      color: "gradient-success"
    },
    {
      title: "Experiments",
      description: "Track ML experiments, compare results, and reproduce successful runs. Organize your research workflow.",
      icon: FlaskConical,
      path: "/opsml/experiment", 
      color: "gradient-warning"
    }
  ];

  function handleRegistryClick(path: string) {
    goto(path);
  }

  function handleDocumentationClick() {
    window.open("https://docs.demml.io/opsml/", "_blank");
  }
</script>

<section class="pt-6 px-4 pb-4 alt-grid-background">

  <div class="mb-12 mx-auto w-11/12">
    <div class="flex items-center gap-4 mb-6">
      <div>
        <h1 class="text-3xl font-bold mb-3">
          <span class="bg-primary-500 inline-block px-3 py-1 py-2 text-white border-4 border-black shadow text-3xl sm:text-4xl md:text-5xl">OpsML Dashboard</span>
        </h1>
        <p class="text-gray-600">
          Monitor your ML workflows and explore your registries
        </p>
      </div>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="bg-surface-50 border-2 border-primary-700 rounded-xl p-4 text-center">
        <div class="text-2xl font-bold text-primary-700 mb-1">
          {stats.nbrModels || 0}
        </div>
        <div class="text-sm text-gray-600">Recent Models</div>
      </div>
      <div class="bg-surface-50 border-2 border-primary-700 rounded-xl p-4 text-center">
        <div class="text-2xl font-bold text-primary-700 mb-1">
          {stats.nbrData || 0}
        </div>
        <div class="text-sm text-gray-600">Data Assets</div>
      </div>
      <div class="bg-surface-50 border-2 border-primary-700 rounded-xl p-4 text-center">
        <div class="text-2xl font-bold text-primary-700 mb-1">
          {stats.nbrPrompts || 0}
        </div>
        <div class="text-sm text-gray-600">Prompts</div>
      </div>
      <div class="bg-surface-50 border-2 border-primary-700 rounded-xl p-4 text-center">
        <div class="text-2xl font-bold text-primary-700 mb-1">
          {stats.nbrExperiments || 0}
        </div>
        <div class="text-sm text-gray-600">Experiments</div>
      </div>
    </div>

    <div class="flex flex-wrap gap-3 justify-center lg:justify-start">
      <button
        type="button"
        onclick={handleDocumentationClick}
        class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 px-4 py-2 gap-2"
      >
        <BookOpen size={16} />
        Documentation
      </button>
    </div>
  </div>

</section>
<div class="w-full h-2 bg-black rounded"></div>

<section class="grid-background py-6">
  <div class="mb-8 mx-auto w-11/12">
    <div class="flex items-center gap-3 mb-8">
      <Activity size={24} class="text-primary-600" />
      <h2 class="text-2xl font-bold text-gray-900">
        Recent Activity
      </h2>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mx-4 md:mx-8">
      <HomeCard 
        header="Models" 
        cards={cards.modelcards}
        headerColor="bg-primary-500" 
        headerTextColor="text-black" 
        iconColor="#8059b6"
        badgeColor="#8059b6"
      />
      <HomeCard 
        header="Data"
        cards={cards.datacards}
        headerColor="bg-primary-500"
        headerTextColor="text-black" 
        iconColor="#8059b6"
        badgeColor="#8059b6"
      />
      
      <HomeCard 
        header="Prompts" 
        cards={cards.promptcards}
        headerColor="bg-primary-500" 
        headerTextColor="text-black" 
        iconColor="#8059b6"
        badgeColor="#8059b6"
      />
      <HomeCard 
        header="Experiments"
        cards={cards.experimentcards}
        headerColor="bg-primary-500" 
        headerTextColor="text-black"
        iconColor="#8059b6"
        badgeColor="#8059b6"
      />
    </div>
  </div>
</section>
<div class="w-full h-2 bg-black rounded"></div>

<section class="alt-grid-background py-6">
  <div class="mx-auto w-11/12 px-4">

    <div class="flex items-center gap-3 mb-8">
      <Menu size={24} class="text-primary-600" />
      <h2 class="text-2xl font-bold text-gray-900">
        Explore Registries
      </h2>
    </div>

    <div class="max-w-6xl mx-auto mb-16">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {#each registryInfo as registry}
          <div class="flex flex-col items-start bg-surface-50 border-primary-800 border-3 shadow-primary rounded-2xl p-8">
          
            <h3 class="text-xl font-bold text-gray-900 mb-4">
              {registry.title}
            </h3>
            
            <p class="text-gray-600 text-left leading-relaxed mb-6 flex-1">
              {registry.description}
            </p>
            
            <a
              href={registry.path}
              data-sveltekit-preload-data="hover"
              class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 px-4 py-2 gap-2 w-full"
            >
              Explore {registry.title}
              <ExternalLink size={16} />
            </a>
          </div>
        {/each}
      </div>
    </div>

  </div>
</section>
<div class="w-full h-2 bg-black rounded"></div>

<div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">
  <div class="max-w-4xl mx-auto">
    <div class="rounded-2xl p-8 bg-surface-50 border-black border-3 shadow">
      <h3 class="text-xl font-bold text-gray-900 mb-4">
        Ready to Get Started?
      </h3>
      <p class="text-gray-600 mb-6 leading-relaxed">
        Refer to the following links to start exploring and managing your machine learning assets.
      </p>
      <div class="flex flex-wrap justify-center gap-4">
        <button
          type="button"
          onclick={handleDocumentationClick}
          class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 gap-2"
        >
          <BookOpen size={16} />
          Documentation
        </button>
        <button
          type="button"
          onclick={() => goto("/opsml/model")}
          class="btn bg-secondary-500 text-black shadow shadow-hover border-black border-2 gap-2"
        >
          <BrainCircuit size={16} />
          Start with Models
        </button>
        <button
          type="button"
          onclick={() => goto("/opsml/data")}
          class="btn bg-success-500 text-black shadow shadow-hover border-black border-2 gap-2"
        >
          <Table size={16} />
          Manage Data
        </button>
      </div>
    </div>
  </div>
</div>


<style>
  .grid-background {
    background-color: #E3DFF2;
    background-image: 
      linear-gradient(to right, #CECBDB 1px, transparent 1px),
      linear-gradient(to bottom, #CECBDB 1px, transparent 1px);
    background-size: 60px 60px;
  }
  .alt-grid-background {
    background-color: #f8f8f8;
    background-image: 
      linear-gradient(to right, #CECBDB 1px, transparent 1px),
      linear-gradient(to bottom, #CECBDB 1px, transparent 1px);
    background-size: 60px 60px;
  }
</style>