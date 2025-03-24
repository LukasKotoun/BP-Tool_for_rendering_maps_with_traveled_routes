<script lang="ts">
    import { mapNodesElements, mapWaysElements, mapAreasElements } from '$lib/stores/mapStore';
    let test = $mapWaysElements

    export let multiplierMin: number;
    export let multiplierMax: number;
    function isPlotItem(obj: any): obj is PlotItem {
      return obj && typeof obj === 'object' && 'plot' in obj;
    }
  
    // Check if a category has immediate plot property (not just in children)
    function hasDirectPlot(obj: any): obj is PlotItem {
      return obj && typeof obj === 'object' && 'plot' in obj;
    }
</script>
<div class="space-y-4 rounded-lg bg-gray-100 mt-4 ">
    <h2 class="p-2 text-xl font-bold">Oblasti (polygony)</h2>
    {#each Object.entries(test) as [categoryKey, categoryValue], index}
      <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow border-l-2">
        <div class="flex items-center mb-2">
          {#if hasDirectPlot(categoryValue)}

            <div class="inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  class="h-5 w-5 items-center rounded-lg"
                  bind:checked={test[categoryKey].plot} 
                />
              
            </div>
            <h3 class="text-lg font-medium text-gray-1000 mr-3 ml-3">{categoryKey}</h3>

            {#if categoryValue.plot && ('width_scale' in categoryValue || 'text_scale' in categoryValue)}
              <div class="flex flex-wrap items-center ml-4">
                {#if 'width_scale' in categoryValue}
                <p class="text-xs mr-2">Násobek výchozí šířky čáry</p>
                  <div class="flex items-center mr-6">
                    <!-- Custom Tailwind Slider -->
                      <input
                        type="range" 
                        min={multiplierMin}
                        max={multiplierMax}
                        step="0.1" 
                        bind:value={$test[categoryKey].width_scale} 
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                    <p class="text-xs ml-1 w-6 text-right">{categoryValue.width_scale}</p>
                  </div>
                {/if}
                
                {#if 'text_scale' in categoryValue}
                <p class="text-xs mr-2">Násobek výchozí velikosti textu</p>
                  <div class="flex items-center">
                    <!-- Custom Tailwind Slider -->
                      <input 
                        type="range" 
                        min={multiplierMin}
                        max={multiplierMax} 
                        step="0.1" 
                        bind:value={test[categoryKey].text_scale}
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                    <span class="text-xs ml-1 w-6 text-right">{categoryValue.text_scale}</span>
                  </div>
                {/if}
              </div>
            {/if}
          {/if}
        </div>

        <!-- Plot items displayed horizontally -->
        {#if !hasDirectPlot(categoryValue)}
        <h3 class="text-lg font-medium mb-3 ml-3">{categoryKey}</h3>
        <div class="flex flex-wrap gap-2 ml-2 mb-3">
            {#each Object.entries(categoryValue) as [subKey, subValue]}
            {#if isPlotItem(subValue)}
              <div class="bg-white items-center rounded p-2 border border-gray-200 shadow-sm">
                <div class="flex justify-normal mb-1">
                      <input 
                        type="checkbox" 
                        class="h-5 w-5 rounded-lg"
                        bind:checked={test[categoryKey][subKey].plot}
                      >
                    <p class="text-sm ml-2">{subKey}</p>
                </div>
                
                {#if subValue.plot}
                  <div class="flex flex-col space-y-1 ml-5 mt-1">
                    {#if 'width_scale' in subValue}
                    <p class="text-xs text-gray-600 mr-4">Násobek výchozí šířky</p>
                    <div class="flex items-center p-1">
                          <input 
                            type="range" 
                            min={multiplierMin}
                            max={multiplierMax}  
                            step="0.1" 
                            bind:value={test[categoryKey][subKey].width_scale}
                            class="h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                        <p class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right">{subValue.width_scale}</p>
                      </div>
                    {/if}
                    
                    {#if 'text_scale' in subValue}
                    <p class="text-xs text-gray-600 mr-4">Násobek výchozí velikosti textu</p>
                      <div class="flex items-center p-1">
                        <!-- Custom Tailwind Slider -->
                          <input 
                            type="range" 
                            min={multiplierMin}
                            max={multiplierMax} 
                            step="0.1" 
                            bind:value={test[categoryKey][subKey].text_scale}
                            class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                        <p class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right">{subValue.text_scale}</p>
                      </div>
                    {/if}
                  </div>
                {/if}
              </div>
              {/if}
            {/each}
          </div>
        {/if}
      </div>
    {/each}
  </div>