<script lang="ts"> 
    import { mapNodesElements, mapWaysElements, mapAreasElements, automaticZoomLevel, mapElementsZoomDesign,
       mapElementsWantedZoom, peaksFilterSensitivity, minPopulationFilter, wantPlotBridges, wantPlotTunnels,
       wantedMapTheme } from '$lib/stores/mapStore';
    import { mapValue, updateWantedElements, resetPlotSettings } from '$lib/utils/mapElementsUtils';
    import { nodesKeysNamesMappingCZ, nodesNamesMappingCZ, waysKeysNamesMappingCZ, waysNamesMappingCZ,
       areasKeysNamesMappingCZ, areasNamesMappingCZ, numberOfZoomLevels, wantedNodesUpdatesZooms,
       wantedWaysUpdatesZooms, wantedAreasUpdatesZooms } from '$lib/constants';
  import { onMount } from 'svelte'
  import api from '$lib/axios.config'
    const multiplierMin = 0.1
    const multiplierMax = 4
    let displayedCategory = 'nodes'
    function hasDirectPlot(obj: any): obj is MapElementAttributes {
      return obj && typeof obj === 'object' && 'plot' in obj;
    }

    //always available map theme is mapycz
    let avilableMapThemes: string[] = ["mapycz"]
    onMount(() => {
      api.get('/available_map_themes').then((response) => {
        avilableMapThemes = response.data.map_themes
      }).catch((error) => {
        alert('Nepodařilo se načíst dostupné mapové podklady - nastaven výchozí podklad mapycz')
        console.log(error)
      })
    })

    function setNodesForZoom(zoomLevel: number){
      let restartedData = resetPlotSettings($mapNodesElements, 'plot')
      //set to false and iteratativ add default while using
      for (let i =0; i<=zoomLevel; i++){
        restartedData = updateWantedElements(restartedData, wantedNodesUpdatesZooms[i], 'plot')
      }
      $mapNodesElements = restartedData
      $peaksFilterSensitivity = 2.5
      switch(zoomLevel){
        case 7:
          $minPopulationFilter = 250
          break
        case 6:
          $minPopulationFilter = 500
          break
        case 5:
        case 4:
        case 3:
        case 2:
        case 1:
          $minPopulationFilter = 750
          break
        default:
        $minPopulationFilter = 0
          break
      }
      displayedCategory = 'nodes' 
    }

    function setWaysForZoom(zoomLevel: number){
      let restartedData = resetPlotSettings($mapWaysElements, 'plot')

      for (let i =0; i<=zoomLevel; i++){
        restartedData = updateWantedElements(restartedData, wantedWaysUpdatesZooms[i], 'plot')
      }
      $mapWaysElements = restartedData
      $wantPlotTunnels = true
      switch(zoomLevel){
        case 10:
        case 9:
        case 8:
        case 7:
        case 6:
          $wantPlotBridges = true
          break
        default:
          $wantPlotBridges = false
          break
      }
      displayedCategory = 'ways'
    }
   
    function setAreasForZoom(zoomLevel: number){
      let restartedData = resetPlotSettings($mapAreasElements, 'plot')
      for (let i =0; i<=zoomLevel; i++){
        restartedData = updateWantedElements(restartedData, wantedAreasUpdatesZooms[i], 'plot')
      }
      $mapAreasElements = restartedData
      displayedCategory = 'areas'
    }

    $:{
      $mapElementsZoomDesign
     
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
          <p class="text-md font-medium mb-1">Styly mapového podkladu</p>
          <select
          class="border rounded-sm p-2 w-40"
          bind:value={$wantedMapTheme}
        >
          {#each avilableMapThemes as map_themes}
            <option value={map_themes}>{map_themes}</option>
          {/each}
        </select>
        </div>    
        <div class="flex flex-col">
          <p class="text-md font-medium mb-1">Úroveň detailu bodů</p>
          <select
          class="border rounded-sm p-2 w-40"
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
          class="border rounded-sm p-2 w-40"
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
          class="border rounded-sm p-2 w-40"
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
          <p class="text-md font-medium mb-1">Úroveň detailu obecných prvků</p>
          <select
          class="border rounded-sm p-2 w-40"
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
      <h2 class="p-2 text-xl font-bold">Automatické nastavení zobrazených mapových prvků na základě úrovně přiblížení</h2>
        <div class="p-4 flex flex-wrap gap-4 items-end">
          <div class="flex flex-col">
            <p class="text-md font-medium mb-1">Výchozí body pro detail</p>
            <select
            class="border rounded-sm p-2 w-50"
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
            <button 
            class="flex mt-4 justify-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-sm"
              on:click={() => setNodesForZoom($mapElementsWantedZoom.nodes)}
            >
            Nastavit výchozí body
            </button>
          </div>

          <div class="flex flex-col">
            <p class="text-md font-medium mb-1">Výchozí cesty pro detail</p>
            <select
            class="border rounded-sm p-2 w-50"
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
              <button 
              class="flex mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-sm"
                on:click={() => setWaysForZoom($mapElementsWantedZoom.ways)}
              >
              Nastavit výchozí cesty
              </button>
          </div>
          <div class="flex flex-col">
            <p class="text-md font-medium mb-1">Výchozí oblasti pro detail</p>
            <select
            class="border rounded-sm p-2 w-50"
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
          <button 
          class="flex mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-sm"
            on:click={() => setAreasForZoom($mapElementsWantedZoom.areas)}
          >
            Nastavit výchozí oblasti
          </button>
          </div> 
          </div>
    </div>
    <div class="text-md text-center text-gray-500 border-b border-gray-200 dark:text-gray-400 dark:border-gray-700">
      <div class="flex flex-wrap -mb-px">
            <button 
             class= { displayedCategory == "nodes" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
                    "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                    on:click={() => displayedCategory = "nodes"}>
                    Body (Ikony a texty)
            </button>
            <button  class= { displayedCategory == "ways" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
                    "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                    on:click={() => displayedCategory = "ways"}>
                    Cesty
            </button>
            <button class= { displayedCategory == "areas" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
                    "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                    on:click={() => displayedCategory = "areas"}>
                     Oblasti (Polygony)
            </button>
          
       
      </div>
  </div>
  {#if displayedCategory == "nodes"}
    <div class="space-y-4 rounded-lg bg-gray-100 mt-4 ">
      <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
        <h3 class="text-lg font-medium mb-3 ml-3">Obecné nastavení (odstranění některých bodů dle podmínek)</h3>
        <div class="flex flex-wrap gap-2 ml-2 mb-3">
          <div class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs">
            <div class="flex flex-col space-y-1 ml-4">
              <p class="text-sm mr-6">Minimální počet obyvatel vesnic, měst, velkoměst</p>
              <div class="flex mr-6">
                <input
                type="number"
                class="border rounded-sm p-2 w-40"
                bind:value={$minPopulationFilter}/>
              </div> 
            </div>
          </div>
          <div class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs">
            <div class="flex flex-col space-y-1 ml-4">
              <p class="text-sm mr-6">Citlivost filtru na důležitost výškových bodů</p>
              <div class="flex  items-center mr-6">
                <input
                type="range"
                min="0"
                max="7"
                step="0.1"
                bind:value={$peaksFilterSensitivity}
                class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
              <p class="text-sm text-gray-600 ml-4 w-6 text-right">{$peaksFilterSensitivity}</p>
              </div> 
            </div>
          </div>
        </div>
      </div>
      
      {#each Object.entries($mapNodesElements) as [categoryKey, categoryValue], index}
        <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
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
                          class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
                          class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <p class="text-xs ml-1 w-6 text-right">{categoryValue.text_scale}</p>
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
                <div class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs">
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
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
    {:else if displayedCategory == "ways"}
    <!-- WAYS -->
    <div class="space-y-4 rounded-lg bg-gray-100 mt-4 ">
      <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
        <h3 class="text-lg font-medium mb-3 ml-3">Obecné nastavení</h3>
        <div class="flex flex-wrap gap-2 ml-2 mb-3">
          <div class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs">
            <div class="flex justify-normal mb-1">
              <input 
                type="checkbox" 
                class="h-5 w-5 rounded-lg"
                bind:checked={$wantPlotBridges}
              >
            <p class="text-sm ml-2">Vyznačit mosty</p>
            </div> 
          </div>
          <div class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs">
            <div class="flex justify-normal mb-1">
              <input 
                type="checkbox" 
                class="h-5 w-5 rounded-lg"
                bind:checked={$wantPlotTunnels}
              >
            <p class="text-sm ml-2">Vyznačit tunely</p>
            </div> 
          </div>
        </div>
      </div>

      {#each Object.entries($mapWaysElements) as [categoryKey, categoryValue], index}
        <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
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
                          class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
                          class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <p class="text-xs ml-1 w-6 text-right">{categoryValue.text_scale}</p>
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
                <div class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs">
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
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
    {:else}
    <!-- AREAS -->
    <div class="space-y-4 rounded-lg bg-gray-100 mt-4 ">
      {#each Object.entries($mapAreasElements) as [categoryKey, categoryValue], index}
        <div class="ml-4 mr-4 mb-4 p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
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
                          class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
                          class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                      <p class="text-xs ml-1 w-6 text-right">{categoryValue.text_scale}</p>
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
                <div class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs">
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
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
  {/if}
  </div>