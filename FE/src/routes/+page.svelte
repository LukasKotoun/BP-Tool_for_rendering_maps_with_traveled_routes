<script lang="ts">
  import MapElementsManager from "$lib/managers/mapElementsManager.svelte"
  import AreaPaperManager from "$lib/managers/areaPaperManager.svelte";
  import GpxManager from "$lib/managers/gpxManager.svelte";
  import MapGeneratingManager from "$lib/managers/mapGeneratingManager.svelte";
  import { onMount } from 'svelte';
  import api from '$lib/axios.config'
  import { Save, Upload } from '@lucide/svelte';

  import {
  avilableMapThemes,
  avilableMapFiles,
  automaticZoomLevelChangedElements,
  //stores
  mapElementsZoomDesign,
  mapElementsWantedZoom,
  areasId,
  wantedAreas,
  areasPreviewId,
  wantedPreviewAreas,
  paperPreviewDimensions,
  fitPaperSize,
  paperDimensions,
  paperDimensionsRequest,
  automaticZoomLevel,
  wantPlotTunnels,
  wantPlotBridges,
  peaksFilterSensitivity,
  minPopulationFilter,
  mapNodesElements,
  mapWaysElements,
  mapAreasElements,
  selectedMapTheme,
  selectedMapFiles,
  gpxFileGroups,
  gpxStyles
} from '$lib/stores/mapStore';

  let displayedTab = "areaPaper"

   onMount(() => {
      api.get('/available_map_themes').then((response) => {
        $avilableMapThemes = response.data.map_themes
        if($selectedMapTheme == "" && $avilableMapThemes.includes('mapycz')){
          $selectedMapTheme = "mapycz"
        }else if($selectedMapTheme != "" && !$avilableMapThemes.includes($selectedMapTheme)){
          if($avilableMapThemes.length > 0){
            $selectedMapTheme = $avilableMapThemes[0]
        }
      }
      }).catch((error) => {
        alert('Nepodařilo se načíst dostupné mapové podklady - nastaven výchozí podklad mapycz')
        $selectedMapTheme = "mapycz"
        $avilableMapThemes = ["mapycz"]
        console.log(error)
      })

      api.get('/available_osm_files').then((response) => {
        $avilableMapFiles = response.data.osm_files
        if($avilableMapFiles.includes('cz') && $selectedMapFiles.length == 0){
          $selectedMapFiles = ["cz"]
        }else if($selectedMapFiles.length != 0){
          $selectedMapFiles = $selectedMapFiles.filter(file => $avilableMapFiles.includes(file))
        }

      }).catch((error) => {
        alert('Nepodařilo se načíst dostupné mapové soubory - nastaven výchozí soubor pro českou republiku')
        if($selectedMapFiles.length == 0){
          $selectedMapFiles = ["cz"]
        }
        console.log("loading map files error", error)
      })
    })

  function saveToFile() {
    try {
    let gpxFilesGroupsFiltered = Object.fromEntries(
      Object.keys($gpxFileGroups).map(key => [key, []])
    );
    const storeData: StoreData = {
      areasId: $areasId,
      wantedAreas: $wantedAreas,
      areasPreviewId: $areasPreviewId,
      wantedPreviewAreas: $wantedPreviewAreas,
      paperPreviewDimensions: $paperPreviewDimensions,
      fitPaperSize: $fitPaperSize,
      paperDimensions: $paperDimensions,
      paperDimensionsRequest: $paperDimensionsRequest,
      automaticZoomLevel: $automaticZoomLevel,
      wantPlotTunnels: $wantPlotTunnels,
      wantPlotBridges: $wantPlotBridges,
      peaksFilterSensitivity: $peaksFilterSensitivity,
      minPopulationFilter: $minPopulationFilter,
      mapNodesElements: $mapNodesElements,
      mapWaysElements: $mapWaysElements,
      mapAreasElements: $mapAreasElements,
      selectedMapTheme: $selectedMapTheme,
      selectedMapFiles: $selectedMapFiles,
      mapElementsZoomDesign: $mapElementsZoomDesign,
      mapElementsWantedZoom: $mapElementsWantedZoom,
      gpxFileGroups: gpxFilesGroupsFiltered,
      gpxStyles: $gpxStyles
    };

    const jsonData = JSON.stringify(storeData, null, 2);

    const finalFilename = 'map_settings.json';
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = finalFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Error saving store data to JSON:', error);
  }
}

  function loadToStores(data: StoreData){
    if(data.areasId != null){
      $areasId = data.areasId
    }
    if(data.wantedAreas != null){
      $wantedAreas = data.wantedAreas
    }
    if(data.areasPreviewId != null){
      $areasPreviewId = data.areasPreviewId
    }
    if(data.wantedPreviewAreas != null){
      $wantedPreviewAreas = data.wantedPreviewAreas
    }
    if(data.paperPreviewDimensions != null){
      $paperPreviewDimensions = data.paperPreviewDimensions
    }
    if(data.fitPaperSize != null){
      $fitPaperSize = data.fitPaperSize
    }
    if(data.paperDimensions != null){
      $paperDimensions = data.paperDimensions
    }
    if(data.paperDimensionsRequest != null){
      $paperDimensionsRequest = data.paperDimensionsRequest
    }
    if(data.automaticZoomLevel != null){
      $automaticZoomLevel = data.automaticZoomLevel
    }
    if(data.wantPlotTunnels != null){
      $wantPlotTunnels = data.wantPlotTunnels
    }
    if(data.wantPlotBridges != null){
      $wantPlotBridges = data.wantPlotBridges
    }
    if(data.peaksFilterSensitivity != null){
      $peaksFilterSensitivity = data.peaksFilterSensitivity
    }
    if(data.minPopulationFilter != null){
      $minPopulationFilter = data.minPopulationFilter
    }
    if(data.mapNodesElements != null){
      $mapNodesElements = data.mapNodesElements
    }
    if(data.mapWaysElements != null){
      $mapWaysElements = data.mapWaysElements
    }
    if(data.mapAreasElements != null){
      $mapAreasElements = data.mapAreasElements
    }
    if(data.selectedMapTheme != null){ 
      //check if selectedMapTheme is in available map themes
      if($avilableMapThemes.includes(data.selectedMapTheme)){
        $selectedMapTheme = data.selectedMapTheme
      }else{
        alert("Mapový podklad z uloženého nastavení není dostupný. Nastaven výchozí podklad")
      }
    }
    if(data.selectedMapFiles != null){
      //check if selectedMapFiles are in available map files
      const selectedMapFilesFiltered = data.selectedMapFiles.filter(file => $avilableMapFiles.includes(file))
      if(selectedMapFilesFiltered.length == data.selectedMapFiles.length){
        $selectedMapFiles = data.selectedMapFiles
      }else{
        alert("Některé mapové data z uloženého nastavení nejsou dostupné, byly použity pouze dostupná data nebo výchozí data")
        if(selectedMapFilesFiltered.length > 0){
          $selectedMapFiles = selectedMapFilesFiltered
        }
      }
    }
    if(data.mapElementsZoomDesign != null){
      $mapElementsZoomDesign = data.mapElementsZoomDesign
    }
    if(data.mapElementsWantedZoom != null){
      $mapElementsWantedZoom = data.mapElementsWantedZoom
    }
    if(data.gpxFileGroups != null){
      $gpxFileGroups = data.gpxFileGroups
    }
    if(data.gpxStyles != null){
      $gpxStyles = data.gpxStyles
    }
  }

  function loadJsonObjectFromFile(event: Event) {
    const input = event.target as HTMLInputElement;
    const files = input.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    try {
      const reader = new FileReader();
      
      reader.onload = async (e) => {
        try {
          const content = e.target?.result as string;
          loadToStores(JSON.parse(content));
        } catch (error) {
          console.error("Json parsing error", error);
          alert("Nepodařilo se načíst nastavení ze souboru. Zkontrolujte formát JSON.");
        } finally {
        }
      };
      reader.onerror = () => {
        alert('Error reading file');
      };
      
      reader.readAsText(file);
    } catch (error) {
      alert("Chyba při načítání souboru");
    }
    input.value = '';
  }
  
