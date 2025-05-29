<script lang="ts">
    import { goto } from "$app/navigation";
    import {CircuitBoard, NotebookText, FlaskConical, Table, BrainCircuit } from 'lucide-svelte';
    import { type SpaceStats } from "../card/types";
  
    let {
      stats
    } = $props<{
      stats: SpaceStats;
    }>();

    function navigateToSpacePage() {
      goto(`/opsml/space/${stats.name}`);
    }
  
  
  </script>

  <button 
  class="w-full max-w-96 h-auto p-3 text-black rounded-lg shadow border-2 border-black bg-primary-400 hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" 
  onclick={navigateToSpacePage}
  >
    <div class="flex items-center justify-start gap-2">
      <div class="ml-2">
        <CircuitBoard color="#5948a3" />
      </div>
      <div><h4 class="truncate font-bold">{stats.space}</h4></div>
    </div>
 
    <div class="flex items-center justify-start gap-2">
      <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs lg:text-sm mb-1">
        <div class="ml-2">
          <BrainCircuit color="#5948a3" />
        </div>
          <div class="text-black">{stats.model_count} models</div>
      </div>

      <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs lg:text-sm mb-1">
        <div class="ml-2">
          <Table color="#5948a3" />
        </div>
          <div class="text-black">{stats.data_count} datasets</div>
      </div>
    </div>

    <div class="flex items-center justify-start gap-2">
      <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs lg:text-sm mb-1">
        <div class="ml-2">
          <FlaskConical color="#5948a3" />
        </div>
          <div class="text-black">{stats.experiment_count} experiments</div>
      </div>

      <div class="flex items-center justify-start gap-2 overflow-hidden whitespace-nowrap text-xs lg:text-sm mb-1">
        <div class="ml-2">
          <NotebookText color="#5948a3" />
        </div>
          <div class="text-black">{stats.prompt_count} prompts</div>
      </div>
    </div>

  </button>

