<script lang="ts">
  import MapElementsManager from "$lib/managers/mapElementsManager.svelte"
  import AreaPaperManager from "$lib/managers/areaPaperManager.svelte";
  import GpxManager from "$lib/managers/gpxManager.svelte";
  import MapGeneratingManager from "$lib/managers/mapGeneratingManager.svelte";
  import { onMount } from 'svelte';
  import api from '$lib/axios.config'
  import { avilableMapThemes, selectedMapTheme, avilableMapFiles, selectedMapFiles } from '$lib/stores/mapStore'
  let displayedTab = "generating"
  // add loading and storing to file - if loading check for available files and themes (if exists)
  // add it to try catch and in catch restart everything with default values

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
        console.log(error)
      })
    })
</script>
<div class="container mx-auto p-4">

  <div class="flex flex-wrap -mb-px">
    <button 
    class= { displayedTab == "areaPaper" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
            "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
            on:click={() => displayedTab = "areaPaper"}>
            Nastavení oblasti a papíru
    </button>
    <button 
    class= { displayedTab == "gpx" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
            "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
            on:click={() => displayedTab = "gpx"}>
            Nastavení a nahrání tras (gpx)
    </button>
    <button  class= { displayedTab == "mapElements" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
            "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
            on:click={() => displayedTab = "mapElements"}>
            Nastavení mapových prvků
    </button>
    <button  class= { displayedTab == "generating" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
            "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
            on:click={() => displayedTab = "generating"}>
            Vygenerování mapy
    </button>
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
