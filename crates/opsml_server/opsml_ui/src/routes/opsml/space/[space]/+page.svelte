<script lang="ts">
  import {CircuitBoard, NotebookText, FlaskConical, Table, BrainCircuit } from 'lucide-svelte';

</script>


<div class="flex-1 mx-auto w-9/12 pt-20 pt-[100px] justify-center px-4 pb-10">

    <!-- Left column for activity and members-->
    <div class="grid grid-cols-1 md:grid-cols-6 gap-4 w-full">
        <div class="col-span-1 md:col-span-2 bg-slate-100 p-4 flex flex-col rounded-base border-black border-2 shadow min-h-[400px] h-fit">
            <!-- Top Section -->
          <div class="mb-4">
            <h3 class="font-bold text-lg">Activity</h3>
            <p class="text-sm text-gray-500">View recent activity in this space</p>
          </div>
          
        </div>

    </div>

    <!-- Right column for experiments, models, prompts -->
    <div class="col-span-1 md:col-span-4 gap-1 p-4 flex flex-col h-auto">

      <div class="rounded-base border-primary-500 border-2 shadow-primary bg-surface-50">
        <div class="flex flex-row items-center gap-2 pb-2">
          <div class="rounded-full bg-surface-200 border-black border-2 p-1 shadow-small">
            <BrainCircuit color="#40328b" />
          </div>
          <h2 class="font-bold text-primary-800 text-xl">Models</h2>
        </div>
      </div>

    </div>

</div>