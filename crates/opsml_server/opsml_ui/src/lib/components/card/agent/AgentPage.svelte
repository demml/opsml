<script lang="ts">
  import { goto } from "$app/navigation";
  import { ArrowLeft, Bell, ExternalLink, BookOpen } from 'lucide-svelte';
  
  interface Feature {
    title: string;
    description: string;
    icon: any;
  }


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
    
    <h1 class="text-4xl font-bold text-gray-900 mb-4">
      <span class="bg-error-500 inline-block px-3 py-1 py-2 text-white -rotate-2 shadow">Coming Soon</span>
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
      Was this page written with AI?
    </h2>
    
    <p class="text-gray-600 text-center">
      Yeah, deal with it. I didn't feel like writing a coming soon page.
    </p>
  </div>

</div>