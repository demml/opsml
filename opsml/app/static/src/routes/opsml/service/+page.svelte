<script lang="ts">

  import logo from "$lib/images/opsml-logo.png";
  import Fa from 'svelte-fa'
  import { faAdd } from '@fortawesome/free-solid-svg-icons'

  let svgClass: string = "flex-none w-3 mr-0.5 fill-secondary-500 dark:fill-secondary-500";

  let cardBasket: any = [];
  let serviceName: string = '';
  let modelName: string = '';
  let addModel: boolean = false;

  async function handleRegister() {
    console.log('Registering service', serviceName);
  }

  async function addModelToService() {
    addModel = true;
  }

  let hoveringOverBasket;

  function dragStart(event, model) {
		// The data we want to make available when the element is dropped
    // is the index of the item being dragged and
    // the index of the basket from which it is leaving.
		const data = {model};
   	event.dataTransfer.setData('text/plain', JSON.stringify(data));
	}


  function drop(event) {
		event.preventDefault();
    console.log('event')
    const json = event.dataTransfer.getData("text/plain");
		const data = JSON.parse(json);
    console.log(data);
    
		//
		//// Remove the item from one basket.
		//// Splice returns an array of the deleted elements, just one in this case.
		//const [item] = cardBasket[data.serviceIndex].items.splice(data.serviceItemIndex, 1);
		//
    //// Add the item to the drop target basket.
		//cardBasket[serviceIndex].items.push(item);
		//cardBasket = cardBasket;
		//
		//hoveringOverBasket = null;
	}

</script>

<div class="flex flex-wrap bg-white min-h-screen mb-8">

  <div class="w-full md:w-1/3 mt-4 ml-4 pl-2 md:ml-12">

    <a draggable={true} on:dragstart={event => dragStart(event, "hello")} class= "block card max-w-96 border p-4 bg-gray-50 rounded-2xl  hover:border-solid hover:border hover:border-secondary-500 dark:bg-surface-700 dark:hover:bg-surface-600" href="#">
      <header class="flex items-center ml-0.5 mb-0.5" title="blah/blah">
        <h4 class="truncate font-boing">blah/blah</h4>
      </header>
    
      <div class="mr-1 ml-0.5 flex items-center overflow-hidden whitespace-nowrap text-sm leading-tight">
        <svg class="flex-none w-3 mr-1 {svgClass}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <path d="M 12 0 C 5.371094 0 0 5.371094 0 12 C 0 18.628906 5.371094 24 12 24 C 18.628906 24 24 18.628906 24 12 C 24 5.371094 18.628906 0 12 0 Z M 12 2 C 17.523438 2 22 6.476563 22 12 C 22 17.523438 17.523438 22 12 22 C 6.476563 22 2 17.523438 2 12 C 2 6.476563 6.476563 2 12 2 Z M 10.9375 3.875 L 10.5 12.0625 L 10.59375 12.9375 L 16.75 18.375 L 17.71875 17.375 L 12.625 11.96875 L 12.1875 3.875 Z"></path>
        </svg>
        <span class="truncate text-black dark:text-white">
          <time datetime={ Date() } >
            Last updated
          </time>
        </span>
        <span class="px-1.5 text-black dark:text-white">- </span>
        <svg class="flex-none w-3 mr-0.5 {svgClass}" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
          <path d="M8 3a3 3 0 0 0-1 5.83v6.34a3.001 3.001 0 1 0 2 0V15a2 2 0 0 1 2-2h1a5.002 5.002 0 0 0 4.927-4.146A3.001 3.001 0 0 0 16 3a3 3 0 0 0-1.105 5.79A3.001 3.001 0 0 1 12 11h-1c-.729 0-1.412.195-2 .535V8.83A3.001 3.001 0 0 0 8 3Z"/>
        </svg>
        <div class="text-black dark:text-white"> {10} versions</div>
      </div>
    </a>
  </div>

  <div class="min-h-screen  bg-primary-500 w-[2px]"></div>

  <div class="flex flex-col w-full md:w-7/12 mt-5">

    <section class="pt-4 border-gray-100 col-span-full flex-1 pb-16 items-center pl-8">

      <form class="z-10 mx-auto rounded-2xl bg-slate-100 border shadow p-4 md:px-5" on:submit|preventDefault={handleRegister}>
  
        <img alt="OpsML logo" class="mx-auto -mt-12 mb-2 w-20" src={logo}>
        <h2 class="pt-1 pb-4 text-center text-3xl font-bold text-primary-500">Model Service</h2>
        
        <div class="mb-8 grid grid-cols-1 gap-3">
  
          <label class="text-primary-500">Service Name
            <input
              class="input rounded-lg bg-slate-200 hover:bg-slate-100"
              type="text" 
              placeholder="Service Name"
              bind:value={serviceName}
            />
          </label>

          {#if addModel}
            <label class="text-primary-500 pb-4">Model Name
              <input
                class="input rounded-lg bg-slate-200 hover:bg-slate-100"
                type="text" 
                placeholder="Model Name"
                bind:value={modelName}
              />
            </label>

            <input
                class="input rounded-lg bg-slate-200 hover:bg-slate-100"
                type="text" 
                placeholder="Model"
                bind:value={modelName}
                on:drop={event => drop(event)}
              />


          {/if}

          <div class="flex flex-row items-center align-center">
            <button type="button" class="m-1 btn btn-sm bg-darkpurple text-white mr-2" on:click={() => addModelToService() }>
              <Fa class="h-3" icon={faAdd}/>
              <header class="text-white text-xs">Add Model</header>
            </button>
  
          </div>

  
        </div>
  
        <div class="grid justify-items-center">
          <button type="submit" class="btn bg-primary-500 text-white rounded-lg md:w-72 justify-self-center mb-2">
            <span>Register Service</span>
          </button>
        </div>
      </form>
    </section>
  </div>

</div>

