<script lang="ts">
  import MapElementsManager from "$lib/managers/mapElementsManager.svelte"
  import AreaPaperManager from "$lib/managers/areaPaperManager.svelte";
  import GpxManager from "$lib/managers/gpxManager.svelte";
  

  let displayedTab = "areaPaper"
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
asdh
{/if}
</div>