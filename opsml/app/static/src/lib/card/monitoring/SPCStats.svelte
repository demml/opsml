<script lang="ts">

    import { type FeatureDriftProfile, type ChartjsData} from "$lib/scripts/types";
    import IndividualChart from "$lib/card/run/IndividualCharts.svelte";
    import Fa from 'svelte-fa';
    import { faComputer } from '@fortawesome/free-solid-svg-icons';

    export let feature_profile: FeatureDriftProfile;
    export let featureDistVizData: ChartjsData;


    let center_rounded = feature_profile.center.toFixed(2);
    let one_lcl_rounded = feature_profile.one_lcl.toFixed(2);
    let one_ucl_rounded = feature_profile.one_ucl.toFixed(2);
    let two_lcl_rounded = feature_profile.two_lcl.toFixed(2);
    let two_ucl_rounded = feature_profile.two_ucl.toFixed(2);
    let three_lcl_rounded = feature_profile.three_lcl.toFixed(2);
    let three_ucl_rounded = feature_profile.three_ucl.toFixed(2);

  </script>

  
    
    <div class="flex flex-col space-y-1">

      <div class="rounded-lg border-2 border-darkpurple px-4 shadow-md shadow-primary-500 lg:mt-2 mb-2 pb-2 overflow-x-scroll bg-white">
        <div class="min-h-[250px] max-h-[225px] lg:mt-2">
          <div class="flex flex-row items-center border-b-2 border-gray-400">
            <Fa icon={faComputer} color="#04cd9b"/>
            <header class="pl-2 text-darkpurple text-lg font-bold">Feature Distribution</header>
          </div>
          <div class="min-h-[200px]">
            <IndividualChart
              data={featureDistVizData.data}
              type="bar"
              options={featureDistVizData.options}
              id="featureChart"
            />
          </div>
        </div>
      </div>

      <div class="rounded-lg border-2 border-darkpurple px-4 shadow-md shadow-primary-500 mb-2 pb-2 overflow-x-scroll bg-white w-auto">
        <div>
          <div class="flex flex-row items-center border-b-2 border-gray-400 mb-2">
            <Fa icon={faComputer} color="#04cd9b"/>
            <div class="flex flex-row items-center justify-center gap-x-2">
              <header class="pl-2 text-darkpurple text-lg font-bold">Feature Stats</header>
              <div class=" text-darkpurple text-sm">Zone | LCL | UCL </div>
            </div>
          </div>

          <div id="stat-grid" class="grid grid-rows-4 justify-center items-center gap-y-1"> 
            <div class="my-1 flex flex-row rounded-lg border border-darkpurple text-sm w-fit">
              <div class="px-2 rounded-l-lg text-darkpurple bg-primary-50 italic">Center</div> 
                  <div class="px-2 border-l border-darkpurple text-scouter_red bg-surface-50">{center_rounded}</div> 
                  <div class="px-2 border-l border-darkpurple rounded-r-lg text-secondary-500 bg-surface-50">{center_rounded}</div> 
            </div>
            <div class="my-1 flex flex-row rounded-lg border border-darkpurple text-sm w-fit">
              <div class="px-2 rounded-l-lg text-darkpurple bg-primary-50 italic">Zone 1</div> 
                  <div class="px-2 border-l border-darkpurple text-scouter_red bg-surface-50">{one_lcl_rounded}</div> 
                  <div class="px-2 border-l border-darkpurple rounded-r-lg text-secondary-500 bg-surface-50">{one_ucl_rounded}</div> 
            </div>
            <div class="my-1 flex flex-row rounded-lg border border-darkpurple text-sm w-fit">
              <div class="px-2 rounded-l-lg text-darkpurple bg-primary-50 italic">Zone 2</div> 
                  <div class="px-2 border-l border-darkpurple text-scouter_red bg-surface-50">{two_lcl_rounded}</div> 
                  <div class="px-2 border-l border-darkpurple rounded-r-lg text-secondary-500 bg-surface-50">{two_ucl_rounded}</div> 
            </div>
            <div class="my-1 flex flex-row rounded-lg border border-darkpurple text-sm w-fit">
              <div class="px-2 rounded-l-lg text-darkpurple bg-primary-50 italic">Zone 3</div> 
                  <div class="px-2 border-l border-darkpurple text-scouter_red bg-surface-50">{three_lcl_rounded}</div> 
                  <div class="px-2 border-l border-darkpurple rounded-r-lg text-secondary-500 bg-surface-50">{three_ucl_rounded}</div> 
            </div>
          </div>
        </div>
      </div>
    </div>

    
    