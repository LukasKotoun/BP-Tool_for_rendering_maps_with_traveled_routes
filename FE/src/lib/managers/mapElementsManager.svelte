<script lang="ts"> 
    import { mapNodesElements, mapWaysElements, mapAreasElements, automaticZoomLevel, mapElementsZoomDesign, mapElementsWantedZoom } from '$lib/stores/mapStore';
    import { mapValue, updateWantedElements } from '$lib/utils/mapElementsUtils';
    import { nodesKeysNamesMappingCZ, nodesNamesMappingCZ, waysKeysNamesMappingCZ, waysNamesMappingCZ,
       areasKeysNamesMappingCZ, areasNamesMappingCZ, numberOfZoomLevels, wantedNodesUpdatesZooms,
       wantedWaysUpdatesZooms, wantedAreasUpdatesZooms } from '$lib/constants';
    const multiplierMin = 0.1
    const multiplierMax = 4
    
    function hasDirectPlot(obj: any): obj is MapElementAttributes {
      return obj && typeof obj === 'object' && 'plot' in obj;
    }

    function setNodesForZoom(zoomLevel: number){
      //set to false and iteriate while using
      for (let i =0; i<=zoomLevel; i++){
        console.log(wantedNodesUpdatesZooms[i])
      }
    }

    function setAreasForZoom(zoomLevel: number){
      for (let i =0; i<=zoomLevel; i++){
        console.log(wantedNodesUpdatesZooms[i])
      }
    }
   
    function setWaysForZoom(zoomLevel: number){
      for (let i =0; i<=zoomLevel; i++){
        console.log(wantedNodesUpdatesZooms[i])
      }
    }

    $:{
      $automaticZoomLevel
      $mapElementsZoomDesign.nodes = $automaticZoomLevel
      $mapElementsZoomDesign.ways = $automaticZoomLevel
      $mapElementsZoomDesign.areas = $automaticZoomLevel
      $mapElementsZoomDesign.general = $automaticZoomLevel
      $mapElementsWantedZoom.nodes = $automaticZoomLevel
      $mapElementsWantedZoom.ways = $automaticZoomLevel
      $mapElementsWantedZoom.areas = $automaticZoomLevel
    }


  </script>

   <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Mapové prvky</h1>
    <div class="space-y-4 rounded-lg bg-gray-100 ">
      <h2 class="p-2 text-xl font-bold">Vzhled mapových prvků na základě úrovně přiblížení (detailu)</h2>
      <div class="p-4 flex flex-wrap gap-4 items-start">
       

        <div class="flex flex-col">
          <p class="text-md font-medium mb-1">Úroveň detailu bodů</p>
          <select
          class="border rounded p-2 w-40"
          bind:value={$mapElementsZoomDesign.nodes}
        >
          {#each Array.from({length: numberOfZoomLevels}, (_, i) => i+1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
        </div>

        <div class="flex flex-col">
          <p class="text-md font-medium mb-1">Úroveň detailu cest</p>
          <select
          class="border rounded p-2 w-40"
          bind:value={$mapElementsZoomDesign.ways}
        >
          {#each Array.from({length: numberOfZoomLevels}, (_, i) => i+1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
        </div>

        <div class="flex flex-col">
          <p class="text-md font-medium mb-1">Úroveň detailu oblastí</p>
          <select
          class="border rounded p-2 w-40"
          bind:value={$mapElementsZoomDesign.areas}
        >
          {#each Array.from({length: numberOfZoomLevels}, (_, i) => i+1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
        </div>
        <div class="flex flex-col">
          <p class="text-md font-medium mb-1">Úroveň detail obecných prvků</p>
          <select
          class="border rounded p-2 w-40"
          bind:value={$mapElementsZoomDesign.general}
        >
          {#each Array.from({length: numberOfZoomLevels}, (_, i) => i+1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
        </div>
      </div>
      </div>
      
      

    <div class="space-y-4 rounded-lg bg-gray-100 mt-4">
      <h2 class="p-2 text-xl font-bold">Filtr některých bodů (odstranění nevyhovujících)</h2>
        <div class="p-4 flex flex-wrap gap-10 items-start">
          <div class="flex flex-col">
            <p class="text-sm font-medium mb-1">Minimální počet obyvatel vesnic, měst, velkoměst</p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm font-medium mb-1">Citlivost filtru na důležitost výškových bodů</p>
          </div>
        </div>
    </div>

    <div class="space-y-4 rounded-lg bg-gray-100 mt-4">
      <h2 class="p-2 text-xl font-bold">Automatické nastavení zobrazených mapových prvků na základě úrovně přiblížení</h2>
        <div class="p-4 flex flex-wrap gap-4 items-end">
          <div class="flex flex-col">
            <p class="text-md font-medium mb-1">Body pro detail</p>
            <select
            class="border rounded p-2 w-40"
            bind:value={$mapElementsWantedZoom.nodes}
            >
              {#each Array.from({length: numberOfZoomLevels}, (_, i) => i+1) as zoomLevel}
                {#if zoomLevel == $automaticZoomLevel}
                  <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
                {:else}
                  <option value={zoomLevel}>{zoomLevel}</option>
                {/if}
              {/each}
            </select>
          </div>

          <div class="flex flex-col">
          <button 
          class="flex mt-4 justify-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
            on:click={() => setNodesForZoom($mapElementsWantedZoom.nodes)}
          >
          Určit body
          </button>
          </div>
          <div class="flex flex-col">
            <p class="text-md font-medium mb-1">Cesty pro detail</p>
            <select
            class="border rounded p-2 w-40"
            bind:value={$mapElementsWantedZoom.ways}
            >
              {#each Array.from({length: numberOfZoomLevels}, (_, i) => i+1) as zoomLevel}
                {#if zoomLevel == $automaticZoomLevel}
                  <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
                {:else}
                  <option value={zoomLevel}>{zoomLevel}</option>
                {/if}
              {/each}
              </select>
              </div>
              <div class="flex flex-col">

              <button 
              class="flex mt-4  bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                on:click={() => setWaysForZoom($mapElementsWantedZoom.ways)}
              >
              Určit cesty
              </button>
          </div>
          <div class="flex flex-col">
            <p class="text-md font-medium mb-1">Oblasti pro detail</p>
            <select
            class="border rounded p-2 w-40"
            bind:value={$mapElementsWantedZoom.areas}
          >
            {#each Array.from({length: numberOfZoomLevels}, (_, i) => i+1) as zoomLevel}
              {#if zoomLevel == $automaticZoomLevel}
                <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
              {:else}
                <option value={zoomLevel}>{zoomLevel}</option>
              {/if}
            {/each}
          </select>
          </div>  <div class="flex flex-col items-end">
          <button 
              class="flex mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                on:click={() => setAreasForZoom($mapElementsWantedZoom.areas)}
              >
                Určit oblasti
              </button>
            </div>
          </div>
    </div>

    <div class="space-y-4 rounded-lg bg-gray-100 mt-4 ">
      <h2 class="p-2 text-xl font-bold">Body (Ikony a texty)</h2>
      {#each Object.entries($mapNodesElements) as [categoryKey, categoryValue], index}
        <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow border-l-2">
          <div class="flex items-center mb-2">
            <!-- nodes with plot directly (without specific elements) -->
            {#if hasDirectPlot(categoryValue) && hasDirectPlot($mapNodesElements[categoryKey])}

              <div class="inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    class="h-5 w-5 items-center rounded-lg"
                    bind:checked={$mapNodesElements[categoryKey].plot} 
                  />
                
              </div>
              <h3 class="text-lg font-medium text-gray-1000 mr-3 ml-3">{mapValue(nodesKeysNamesMappingCZ, categoryKey)}</h3>

              {#if categoryValue.plot && ('width_scale' in categoryValue || 'text_scale' in categoryValue)}
                <div class="flex flex-wrap items-center ml-4">
                  {#if 'width_scale' in categoryValue}
                  <p class="text-xs mr-2">Násobek výchozí šířky čáry</p>
                    <div class="flex items-center mr-6">
                        <input
                          type="range" 
                          min={multiplierMin}
                          max={multiplierMax}
                          step="0.1" 
                          bind:value={$mapNodesElements[categoryKey].width_scale} 
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <p class="text-xs ml-1 w-6 text-right">{categoryValue.width_scale}</p>
                    </div>
                  {/if}
                  
                  {#if 'text_scale' in categoryValue}
                  <p class="text-xs mr-2">Násobek výchozí velikosti textu</p>
                    <div class="flex items-center">
                        <input 
                          type="range" 
                          min={multiplierMin}
                          max={multiplierMax} 
                          step="0.1" 
                          bind:value={$mapNodesElements[categoryKey].text_scale}
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <span class="text-xs ml-1 w-6 text-right">{categoryValue.text_scale}</span>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>

          <!-- areas with specific elements (e.g place: city) -->
          {#if !hasDirectPlot(categoryValue)}
          <h3 class="text-lg font-medium mb-3 ml-3">{mapValue(nodesKeysNamesMappingCZ, categoryKey)}</h3>
          <div class="flex flex-wrap gap-2 ml-2 mb-3">
              {#each Object.entries(categoryValue) as [subKey, subValue]}
              {#if hasDirectPlot(subValue)}
                <div class="bg-white items-center rounded p-2 border border-gray-200 shadow-sm">
                  <div class="flex justify-normal mb-1">
                        <input 
                          type="checkbox" 
                          class="h-5 w-5 rounded-lg"
                          bind:checked={$mapNodesElements[categoryKey][subKey].plot}
                        >
                      <p class="text-sm ml-2">{mapValue(nodesNamesMappingCZ[categoryKey], subKey)}</p>
                  </div>
                  
                  {#if subValue.plot}
                    <div class="flex flex-col space-y-1 ml-5 mt-1">
                      {#if 'width_scale' in subValue}
                      <p class="text-xs text-gray-600 mr-4">Násobek výchozí velikosti ikony</p>
                      <div class="flex items-center p-1">
                            <input 
                              type="range" 
                              min={multiplierMin}
                              max={multiplierMax}  
                              step="0.1" 
                              bind:value={$mapNodesElements[categoryKey][subKey].width_scale}
                              class="h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                          <p class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right">{subValue.width_scale}</p>
                        </div>
                      {/if}
                      
                      {#if 'text_scale' in subValue}
                      <p class="text-xs text-gray-600 mr-4">Násobek výchozí velikosti textu</p>
                        <div class="flex items-center p-1">
                            <input 
                              type="range" 
                              min={multiplierMin}
                              max={multiplierMax} 
                              step="0.1" 
                              bind:value={$mapNodesElements[categoryKey][subKey].text_scale}
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

    <!-- WAYS -->
    <div class="space-y-4 rounded-lg bg-gray-100 mt-4 ">
      <h2 class="p-2 text-xl font-bold">Cesty</h2>
      {#each Object.entries($mapWaysElements) as [categoryKey, categoryValue], index}
        <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow border-l-2">
          <div class="flex items-center mb-2">
            <!-- ways with plot directly (without specific elements) -->
            {#if hasDirectPlot(categoryValue) && hasDirectPlot($mapWaysElements[categoryKey])}

              <div class="inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    class="h-5 w-5 items-center rounded-lg"
                    bind:checked={$mapWaysElements[categoryKey].plot} 
                  />
                
              </div>
              <h3 class="text-lg font-medium text-gray-1000 mr-3 ml-3">{mapValue(waysKeysNamesMappingCZ, categoryKey)}</h3>

              {#if categoryValue.plot && ('width_scale' in categoryValue || 'text_scale' in categoryValue)}
                <div class="flex flex-wrap items-center ml-4">
                  {#if 'width_scale' in categoryValue}
                  <p class="text-xs mr-2">Násobek výchozí šířky čáry</p>
                    <div class="flex items-center mr-6">
                        <input
                          type="range" 
                          min={multiplierMin}
                          max={multiplierMax}
                          step="0.1" 
                          bind:value={$mapWaysElements[categoryKey].width_scale} 
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <p class="text-xs ml-1 w-6 text-right">{categoryValue.width_scale}</p>
                    </div>
                  {/if}
                  
                  {#if 'text_scale' in categoryValue}
                  <p class="text-xs mr-2">Násobek výchozí velikosti textu</p>
                    <div class="flex items-center">
                        <input 
                          type="range" 
                          min={multiplierMin}
                          max={multiplierMax} 
                          step="0.1" 
                          bind:value={$mapWaysElements[categoryKey].text_scale}
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <span class="text-xs ml-1 w-6 text-right">{categoryValue.text_scale}</span>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>
          <!-- ways with specific elements (e.g highway: primary) -->
          {#if !hasDirectPlot(categoryValue)}
          <h3 class="text-lg font-medium mb-3 ml-3">{mapValue(waysKeysNamesMappingCZ, categoryKey)}</h3>
          <div class="flex flex-wrap gap-2 ml-2 mb-3">
              {#each Object.entries(categoryValue) as [subKey, subValue]}
              {#if hasDirectPlot(subValue)}
                <div class="bg-white items-center rounded p-2 border border-gray-200 shadow-sm">
                  <div class="flex justify-normal mb-1">
                        <input 
                          type="checkbox" 
                          class="h-5 w-5 rounded-lg"
                          bind:checked={$mapWaysElements[categoryKey][subKey].plot}
                        >
                      <p class="text-sm ml-2">{mapValue(waysNamesMappingCZ[categoryKey], subKey)}</p>
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
                              bind:value={$mapWaysElements[categoryKey][subKey].width_scale}
                              class="h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                          <p class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right">{subValue.width_scale}</p>
                        </div>
                      {/if}
                      
                      {#if 'text_scale' in subValue}
                      <p class="text-xs text-gray-600 mr-4">Násobek výchozí velikosti textu</p>
                        <div class="flex items-center p-1">
                            <input 
                              type="range" 
                              min={multiplierMin}
                              max={multiplierMax} 
                              step="0.1" 
                              bind:value={$mapWaysElements[categoryKey][subKey].text_scale}
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

    <!-- AREAS -->
    <div class="space-y-4 rounded-lg bg-gray-100 mt-4 ">
      <h2 class="p-2 text-xl font-bold">Oblasti (Polygony)</h2>
      {#each Object.entries($mapAreasElements) as [categoryKey, categoryValue], index}
        <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow border-l-2">
          <div class="flex items-center mb-2">

            <!-- areas with plot directly (without specific elements) -->
            {#if hasDirectPlot(categoryValue) && hasDirectPlot($mapAreasElements[categoryKey])}

              <div class="inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    class="h-5 w-5 items-center rounded-lg"
                    bind:checked={$mapAreasElements[categoryKey].plot} 
                  />
                
              </div>
              <h3 class="text-lg font-medium text-gray-1000 mr-3 ml-3">{mapValue(areasKeysNamesMappingCZ, categoryKey)}</h3>

              {#if categoryValue.plot && ('width_scale' in categoryValue || 'text_scale' in categoryValue)}
                <div class="flex flex-wrap items-center ml-4">
                  {#if 'width_scale' in categoryValue}
                  <p class="text-xs mr-2">Násobek výchozí šířky okraje</p>
                    <div class="flex items-center mr-6">
                        <input
                          type="range" 
                          min={multiplierMin}
                          max={multiplierMax}
                          step="0.1" 
                          bind:value={$mapAreasElements[categoryKey].width_scale} 
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <p class="text-xs ml-1 w-6 text-right">{categoryValue.width_scale}</p>
                    </div>
                  {/if}
                  
                  {#if 'text_scale' in categoryValue}
                  <p class="text-xs mr-2">Násobek výchozí velikosti textu</p>
                    <div class="flex items-center">
                        <input 
                          type="range" 
                          min={multiplierMin}
                          max={multiplierMax} 
                          step="0.1" 
                          bind:value={$mapAreasElements[categoryKey].text_scale}
                          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <span class="text-xs ml-1 w-6 text-right">{categoryValue.text_scale}</span>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>

          <!-- areas with specific elements (e.g landuse: farmland) -->
          {#if !hasDirectPlot(categoryValue)}
          <h3 class="text-lg font-medium mb-3 ml-3">{mapValue(areasKeysNamesMappingCZ, categoryKey)}</h3>
          <div class="flex flex-wrap gap-2 ml-2 mb-3">
              {#each Object.entries(categoryValue) as [subKey, subValue]}
              {#if hasDirectPlot(subValue)}
                <div class="bg-white items-center rounded p-2 border border-gray-200 shadow-sm">
                  <div class="flex justify-normal mb-1">
                        <input 
                          type="checkbox" 
                          class="h-5 w-5 rounded-lg"
                          bind:checked={$mapAreasElements[categoryKey][subKey].plot}
                        >
                      <p class="text-sm ml-2">{mapValue(areasNamesMappingCZ[categoryKey], subKey)}</p>
                  </div>
                  
                  {#if subValue.plot}
                    <div class="flex flex-col space-y-1 ml-5 mt-1">
                      {#if 'width_scale' in subValue}
                      <p class="text-xs text-gray-600 mr-4">Násobek výchozí šířky okraje</p>
                      <div class="flex items-center p-1">
                            <input 
                              type="range" 
                              min={multiplierMin}
                              max={multiplierMax}  
                              step="0.1" 
                              bind:value={$mapAreasElements[categoryKey][subKey].width_scale}
                              class="h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                          <p class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right">{subValue.width_scale}</p>
                        </div>
                      {/if}
                      
                      {#if 'text_scale' in subValue}
                      <p class="text-xs text-gray-600 mr-4">Násobek výchozí velikosti textu</p>
                        <div class="flex items-center p-1">
                            <input 
                              type="range" 
                              min={multiplierMin}
                              max={multiplierMax} 
                              step="0.1" 
                              bind:value={$mapAreasElements[categoryKey][subKey].text_scale}
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
  </div>