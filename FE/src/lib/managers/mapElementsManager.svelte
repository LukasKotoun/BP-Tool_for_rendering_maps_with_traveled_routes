<script lang="ts">
    // TypeScript interfaces for your data structure
    interface PlotItem {
      plot: boolean;
      width_scale?: number;
      text_scale?: number;
    }
    
    interface MapCategory {
      [key: string]: MapCategory | PlotItem;
    }
    
    // Your data structure (this would typically come from a prop or store)
    let areas: MapCategory = {
      "highway": {
        "motorway": {"plot": false, "width_scale": 1},
        "primary": {"plot": false}
      },
      "railway": {
        "rail": {"plot": false, "width_scale": 1, "text_scale": 3},
        "subway": {"plot": false}
      },
      "route": {"plot": false, "width_scale": 2},
      "barrier": {"plot": false}
    };
    
    // Helper function to check if an object is a PlotItem
    function isPlotItem(obj: any): obj is PlotItem {
      return obj && typeof obj === 'object' && 'plot' in obj;
    }
  
    // Check if a category has immediate plot property (not just in children)
    function hasDirectPlot(obj: any): obj is PlotItem {
      return obj && typeof obj === 'object' && 'plot' in obj;
    }
    
  </script>
    <div class="bg-blue-500 text-white p-4">
        This div should have a blue background.
      </div>
  <div class="max-w-4xl mx-auto font-sans bg-white shadow-lg rounded-lg overflow-hidden p-6">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Map Layer Controls</h2>
    
    <div class="space-y-4">
      <!-- Map Structure Label -->
      <div class="text-lg font-semibold text-gray-700 pl-2 border-l-4 border-blue-500">
        areas
      </div>
      
      {#each Object.entries(areas) as [categoryKey, categoryValue], index}
        <div class="ml-4 p-4 bg-gray-50 rounded-md shadow border-l-2 border-blue-400">
          <!-- Category Header with possible checkbox -->
          <div class="flex items-center mb-2">
            <h3 class="text-lg font-medium text-gray-800 mr-3">{categoryKey}</h3>
            
            {#if hasDirectPlot(categoryValue)}
              <!-- Custom Tailwind Checkbox -->
              <label class="inline-flex items-center cursor-pointer">
                <div class="relative">
                  <input 
                    type="checkbox" 
                    class="sr-only peer" 
                    bind:checked={categoryValue.plot}
                  >
                  <div class="w-5 h-5 bg-white border-2 border-gray-300 rounded transition-colors peer-checked:bg-blue-500 peer-checked:border-blue-500 peer-focus:ring-2 peer-focus:ring-blue-200"></div>
                
                </div>
              </label>
              
              {#if categoryValue.plot && ('width_scale' in categoryValue || 'text_scale' in categoryValue)}
                <div class="flex flex-wrap items-center ml-4">
                  {#if 'width_scale' in categoryValue}
                    <div class="flex items-center mr-6">
                      <span class="text-xs text-gray-600 mr-2">Width</span>
                      <!-- Custom Tailwind Slider -->
                      <div class="relative w-24">
                        <input 
                          type="range" 
                          min="0.1" 
                          max="5" 
                          step="0.1" 
                          bind:value={categoryValue.width_scale} 
                          disabled={!categoryValue.plot}
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      </div>
                      <span class="text-xs text-gray-600 ml-1 w-6 text-right">{categoryValue.width_scale}</span>
                    </div>
                  {/if}
                  
                  {#if 'text_scale' in categoryValue}
                    <div class="flex items-center">
                      <span class="text-xs text-gray-600 mr-2">Text</span>
                      <!-- Custom Tailwind Slider -->
                      <div class="relative w-24">
                        <input 
                          type="range" 
                          min="0.1" 
                          max="5" 
                          step="0.1" 
                          bind:value={categoryValue.text_scale}
                          disabled={!categoryValue.plot}
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      </div>
                      <span class="text-xs text-gray-600 ml-1 w-6 text-right">{categoryValue.text_scale}</span>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>

          <!-- Plot items displayed horizontally -->
          {#if !hasDirectPlot(categoryValue)}
            <div class="flex flex-wrap gap-2 ml-4 mb-3">
              {#each Object.entries(categoryValue) as [subKey, subValue]}
              {#if isPlotItem(subValue)}
                <div class="bg-white rounded p-2 border border-gray-200 shadow-sm">
                  <div class="flex items-center mb-1">
                    <label class="inline-flex items-center cursor-pointer">
                      <div class="relative">
                        <input 
                          type="checkbox" 
                          class="sr-only peer" 
                          bind:checked={subValue.plot}
                        >

                      <span class="text-sm ml-2">{subKey}</span>
                    </label>
                  </div>
                  
                  {#if subValue.plot}
                    <div class="flex flex-col space-y-1 ml-5 mt-1">
                      {#if 'width_scale' in subValue}
                        <div class="flex items-center">
                          <span class="text-xs text-gray-600 w-10">Width</span>
                          <!-- Custom Tailwind Slider -->
                          <div class="relative w-20">
                            <input 
                              type="range" 
                              min="0.1" 
                              max="5" 
                              step="0.1" 
                              bind:value={subValue.width_scale}
                              disabled={!subValue.plot}
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                          </div>
                          <span class="text-xs text-gray-600 ml-1 w-6 text-right">{subValue.width_scale}</span>
                        </div>
                      {/if}
                      
                      {#if 'text_scale' in subValue}
                        <div class="flex items-center">
                          <span class="text-xs text-gray-600 w-10">Text</span>
                          <!-- Custom Tailwind Slider -->
                          <div class="relative w-20">
                            <input 
                              type="range" 
                              min="0.1" 
                              max="5" 
                              step="0.1" 
                              bind:value={subValue.text_scale}
                              disabled={!subValue.plot}
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                          </div>
                          <span class="text-xs text-gray-600 ml-1 w-6 text-right">{subValue.text_scale}</span>
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
  </div>