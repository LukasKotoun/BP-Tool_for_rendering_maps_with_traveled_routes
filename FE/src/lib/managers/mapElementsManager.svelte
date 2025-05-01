<script lang="ts">
  import InfoToolTip from "$lib/components/infoToolTip.svelte";
  import {
    avilableMapThemes,
    displayedElementsCategory,
  } from "$lib/stores/frontendStore";
  import {
    mapValue,
    updateWantedElements,
    resetPlotSettings,
  } from "$lib/utils/mapElementsUtils";
  import {
    mapNodesElements,
    mapWaysElements,
    mapAreasElements,
    automaticZoomLevel,
    mapElementsZoomDesign,
    mapElementsWantedZoom,
    peaksFilterSensitivity,
    minPopulationFilter,
    wantPlotBridges,
    wantPlotTunnels,
    selectedMapTheme,
  } from "$lib/stores/mapStore";
  import {
    nodesKeysNamesMappingCZ,
    nodesNamesMappingCZ,
    waysKeysNamesMappingCZ,
    waysNamesMappingCZ,
    areasKeysNamesMappingCZ,
    areasNamesMappingCZ,
    numberOfZoomLevels,
    wantedNodesUpdatesZooms,
    wantedWaysUpdatesZooms,
    wantedAreasUpdatesZooms,
    nodesMapElements,
    waysMapElements,
    areasMapElements,
  } from "$lib/constants";

  const multiplierMin = 0.1;
  const multiplierStep = 0.05;
  const multiplierMax = 4;

  function hasDirectPlot(obj: any): obj is MapElementAttributes {
    return obj && typeof obj === "object" && "plot" in obj;
  }
  function resetNodesToDefault() {
    // Reset the nodes to their original state with all changed sizes
    $mapNodesElements = JSON.parse(JSON.stringify(nodesMapElements));
    $minPopulationFilter = 0;
    $peaksFilterSensitivity = 2.5;
  }
  function resetWaysToDefault() {
    // Reset the ways to their original state with all changed sizes
    $mapWaysElements = JSON.parse(JSON.stringify(waysMapElements));
    $wantPlotBridges = false;
    $wantPlotTunnels = true;
  }
  function resetAreasToDefault() {
    // Reset the areas to their original state with all changed sizes
    $mapAreasElements = JSON.parse(JSON.stringify(areasMapElements));
  }

  function setNodesForZoom(zoomLevel: number) {
    let restartedData = resetPlotSettings($mapNodesElements);
    //set to false and iteratativ add default while using
    for (let i = 0; i <= zoomLevel; i++) {
      restartedData = updateWantedElements(
        restartedData,
        wantedNodesUpdatesZooms[i]
      );
    }
    $mapNodesElements = restartedData;
    $peaksFilterSensitivity = 2.5;
    // default values for zoom levels
    switch (zoomLevel) {
      case 5:
        $minPopulationFilter = 250;
        break;
      case 4:
        $minPopulationFilter = 500;
        break;
      case 3:
        $minPopulationFilter = 750;
        break;
      case 2:
      case 1:
        $minPopulationFilter = 1000;
        break;
      default:
        $minPopulationFilter = 0;
        break;
    }
    $displayedElementsCategory = "nodes";
  }

  function setWaysForZoom(zoomLevel: number) {
    let restartedData = resetPlotSettings($mapWaysElements);

    for (let i = 0; i <= zoomLevel; i++) {
      restartedData = updateWantedElements(
        restartedData,
        wantedWaysUpdatesZooms[i]
      );
    }
    $mapWaysElements = restartedData;
    $wantPlotTunnels = true;
    // default values for zoom levels
    switch (zoomLevel) {
      case 10:
      case 9:
      case 8:
      case 7:
      case 6:
        $wantPlotBridges = true;
        break;
      default:
        $wantPlotBridges = false;
        break;
    }
    $displayedElementsCategory = "ways";
  }

  function setAreasForZoom(zoomLevel: number) {
    let restartedData = resetPlotSettings($mapAreasElements);
    for (let i = 0; i <= zoomLevel; i++) {
      restartedData = updateWantedElements(
        restartedData,
        wantedAreasUpdatesZooms[i]
      );
    }
    $mapAreasElements = restartedData;
    $displayedElementsCategory = "areas";
  }
