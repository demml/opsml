<script lang="ts">

import { writable } from 'svelte/store';
  import {
    SvelteFlow,
    Controls,
    Background,
    MiniMap,
  } from '@xyflow/svelte';

  import '@xyflow/svelte/dist/style.css'

  import PackageNode from './PackageNode.svelte';

  const nodeTypes = {
    'package': PackageNode
  };

  const nodes = writable([
    {
    id: '1',
    type: 'package',
    data: {
            package_name: writable("accelerate"), 
            version: writable("0.26.1")
          },
    position: {"x": 0, "y": 0},
    },
    {
    id: '2', 
    type: 'package',
    data: {
          package_name: writable('huggingface-hub'), 
          version: writable('0.24.6')
        }, 
    position: {'x': 200, 'y': 0}
    },
    {
    id: '3',
    type: 'package',
    data: {
            package_name: writable("accedlerate"), 
            version: writable("0.26.1")
          },
    position: {"x": 0, "y": 0},
    },
    {
    id: '4', 
    type: 'package',
    data: {
          package_name: writable('hugginsgface-hub'), 
          version: writable('0.24.6')
        }, 
    position: {'x': 200, 'y': 0}
    },{
    id: '5',
    type: 'package',
    data: {
            package_name: writable("accfelerate"), 
            version: writable("0.26.1")
          },
    position: {"x": 0, "y": 0},
    },
    {
    id: '6', 
    type: 'package',
    data: {
          package_name: writable('huggingfacea-hub'), 
          version: writable('0.24.6')
        }, 
    position: {'x': 200, 'y': 0}
    },
    {
    id: '7',
    type: 'package',
    data: {
            package_name: writable("accelerate"), 
            version: writable("0.26.1")
          },
    position: {"x": 0, "y": 0},
    },
    {
    id: '8', 
    type: 'package',
    data: {
          package_name: writable('huggingface-hub'), 
          version: writable('0.24.6')
        }, 
    position: {'x': 200, 'y': 0}
    }
   
  ]);

  const edges = writable([
    {
      id: '1-2',
      source: '1',
      target: '2',
    }
  ]);



</script>

<div class="flex min-h-screen">

  <div class="w-full bg-white px-16 py-4 gap-4">

    <SvelteFlow {nodes} {edges} {nodeTypes} fitView>
      <Controls />
      <Background />
      <MiniMap />
    </SvelteFlow>

  </div>


</div>