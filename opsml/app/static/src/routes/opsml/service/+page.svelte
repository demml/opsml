<script>
    import { writable } from 'svelte/store';
  
    let searchQuery = '';
    let objects = [
      { id: 1, name: 'Object 1' },
      { id: 2, name: 'Object 2' },
      { id: 3, name: 'Object 3' },
      { id: 4, name: 'Object 4' }
    ];
    let filteredObjects = [...objects];
    let nodes = writable([]);
    let cards = writable([]);
    let connections = writable([]);
    let newObjectName = '';
    let offsetX = 0;
    let offsetY = 0;
    let connectingNode = null;
    let tempConnection = { x1: 0, y1: 0, x2: 0, y2: 0 };
  
    // Filter objects based on search query
    $: filteredObjects = objects.filter(obj => obj.name.toLowerCase().includes(searchQuery.toLowerCase()));
  
    function handleDragStart(event, object) {
      event.dataTransfer.setData('application/json', JSON.stringify(object));
      event.dataTransfer.effectAllowed = 'move';
    }
  
    function handleDrop(event) {
      const object = JSON.parse(event.dataTransfer.getData('application/json'));
      const dropZoneRect = event.target.getBoundingClientRect();
      const x = event.clientX - dropZoneRect.left;
      const y = event.clientY - dropZoneRect.top;
  
      // Check if the drop target is a valid "route" element
      if (event.target.classList.contains('route')) {
        nodes.update(n => {
          if (!n.find(node => node.id === object.id)) {
            return [...n, { id: object.id, label: object.name, x, y, linkedCards: [], linkedCardsText: '' }];
          }
          return n;
        });
      }
    }
  
    function handleCardDrop(event) {
      const object = JSON.parse(event.dataTransfer.getData('application/json'));
      cards.update(c => {
        if (!c.find(card => card.id === object.id)) {
          return [...c, { id: object.id, name: object.name }];
        }
        return c;
      });
    }
  
    function allowDrop(event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    }
  
    function handleNodeDrag(event, node) {
      const dropZoneRect = event.target.parentElement.getBoundingClientRect();
      const x = event.clientX - dropZoneRect.left - offsetX;
      const y = event.clientY - dropZoneRect.top - offsetY;
  
      nodes.update(n => {
        const index = n.findIndex(n => n.id === node.id);
        if (index !== -1) {
          n[index] = { ...n[index], x, y };
        }
        return n;
      });
    }
  
    function handleNodeDragStart(event, node) {
      // Create an invisible element to use as the drag image
      const img = new Image();
      img.src = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='; // 1x1 pixel transparent gif
      event.dataTransfer.setDragImage(img, 0, 0);
  
      // Calculate the offset between the mouse position and the top-left corner of the node
      const nodeRect = event.target.getBoundingClientRect();
      offsetX = event.clientX - nodeRect.left;
      offsetY = event.clientY - nodeRect.top;
    }
  
    function handleDragEnter(event) {
      event.preventDefault();
    }
  
    function addNewObject() {
      nodes.update(n => [...n, { id: Date.now(), label: newObjectName, x: 50, y: 50, linkedCards: [], linkedCardsText: '' }]);
      newObjectName = '';
    }
  
    function handleCardFieldDrop(event, node) {
      const object = JSON.parse(event.dataTransfer.getData('application/json'));
      nodes.update(n => {
        const index = n.findIndex(n => n.id === node.id);
        if (index !== -1) {
          if (!n[index].linkedCards) {
            n[index].linkedCards = [];
          }
          if (!n[index].linkedCards.includes(object.name)) {
            n[index].linkedCards.push(object.name);
            n[index].linkedCardsText = n[index].linkedCards.join(', ');
          }
        }
        return n;
      });
    }
  
    function deleteNode(nodeId) {
      nodes.update(n => n.filter(node => node.id !== nodeId));
      connections.update(c => c.filter(conn => conn.from !== nodeId && conn.to !== nodeId));
    }
  
    function startConnection(event, node) {
      connectingNode = node;
      const rect = event.target.getBoundingClientRect();
      tempConnection.x1 = rect.left + rect.width / 2;
      tempConnection.y1 = rect.top + rect.height / 2;
      tempConnection.x2 = tempConnection.x1;
      tempConnection.y2 = tempConnection.y1;
    }
  
    function updateTempConnection(event) {
      if (connectingNode) {
        tempConnection.x2 = event.clientX;
        tempConnection.y2 = event.clientY;
      }
    }
  
    function completeConnection(event, targetNode) {
      if (connectingNode && connectingNode.id !== targetNode.id) {
        connections.update(c => [...c, { from: connectingNode.id, to: targetNode.id }]);
      }
      connectingNode = null;
      tempConnection = { x1: 0, y1: 0, x2: 0, y2: 0 };
    }
  </script>
  
  <div class="flex h-screen">
    <div id="model-search" class="w-1/4 p-4 border-r border-gray-300">
      <input
        type="text"
        class="w-full p-2 mb-4 border border-gray-300 rounded"
        placeholder="Search objects..."
        bind:value={searchQuery}
      />
      {#each filteredObjects as object}
        <div
          class="p-2 mb-2 bg-gray-200 rounded cursor-grab"
          draggable="true"
          on:dragstart={(event) => handleDragStart(event, object)}
        >
          {object.name}
        </div>
      {/each}
    </div>
    <div class="w-3/4 p-4 flex flex-col relative">
      <div id="model-service" class="flex-1 border-b border-gray-300 p-4">
        <h2 class="text-xl mb-4">Model Service</h2>
        <div
          class="h-full border-2 border-dashed border-gray-300 flex items-center justify-center relative"
          on:drop={handleCardDrop}
          on:dragover={allowDrop}
          on:dragenter={handleDragEnter}
        >
          {#if $cards.length === 0}
            <p>Drag objects here to create cards</p>
          {:else}
            {#each $cards as card}
              <div
                class="p-4 mb-2 bg-white border rounded shadow cursor-grab"
                draggable="true"
                on:dragstart={(event) => handleDragStart(event, card)}
              >
                <p>{card.name}</p>
              </div>
            {/each}
          {/if}
        </div>
      </div>
      <div id="api-builder" class="flex-1 p-4 relative">
        <div
          class="h-full border-2 border-dashed border-gray-300 flex flex-col items-center justify-center relative"
          on:drop={handleDrop}
          on:dragover={allowDrop}
          on:dragenter={handleDragEnter}
        >
          {#if $nodes.length === 0}
            <p>Drag objects here</p>
          {:else}
            {#each $nodes as node}
              <div
                class="route p-2 mb-2 bg-gray-300 rounded cursor-grab absolute"
                style="left: {node.x}px; top: {node.y}px;"
                draggable="true"
                on:drag={(event) => handleNodeDrag(event, node)}
                on:dragstart={(event) => handleNodeDragStart(event, node)}
                on:dragover={(event) => event.preventDefault()}
                on:dragenter={(event) => event.preventDefault()}
                on:dblclick={() => startConnection(node)}
                on:mouseup={() => completeConnection(node)}
              >
                <label class="block mb-1">Name</label>
                <input type="text" class="mb-2 p-1 border rounded" bind:value={node.label} placeholder="Name" />
                <label class="block mb-1">Model(s)</label>
                <textarea
                  class="p-2 bg-white border rounded mb-2 w-full"
                  bind:value={node.linkedCardsText}
                  on:input={(event) => node.linkedCards = event.target.value.split(',').map(s => s.trim())}
                  on:drop={(event) => handleCardFieldDrop(event, node)}
                  on:dragover={allowDrop}
                  on:dragenter={handleDragEnter}
                ></textarea>
                <button class="p-1 bg-red-500 text-white rounded" on:click={() => deleteNode(node.id)}>Delete</button>
              </div>
            {/each}
          {/if}
          <button class="absolute bottom-4 right-4 p-2 bg-blue-500 text-white rounded" on:click={addNewObject}>+</button>
        </div>
        <svg class="absolute inset-0 w-full h-full pointer-events-none">
          {#each $connections as conn}
            {#if $nodes.find(n => n.id === conn.from) && $nodes.find(n => n.id === conn.to)}
              <line
                x1={$nodes.find(n => n.id === conn.from).x + 50}
                y1={$nodes.find(n => n.id === conn.from).y + 25}
                x2={$nodes.find(n => n.id === conn.to).x + 50}
                y2={$nodes.find(n => n.id === conn.to).y + 25}
                stroke="black"
                stroke-width="2"
                marker-end="url(#arrowhead)"
              />
            {/if}
          {/each}
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" />
            </marker>
          </defs>
        </svg>
      </div>
    </div>
  </div>