</script>

<div class="container mx-auto p-4">
  <div class="space-y-4 rounded-lg bg-gray-100">
    <h1 class="text-xl p-4 font-bold">
      Vzhled na základě úrovně přiblížení <InfoToolTip
        text="Při nastavení jiné oblasti nebo jiného papíru se změní úroveň detailu zpět na automatickou."
        position="right"
        size="sm"
      />
    </h1>
    <div class="p-4 flex flex-wrap gap-4 items-start">
      <div class="flex flex-col">
        <p class="text-md font-medium mb-1">
          Styly mapového podkladu <InfoToolTip
            text="Podklad (style) podle kterého bude mapa vypadat. 
            Vzhledy se také upravují podle úrovně detailu."
            position="right"
            size="sm"
          />
        </p>
        {#if $avilableMapThemes.length == 0}
          <p>Žádné načtené mapového podklady</p>
        {:else}
          <select
            class="border rounded-sm p-2 w-40"
            bind:value={$selectedMapTheme}
          >
            {#each $avilableMapThemes as map_themes}
              <option value={map_themes}>{map_themes}</option>
            {/each}
          </select>
        {/if}
      </div>
      <div class="flex flex-col">
        <p class="text-md font-medium mb-1">
          Úroveň detailu bodů <InfoToolTip
            text="Úroveň podle které bude nastaven vzhled bodů, např. barvy, velikosti okrajů...
            (Každá úroveň detailu má odpovídající vzhled)"
            position="right"
            size="sm"
          />
        </p>
        <select
          class="border rounded-sm p-2 w-40"
          bind:value={$mapElementsZoomDesign.nodes}
        >
          {#each Array.from({ length: numberOfZoomLevels }, (_, i) => i + 1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
      </div>

      <div class="flex flex-col">
        <p class="text-md font-medium mb-1">
          Úroveň detailu cest <InfoToolTip
            text="Úroveň podle které bude nastaven vzhled cest, např. barvy, velikosti okrajů...
            (Každá úroveň detailu má odpovídající vzhled)"
            position="right"
            size="sm"
          />
        </p>
        <select
          class="border rounded-sm p-2 w-40"
          bind:value={$mapElementsZoomDesign.ways}
        >
          {#each Array.from({ length: numberOfZoomLevels }, (_, i) => i + 1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
      </div>

      <div class="flex flex-col">
        <p class="text-md font-medium mb-1">
          Úroveň detailu oblastí <InfoToolTip
            text="Úroveň podle které bude nastaven vzhled oblastí, např. barvy, velikosti okrajů...
            (Každá úroveň detailu má odpovídající vzhled)"
            position="right"
            size="sm"
          />
        </p>
        <select
          class="border rounded-sm p-2 w-40"
          bind:value={$mapElementsZoomDesign.areas}
        >
          {#each Array.from({ length: numberOfZoomLevels }, (_, i) => i + 1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
      </div>
      <div class="flex flex-col">
        <p class="text-md font-medium mb-1">
          Úroveň detailu obecných prvků <InfoToolTip
            text="Úroveň podle které bude nastaven vzhled ostatních prvků, např. barva podkladu a oceanů..."
            position="right"
            size="sm"
          />
        </p>
        <select
          class="border rounded-sm p-2 w-40"
          bind:value={$mapElementsZoomDesign.general}
        >
          {#each Array.from({ length: numberOfZoomLevels }, (_, i) => i + 1) as zoomLevel}
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
  <div
    class="text-md text-center text-gray-400 border-b border-gray-700"
  >
    <div class="flex flex-wrap -mb-px">
      <button
        class={$displayedElementsCategory == "nodes"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg "
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
        on:click={() => ($displayedElementsCategory = "nodes")}
      >
        Body (Ikony a texty)
      </button>
      <button
        class={$displayedElementsCategory == "ways"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg"
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
        on:click={() => ($displayedElementsCategory = "ways")}
      >
        Cesty
      </button>
      <button
        class={$displayedElementsCategory == "areas"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg"
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
        on:click={() => ($displayedElementsCategory = "areas")}
      >
        Oblasti (Polygony)
      </button>
    </div>
  </div>
  {#if $displayedElementsCategory == "nodes"}
    <div class="space-y-4 rounded-lg bg-gray-100">
      <div class="flex flex-col p-4">
        <p class="text-md font-medium mb-1">
          Úroveň detailu bodů <InfoToolTip
            text="Nastaví body, které mají být zobrazeny na mapě pro zvolenou úrovně detailu."
            position="right"
            size="sm"
          />
        </p>
        <select
          class="border rounded-sm p-2 w-50"
          bind:value={$mapElementsWantedZoom.nodes}
        >
          {#each Array.from({ length: numberOfZoomLevels }, (_, i) => i + 1) as zoomLevel}
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
          Vybrat prvky k vykreslení dle vybraného detailu
        </button>
      </div>
    </div>
    <div class="space-y-4 rounded-lg p-4 bg-gray-100 mt-4">
      <div class="flex justify-end">
        <button
          class="bg-red-500 text-white rounded hover:bg-red-600 transition-colors px-4 py-2"
          on:click={() => {
            const confirmed = window.confirm(
              "Opravdu chcete obnovit vykreslované body a jejich velikosti na původní nastavení?"
            );
            if (!confirmed) {
              return;
            } else {
              resetNodesToDefault();
            }
          }}
        >
          Obnovit body na výchozí nastavení
        </button>
      </div>
      <div class="bg-gray-50 p-4 rounded-md shadow-sm border-l-2">
        <h3 class="text-lg font-medium mb-3 ml-3">
          Obecné nastavení (odstranění některých bodů dle podmínek)
        </h3>
        <div class="flex flex-wrap gap-2 ml-2 mb-3">
          <div
            class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs"
          >
            <div class="flex flex-col space-y-1 ml-4">
              <p class="text-sm mr-6">
                Minimální počet obyvatel vesnic, měst, velkoměst <InfoToolTip
                  text="Profiltruje zobrazované názvy obcí pro čistší vzhled mapy. 
                Pokud je nezadáno nic nebo nula, tak se filtr neaplikuje."
                  position="right"
                  size="sm"
                />
              </p>
              <div class="flex mr-6">
                <input
                  min="0"
                  step="25"
                  type="number"
                  class="border rounded-sm p-2 w-40"
                  bind:value={$minPopulationFilter}
                />
              </div>
            </div>
          </div>
          <div
            class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs"
          >
            <div class="flex flex-col space-y-1 ml-4">
              <p class="text-sm mr-6">
                Citlivost filtru na důležitost výškových bodů <InfoToolTip
                  text="Zobrazí pouze duležité výškové body pro čistčí vzhled mapy. Čím větší citlivost, tím míň bodů.
                Pokud je zadána nula, tak se filtr neaplikuje."
                  position="right"
                  size="sm"
                />
              </p>
              <div class="flex items-center mr-6">
                <input
                  type="range"
                  min="0"
                  max="10"
                  step={multiplierStep}
                  bind:value={$peaksFilterSensitivity}
                  class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <p class="text-sm text-gray-600 ml-4 w-6 text-right">
                  {$peaksFilterSensitivity}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {#each Object.entries($mapNodesElements) as [categoryKey, categoryValue], index}
        <div class="p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
          <div class="flex items-center mb-2">
            <!-- nodes with plot directly (without specific elements) -->
            {#if hasDirectPlot(categoryValue) && hasDirectPlot($mapNodesElements[categoryKey])}
              <div class="inline-flex items-center">
                <input
                  id="checkbox-nodes-direct-{categoryKey}"
                  type="checkbox"
                  class="h-5 w-5 items-center rounded-lg cursor-pointer"
                  bind:checked={$mapNodesElements[categoryKey].plot}
                />
                <label
                  class="text-lg font-medium text-gray-1000 mr-3 ml-3 cursor-pointer"
                  for="checkbox-nodes-direct-{categoryKey}"
                >
                  {mapValue(nodesKeysNamesMappingCZ, categoryKey)}
                </label>
              </div>

              {#if categoryValue.plot && ("width_scale" in categoryValue || "text_scale" in categoryValue)}
                <div class="flex flex-wrap items-center ml-4">
                  {#if "width_scale" in categoryValue}
                    <p class="text-xs mr-2">Násobek výchozí šířky čáry</p>
                    <div class="flex items-center mr-6">
                      <input
                        type="range"
                        min={multiplierMin}
                        max={multiplierMax}
                        step={multiplierStep}
                        bind:value={$mapNodesElements[categoryKey].width_scale}
                        class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      />
                      <p class="text-xs ml-1 w-6 text-right">
                        {categoryValue.width_scale}
                      </p>
                    </div>
                  {/if}

                  {#if "text_scale" in categoryValue}
                    <p class="text-xs mr-2">Násobek výchozí velikosti textu</p>
                    <div class="flex items-center">
                      <input
                        type="range"
                        min={multiplierMin}
                        max={multiplierMax}
                        step={multiplierStep}
                        bind:value={$mapNodesElements[categoryKey].text_scale}
                        class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      />
                      <p class="text-xs ml-1 w-6 text-right">
                        {categoryValue.text_scale}
                      </p>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>

          <!-- areas with specific elements (e.g place: city) -->
          {#if !hasDirectPlot(categoryValue)}
            <h3 class="text-lg font-medium mb-3 ml-3">
              {mapValue(nodesKeysNamesMappingCZ, categoryKey)}
            </h3>
            <div class="flex flex-wrap gap-2 ml-2 mb-3">
              {#each Object.entries(categoryValue) as [subKey, subValue]}
                {#if hasDirectPlot(subValue)}
                  <div
                    class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs"
                  >
                    <div class="flex justify-normal mb-1">
                      <input
                        id="checkbox-nodes-nondirect-{categoryKey}-{subKey}"
                        type="checkbox"
                        class="h-5 w-5 rounded-lg cursor-pointer"
                        bind:checked={
                          $mapNodesElements[categoryKey][subKey].plot
                        }
                      />
                      <label
                        class="text-sm ml-2 cursor-pointer"
                        for="checkbox-nodes-nondirect-{categoryKey}-{subKey}"
                      >
                        {mapValue(nodesNamesMappingCZ[categoryKey], subKey)}
                      </label>
                    </div>

                    {#if subValue.plot}
                      <div class="flex flex-col space-y-1 ml-5 mt-1">
                        {#if "width_scale" in subValue}
                          <p class="text-xs text-gray-600 mr-4">
                            Násobek výchozí velikosti ikony
                          </p>
                          <div class="flex items-center p-1">
                            <input
                              type="range"
                              min={multiplierMin}
                              max={multiplierMax}
                              step={multiplierStep}
                              bind:value={
                                $mapNodesElements[categoryKey][subKey]
                                  .width_scale
                              }
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            />
                            <p
                              class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right"
                            >
                              {subValue.width_scale}
                            </p>
                          </div>
                        {/if}

                        {#if "text_scale" in subValue}
                          <p class="text-xs text-gray-600 mr-4">
                            Násobek výchozí velikosti textu
                          </p>
                          <div class="flex items-center p-1">
                            <input
                              type="range"
                              min={multiplierMin}
                              max={multiplierMax}
                              step={multiplierStep}
                              bind:value={
                                $mapNodesElements[categoryKey][subKey]
                                  .text_scale
                              }
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            />
                            <p
                              class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right"
                            >
                              {subValue.text_scale}
                            </p>
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
  {:else if $displayedElementsCategory == "ways"}
    <!-- WAYS -->
    <div class="space-y-4 rounded-lg bg-gray-100">
      <div class="flex flex-col p-4">
        <p class="text-md font-medium mb-1">
          Úroveň detailu cest <InfoToolTip
            text="Nastaví cesty, které mají být zobrazeny na mapě pro zvolenou úrovně detailu."
            position="right"
            size="sm"
          />
        </p>
        <select
          class="border rounded-sm p-2 w-50"
          bind:value={$mapElementsWantedZoom.ways}
        >
          {#each Array.from({ length: numberOfZoomLevels }, (_, i) => i + 1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
        <button
          class="flex mt-4 justify-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-sm"
          on:click={() => setWaysForZoom($mapElementsWantedZoom.ways)}
        >
          Vybrat prvky k vykreslení dle vybraného detailu
        </button>
      </div>
    </div>
    <div class="space-y-4 p-4 rounded-lg bg-gray-100 mt-4">
      <div class="flex justify-end">
        <button
          class="bg-red-500 text-white rounded hover:bg-red-600 transition-colors px-4 py-2"
          on:click={() => {
            const confirmed = window.confirm(
              "Opravdu chcete obnovit vykreslované cesty a jejich velikosti na původní nastavení?"
            );
            if (!confirmed) {
              return;
            } else {
              resetWaysToDefault();
            }
          }}
        >
          Obnovit cesty na výchozí nastavení
        </button>
      </div>
      <div class="bg-gray-50 p-4 rounded-md shadow-sm border-l-2">
        <h3 class="text-lg font-medium mb-3 ml-3">Obecné nastavení</h3>
        <div class="flex flex-wrap gap-2 ml-2 mb-3">
          <div
            class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs"
          >
            <div class="flex justify-normal mb-1">
              <input
                type="checkbox"
                id="checkbox-ways-general-bridges"
                class="h-5 w-5 rounded-lg cursor-pointer"
                bind:checked={$wantPlotBridges}
              />
              <label
                for="checkbox-ways-general-bridges"
                class="text-sm ml-2 cursor-pointer"
              >
                Vyznačit mosty <InfoToolTip
                  text="Vyznačí mosty pomocí okrajů a správného (reálného) vrstvení cest. 
            Změna od automatického nastavení není doporučena a může výrazně zhoršit vzhled mapy!"
                  position="right"
                  size="sm"
                />
              </label>
            </div>
          </div>
          <div
            class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs"
          >
            <div class="flex justify-normal mb-1">
              <input
                type="checkbox"
                id="checkbox-ways-general-tunnels"
                class="h-5 w-5 rounded-lg cursor-pointer"
                bind:checked={$wantPlotTunnels}
              />
              <label
                for="checkbox-ways-general-tunnels"
                class="text-sm ml-2 cursor-pointer"
              >
                Vyznačit tunely <InfoToolTip
                  text="Pokud není zvoleno, tunely se budou vykreslovat jako normální cesty."
                  position="right"
                  size="sm"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      {#each Object.entries($mapWaysElements) as [categoryKey, categoryValue], index}
        <div class="p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
          <div class="flex items-center mb-2">
            <!-- ways with plot directly (without specific elements) -->
            {#if hasDirectPlot(categoryValue) && hasDirectPlot($mapWaysElements[categoryKey])}
              <div class="inline-flex items-center">
                <input
                  id="checkbox-ways-direct-{categoryKey}"
                  type="checkbox"
                  class="h-5 w-5 items-center rounded-lg cursor-pointer"
                  bind:checked={$mapWaysElements[categoryKey].plot}
                />
              </div>
              <label
                class="text-lg font-medium text-gray-1000 mr-3 ml-3 cursor-pointer"
                for="checkbox-ways-direct-{categoryKey}"
              >
                {mapValue(waysKeysNamesMappingCZ, categoryKey)}
              </label>

              {#if categoryValue.plot && ("width_scale" in categoryValue || "text_scale" in categoryValue)}
                <div class="flex flex-wrap items-center ml-4">
                  {#if "width_scale" in categoryValue}
                    <p class="text-xs mr-2">Násobek výchozí šířky čáry</p>
                    <div class="flex items-center mr-6">
                      <input
                        type="range"
                        min={multiplierMin}
                        max={multiplierMax}
                        step={multiplierStep}
                        bind:value={$mapWaysElements[categoryKey].width_scale}
                        class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      />
                      <p class="text-xs ml-1 w-6 text-right">
                        {categoryValue.width_scale}
                      </p>
                    </div>
                  {/if}

                  {#if "text_scale" in categoryValue}
                    <p class="text-xs mr-2">Násobek výchozí velikosti textu</p>
                    <div class="flex items-center">
                      <input
                        type="range"
                        min={multiplierMin}
                        max={multiplierMax}
                        step={multiplierStep}
                        bind:value={$mapWaysElements[categoryKey].text_scale}
                        class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      />
                      <p class="text-xs ml-1 w-6 text-right">
                        {categoryValue.text_scale}
                      </p>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>
          <!-- ways with specific elements (e.g highway: primary) -->
          {#if !hasDirectPlot(categoryValue)}
            <h3 class="text-lg font-medium mb-3 ml-3">
              {mapValue(waysKeysNamesMappingCZ, categoryKey)}
            </h3>
            <div class="flex flex-wrap gap-2 ml-2 mb-3">
              {#each Object.entries(categoryValue) as [subKey, subValue]}
                {#if hasDirectPlot(subValue)}
                  <div
                    class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs"
                  >
                    <div class="flex justify-normal mb-1">
                      <input
                        id="checkbox-ways-nondirect-{categoryKey}-{subKey}"
                        type="checkbox"
                        class="h-5 w-5 rounded-lg cursor-pointer"
                        bind:checked={
                          $mapWaysElements[categoryKey][subKey].plot
                        }
                      />
                      <label
                        class="text-sm ml-2 cursor-pointer"
                        for="checkbox-ways-nondirect-{categoryKey}-{subKey}"
                      >
                        {mapValue(waysNamesMappingCZ[categoryKey], subKey)}
                      </label>
                    </div>

                    {#if subValue.plot}
                      <div class="flex flex-col space-y-1 ml-5 mt-1">
                        {#if "width_scale" in subValue}
                          <p class="text-xs text-gray-600 mr-4">
                            Násobek výchozí šířky
                          </p>
                          <div class="flex items-center p-1">
                            <input
                              type="range"
                              min={multiplierMin}
                              max={multiplierMax}
                              step={multiplierStep}
                              bind:value={
                                $mapWaysElements[categoryKey][subKey]
                                  .width_scale
                              }
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            />
                            <p
                              class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right"
                            >
                              {subValue.width_scale}
                            </p>
                          </div>
                        {/if}

                        {#if "text_scale" in subValue}
                          <p class="text-xs text-gray-600 mr-4">
                            Násobek výchozí velikosti textu
                          </p>
                          <div class="flex items-center p-1">
                            <input
                              type="range"
                              min={multiplierMin}
                              max={multiplierMax}
                              step={multiplierStep}
                              bind:value={
                                $mapWaysElements[categoryKey][subKey].text_scale
                              }
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            />
                            <p
                              class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right"
                            >
                              {subValue.text_scale}
                            </p>
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
    <div class="space-y-4 rounded-lg bg-gray-100">
      <div class="flex flex-col p-4">
        <p class="text-md font-medium mb-1">
          Úroveň detailu oblastí <InfoToolTip
            text="Nastaví oblasti, které mají být zobrazeny na mapě pro zvolenou úrovně detailu."
            position="right"
            size="sm"
          />
        </p>
        <select
          class="border rounded-sm p-2 w-50"
          bind:value={$mapElementsWantedZoom.areas}
        >
          {#each Array.from({ length: numberOfZoomLevels }, (_, i) => i + 1) as zoomLevel}
            {#if zoomLevel == $automaticZoomLevel}
              <option value={zoomLevel}>{zoomLevel} (Automaticky)</option>
            {:else}
              <option value={zoomLevel}>{zoomLevel}</option>
            {/if}
          {/each}
        </select>
        <button
          class="flex mt-4 justify-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-sm"
          on:click={() => setAreasForZoom($mapElementsWantedZoom.areas)}
        >
          Vybrat prvky k vykreslení dle vybraného detailu
        </button>
      </div>
    </div>
    <div class="space-y-4 p-4 rounded-lg bg-gray-100 mt-4">
      <div class="flex justify-end">
        <button
          class="bg-red-500 text-white rounded hover:bg-red-600 transition-colors px-4 py-2"
          on:click={() => {
            const confirmed = window.confirm(
              "Opravdu chcete obnovit vykreslované oblasti a jejich velikosti na původní nastavení?"
            );
            if (!confirmed) {
              return;
            } else {
              resetAreasToDefault();
            }
          }}
        >
          Obnovit oblasti na výchozí nastavení
        </button>
      </div>
      {#each Object.entries($mapAreasElements) as [categoryKey, categoryValue], index}
        <div class="p-4 bg-gray-50 rounded-md shadow-sm border-l-2">
          <div class="flex items-center mb-2">
            <!-- areas with plot directly (without specific elements) -->
            {#if hasDirectPlot(categoryValue) && hasDirectPlot($mapAreasElements[categoryKey])}
              <div class="inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  id="checkbox-areas-direct-{categoryKey}"
                  class="h-5 w-5 items-center rounded-lg cursor-pointer"
                  bind:checked={$mapAreasElements[categoryKey].plot}
                />
                <label
                  class="text-lg font-medium text-gray-1000 mr-3 ml-3 cursor-pointer"
                  for="checkbox-areas-direct-{categoryKey}"
                >
                  {mapValue(areasKeysNamesMappingCZ, categoryKey)}
                </label>
              </div>

              {#if categoryValue.plot && ("width_scale" in categoryValue || "text_scale" in categoryValue)}
                <div class="flex flex-wrap items-center ml-4">
                  {#if "width_scale" in categoryValue}
                    <p class="text-xs mr-2">Násobek výchozí šířky okraje</p>
                    <div class="flex items-center mr-6">
                      <input
                        type="range"
                        min={multiplierMin}
                        max={multiplierMax}
                        step={multiplierStep}
                        bind:value={$mapAreasElements[categoryKey].width_scale}
                        class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      />
                      <p class="text-xs ml-1 w-6 text-right">
                        {categoryValue.width_scale}
                      </p>
                    </div>
                  {/if}

                  {#if "text_scale" in categoryValue}
                    <p class="text-xs mr-2">Násobek výchozí velikosti textu</p>
                    <div class="flex items-center">
                      <input
                        type="range"
                        min={multiplierMin}
                        max={multiplierMax}
                        step={multiplierStep}
                        bind:value={$mapAreasElements[categoryKey].text_scale}
                        class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      />
                      <p class="text-xs ml-1 w-6 text-right">
                        {categoryValue.text_scale}
                      </p>
                    </div>
                  {/if}
                </div>
              {/if}
            {/if}
          </div>

          <!-- areas with specific elements (e.g landuse: farmland) -->
          {#if !hasDirectPlot(categoryValue)}
            <h3 class="text-lg font-medium mb-3 ml-3">
              {mapValue(areasKeysNamesMappingCZ, categoryKey)}
            </h3>
            <div class="flex flex-wrap gap-2 ml-2 mb-3">
              {#each Object.entries(categoryValue) as [subKey, subValue]}
                {#if hasDirectPlot(subValue)}
                  <div
                    class="bg-white items-center rounded-sm p-2 border border-gray-200 shadow-xs"
                  >
                    <div class="flex justify-normal mb-1">
                      <input
                        id="checkbox-areas-nondirect-{categoryKey}-{subKey}"
                        type="checkbox"
                        class="h-5 w-5 rounded-lg cursor-pointer"
                        bind:checked={
                          $mapAreasElements[categoryKey][subKey].plot
                        }
                      />
                      <label
                        class="text-sm ml-2 cursor-pointer"
                        for="checkbox-areas-nondirect-{categoryKey}-{subKey}"
                      >
                        {mapValue(areasNamesMappingCZ[categoryKey], subKey)}
                      </label>
                    </div>

                    {#if subValue.plot}
                      <div class="flex flex-col space-y-1 ml-5 mt-1">
                        {#if "width_scale" in subValue}
                          <p class="text-xs text-gray-600 mr-4">
                            Násobek výchozí šířky okraje
                          </p>
                          <div class="flex items-center p-1">
                            <input
                              type="range"
                              min={multiplierMin}
                              max={multiplierMax}
                              step={multiplierStep}
                              bind:value={
                                $mapAreasElements[categoryKey][subKey]
                                  .width_scale
                              }
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            />
                            <p
                              class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right"
                            >
                              {subValue.width_scale}
                            </p>
                          </div>
                        {/if}

                        {#if "text_scale" in subValue}
                          <p class="text-xs text-gray-600 mr-4">
                            Násobek výchozí velikosti textu
                          </p>
                          <div class="flex items-center p-1">
                            <input
                              type="range"
                              min={multiplierMin}
                              max={multiplierMax}
                              step={multiplierStep}
                              bind:value={
                                $mapAreasElements[categoryKey][subKey]
                                  .text_scale
                              }
                              class="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                            />
                            <p
                              class="text-xs text-gray-600 ml-1 mr-1 w-6 text-right"
                            >
                              {subValue.text_scale}
                            </p>
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