</script>
<div class="container mx-auto p-4">
  <div class="flex space-x-2 justify-end mb-4">
    <button 
      class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
      on:click={saveToFile}
    >
      <div class="flex items-center">
        <Save class="w-5 h-5 mr-2" />
        Uložit nastavení
      </div>
    </button>
    <button 
  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
  on:click={() => document.getElementById('file-input').click()}
>
  <div class="flex items-center">
    <Upload class="w-5 h-5 mr-2" />
    Nahrát nastavení
  </div>
</button>

<input 
  id="file-input" 
  type="file" 
  accept=".json,application/json" 
  on:change={loadJsonObjectFromFile} 
  class="hidden"
/>
  </div>
  <div class="border-b border-gray-200 dark:border-gray-700">
    <div class="flex flex-wrap -mb-px">
      <button 
        class= { displayedTab == "areaPaper" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
              "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300"}
              on:click={() => displayedTab = "areaPaper"}>
              Nastavení oblasti a papíru
      </button>
      <button 
          class= { displayedTab == "gpx" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
                  "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300"}
          class:dark:text-gray-400={displayedTab == "areaPaper"}
                  on:click={() => displayedTab = "gpx"}>
                  Nastavení a nahrání tras (gpx)
      </button>
      <button  class= { displayedTab == "mapElements" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
              "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
              class:dark:text-gray-400={displayedTab == "areaPaper" || displayedTab == "gpx"}
              on:click={() => {displayedTab = "mapElements"; $automaticZoomLevelChangedElements = false}}>
              {#if $automaticZoomLevelChangedElements}
                <p>Nastavení mapových prvků <span class="text-red-500">(1)</span></p>
              {:else}
                Nastavení mapových prvků
              {/if}
      </button>
      <button  class= { displayedTab == "generating" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
              "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
               class:dark:text-gray-400={displayedTab == "areaPaper" || displayedTab == "gpx" || displayedTab == "mapElements"}
              on:click={() => displayedTab = "generating"}>
              Vygenerování mapy
      </button>
    </div>   
  </div>

  {#if displayedTab == "areaPaper"}
    <AreaPaperManager/>
  {:else if displayedTab == "gpx"}
    <GpxManager/>
  {:else if displayedTab == "mapElements"}
  <MapElementsManager/>
  {:else if displayedTab == "generating"}
    <MapGeneratingManager/>
  {/if}
</div>
