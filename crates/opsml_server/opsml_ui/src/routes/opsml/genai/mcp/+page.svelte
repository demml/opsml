<script lang="ts">
  import { goto } from "$app/navigation";
  import { ArrowLeft, Clock, Bell, ExternalLink, BookOpen, MessageSquare } from 'lucide-svelte';
  
  interface Feature {
    title: string;
    description: string;
    icon: any;
  }

  const upcomingFeatures: Feature[] = [
    {
      title: "Registry Management",
      description: "Full CRUD operations for managing your AI assets with version control",
      icon: MessageSquare
    },
    {
      title: "Advanced Search",
      description: "Powerful filtering and search capabilities across all your resources",
      icon: MessageSquare
    },
    {
      title: "Collaboration Tools",
      description: "Team features for sharing and collaborating on AI workflows",
      icon: MessageSquare
    }
  ];

  function goBack() {
    goto("/opsml/genai");
  }

  function handleNotifyClick() {
    // You can implement email signup or notification logic here
    alert("Thanks for your interest! We'll notify you when this feature is available.");
  }

  function handleTutorialClick() {
    window.open("https://github.com/demml/opsml/tree/main/py-opsml/examples/llm", "_blank");
  }
</script>

<div class="flex-1 mx-auto w-11/12 pt-6 px-4 pb-10">
  
  <!-- Back Button -->
  <div class="mb-8">
    <button
      type="button"
      onclick={goBack}
      class="btn bg-surface-100 text-gray-700 hover:bg-surface-200 border-gray-300 border-2 px-4 py-2 gap-2"
    >
      <ArrowLeft size={16} />
      Back to GenAI
    </button>
  </div>

  <!-- Main Content -->
  <div class="text-center mb-16">
    <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl mb-6 neo-glow grain">
      <Clock size={32} class="text-white" />
    </div>
    
    <h1 class="text-4xl font-bold text-gray-900 mb-4">
      Coming Soon
    </h1>
    
    <p class="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
      We're working hard to bring you an amazing registry experience. This feature will be available soon 
      with powerful tools for managing your AI assets.
    </p>

    <div class="flex flex-wrap justify-center gap-4 mb-12">
      <button
        type="button"
        onclick={handleNotifyClick}
        class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 px-6 py-3 gap-2"
      >
        <Bell size={20} />
        Notify Me When Ready
      </button>
      
      <button
        type="button"
        onclick={handleTutorialClick}
        class="btn bg-surface-100 text-gray-700 hover:bg-surface-200 border-gray-300 border-2 px-6 py-3 gap-2"
      >
        <BookOpen size={20} />
        View Tutorials
        <ExternalLink size={16} />
      </button>
    </div>
  </div>

  <!-- What's Coming -->
  <div class="max-w-4xl mx-auto mb-16">
    <h2 class="text-2xl font-bold text-gray-900 mb-8 text-center">
      What's Coming
    </h2>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      {#each upcomingFeatures as feature}
        {@const IconComponent = feature.icon}
        <div class="bg-surface-50 border-gray-200 border-2 rounded-2xl p-6 text-center">
          <div class="flex items-center justify-center w-10 h-10 bg-gradient-to-br gradient-primary rounded-xl mb-4 mx-auto">
            <IconComponent size={20} class="text-white" />
          </div>
          
          <h3 class="text-lg font-semibold text-gray-900 mb-3">
            {feature.title}
          </h3>
          
          <p class="text-gray-600 text-sm leading-relaxed">
            {feature.description}
          </p>
        </div>
      {/each}
    </div>
  </div>

  <!-- Progress Indicator -->
  <div class="max-w-2xl mx-auto">
    <div class="bg-surface-50 border-black border-3 shadow rounded-2xl p-8 text-center">
      <h3 class="text-xl font-bold text-gray-900 mb-4">
        Development Progress
      </h3>
      
      <div class="w-full bg-gray-200 rounded-full h-4 mb-4">
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 h-4 rounded-full neo-glow" style="width: 45%"></div>
      </div>
      
      <p class="text-gray-600 mb-6 leading-relaxed">
        We're about 45% complete with this feature. Stay tuned for updates!
      </p>
      
      <div class="flex justify-center gap-4">
        <button
          type="button"
          onclick={goBack}
          class="btn bg-primary-500 text-black shadow shadow-hover border-black border-2 px-6 py-2"
        >
          Explore Available Features
        </button>
      </div>
    </div>
  </div>
</div>