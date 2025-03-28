<script lang="ts">
  import { onMount } from 'svelte';
  import { wantedAreas, fitPaperSize, paperDimensions, paperDimensionsRequest, automaticZoomLevel, areasId, selectedMapFiles, avilableMapFiles } from '$lib/stores/mapStore';
  import api from '$lib/axios.config';
  import { checkMapCordinatesFormat, checkFitPaper, parseWantedAreas, numberOfAreaPlots,
    searchAreaWhisper, checkPaperDimensions
   } from '$lib/utils/areaUtils';
  import { paperSizes, mapDataNamesMappingCZ } from '$lib/constants';
  import { mapValue } from '$lib/utils/mapElementsUtils';

  let areaSuggestions: string[][] = [];
  const defaultWidth = 0.5;
  let settingArea = false;
  let gettingMapBorders = false;
  let displayedTab = "mapData";
  let debounceTimeout: ReturnType<typeof setTimeout> | null = null;
  let mapFileSearchTerm = '';

  onMount(() => {
    if($wantedAreas.length === 0){
      const newArea: AreaItemStored = {
      id: $areasId++,
      area: "Česko",
      plot: true,
      width: defaultWidth,
      group: 0
    };
    $wantedAreas = [newArea];
    }
   
  });
  

  function addArea() {
    const newArea: AreaItemStored = {
      id: $areasId++,
      area: "",
      plot: true,
      width: defaultWidth
    };
    $wantedAreas = [...$wantedAreas, newArea];
  }

  function removeArea(id: number) {
    $wantedAreas = $wantedAreas.filter(area => area.id !== id);
  }

  function handleSelectedPaperSizeChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    const selectedSize = JSON.parse(selectedValue) as PaperDimensions; 
    $paperDimensionsRequest.width = selectedSize.width;
    $paperDimensionsRequest.height = selectedSize.height;
  }



  function changeGroupWidth(group: number | undefined, width: number | undefined): void {
    if(group == null || group <= 0 || width == null){
      return;
    }
    $wantedAreas = $wantedAreas.map(area => 
      area.group != null && area.group > 0 && area.group === group ? { ...area, width: width } : area
      );
  }


  function getJoinedGroupWidth(group: number | undefined, myWidth: number | undefined, myId: number): number {
    if(myWidth == null){
      return defaultWidth;
    }
    if(group == null || group <= 0){
      return myWidth
    }
    const groupAreas = $wantedAreas.filter(area => area.group === group);
    if(groupAreas.length === 0){
      return myWidth;
    }
    for (let area of groupAreas)
    {
      if(area.id !== myId){
        return area.width ?? myWidth;
      }
    } 
    return myWidth;
  }


  function getPaperAndZoom() {
    let parsedAreas
    try{
      if(!checkPaperDimensions($paperDimensionsRequest, true)){
        alert("Alespoň jede z rozměrů papíru musí být vyplněn");
        return;
      }
      
      parsedAreas = parseWantedAreas($wantedAreas);
      if(parsedAreas.length === 0){
        alert("Musí být zadána alespoň jedna oblast");
        return;
      }
    }catch(e){
      console.error(e);
      alert("Chyba při zpracování souřadnic oblastí");
      return;
    }
      settingArea = true
      api.post("/paper_and_zoom", {
        map_area: parsedAreas,
        paper_dimensions: {width: $paperDimensionsRequest.width === undefined ? null : $paperDimensionsRequest.width,
           height: $paperDimensionsRequest.height === undefined ? null : $paperDimensionsRequest.height}, 
        given_smaller_paper_dimension: $paperDimensionsRequest.given_smaller_dimension,
        wanted_orientation: $paperDimensionsRequest.orientation,
      }, {
        headers: {
          "Content-Type": "application/json"
        }
      }).then(response => {
        $paperDimensions.height = response.data.height;
        $paperDimensions.width = response.data.width;
        $automaticZoomLevel = response.data.zoom_level;
        settingArea = false
      }).catch(e => {
        console.error(e)
        if(e.response?.status === 400){
          alert("Některé zadané oblasti nemají správný formát")
        }
        else if(e.response?.status === 404){
          alert("Některou se zadaných oblastí se nepodařilo nalézt")
        }
        else{
          alert("Nastala chyba při zpracování požadavku, zkuste to znovu za chvíli")
        }
        settingArea = false
      });
}


async function getMapBorders() {
    let parsedAreas
    try{
      if(!checkPaperDimensions($paperDimensions, false)){
        alert("Alespoň jede z rozměrů papíru musí být vyplněn");
        return;
      }

      if(!checkFitPaper($fitPaperSize)){
        alert("Šířka ohraničení vyplněné oblasti musí být vyplněna");
        return;
      }
      
      parsedAreas = parseWantedAreas($wantedAreas);
      if(parsedAreas.length === 0){
        alert("Musí být zadána alespoň jedna oblast");
        return;
      }
    }catch(e){
      console.error(e);
      alert("Chyba při zpracování oblasti a papíru");
      return;
    }
    gettingMapBorders = true
  
    api.post("/generate_map_borders", {
      map_area: parsedAreas,
      paper_dimensions: $paperDimensions, 
      fit_paper_size: $fitPaperSize
    }, {
      responseType: 'blob',
      headers: {
        "Content-Type": "application/json"
      }
      
    }).then(response => {
      const blob = new Blob([response.data], { 
        type: response.headers['content-type'] 
      });
      const url = window.URL.createObjectURL(blob);
      
      // Create a temporary link element to trigger the download
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', "mapa_okraje.pdf");
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      gettingMapBorders = false
    }).catch(e => {
      if(e.response?.status === 400){
        alert("Některé zadané oblasti nemají správný formát")
      }
      else if(e.response?.status === 404){
        alert("Některou se zadaných oblastí se nepodařilo nalézt")
      }
      else{
        alert("Nastala chyba při zpracování požadavku, zkuste to znovu za chvíli")
      }
      console.error(e);
      gettingMapBorders = false
    });
}

	$: filteredMapFiles = $avilableMapFiles.filter(file => 
    (file.toLowerCase().includes(mapFileSearchTerm.toLowerCase()) && 
		!$selectedMapFiles.includes(file)) || 
    (mapValue(mapDataNamesMappingCZ, file).toLowerCase().includes(mapFileSearchTerm.toLowerCase()) && 
		!$selectedMapFiles.includes(file))
	);

	function addMapFile(file: string) {
    $selectedMapFiles = [...$selectedMapFiles, file];
	}

	function removeMapFile(file: string) {
		$selectedMapFiles = $selectedMapFiles.filter(item => item !== file)
	}

function debounceSearchArea(query: string, id: number){
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(async () => {
      searchAreaWhisper(query).then(areas => {
        areaSuggestions[id] = areas;
      }).catch(e => {
        console.error(e);
      });
    }, 200);
   }

function selectAreaSuggestion(newAreaValue: string, id: number): void{
  $wantedAreas = $wantedAreas.map(area => 
    area.id === id ? { ...area, area: newAreaValue } : area
    );
  areaSuggestions[id] = [];
  areaSuggestions = [...areaSuggestions]; // Trigger reactivity
};

</script>



<div class="container mx-auto p-4">
  <div class="flex flex-wrap -mb-px">
    <button 
     class= { displayedTab == "mapData" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
            "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
            on:click={() => displayedTab = "mapData"}>
            Mapová dat
    </button>
    <button 
     class= { displayedTab == "area" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
            "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
            on:click={() => displayedTab = "area"}>
            Oblasti
    </button>
    <button  class= { displayedTab == "paper" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
            "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
            on:click={() => displayedTab = "paper"}>
            Papír
    </button>
  </div>
  {#if displayedTab == "mapData"}
  <div class="space-y-4 p-4 rounded-lg bg-gray-100 ">
    <div class="p-2 flex flex-wrap gap-4 items-start">
      <h2 class="text-xl font-bold mb-2">Vybraná mapová data: </h2>
      {#if $selectedMapFiles.length != 0}
        {#each $selectedMapFiles as mapFile}
          <p 
            class="flex items-center bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm"
          >
            {mapValue(mapDataNamesMappingCZ, mapFile)}
            <button 
              on:click={() => removeMapFile(mapFile)}
              class="ml-2 text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </p>
        {/each}
      {:else} 
        <p class="flex items-center mt-1 px-2 py-1 rounded text-sm text-gray-500">Žádná mapová data nebyla vybrána</p>
      {/if}
        
      <input 
        type="text" 
        bind:value={mapFileSearchTerm}
        placeholder="Vyhledat mapová data..."
        class="w-full rounded p-2 mb-2"
      />
      <p>Dostupná data: </p>
        <div class="w-full border rounded max-h-28 overflow-y-auto">
        {#each filteredMapFiles as mapFile}
          <div 
          role="button"
          tabindex="0"
          on:keydown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    addMapFile(mapFile)
                  }
                }}
            class="p-2 bg-white hover:bg-gray-100 cursor-pointer"
            on:click={() => addMapFile(mapFile)}
          >
            {mapValue(mapDataNamesMappingCZ, mapFile)}
          </div>
        {:else}
          <div class="bg-white p-2 text-gray-500">{mapFileSearchTerm == ""?"Žádné další dostupné data": "Žádné data neodpovídají vyhledávání"}</div>
        {/each}
      </div>
    </div>
  </div>

  {:else if displayedTab == "area"}
  <div class="space-y-4 p-4 rounded-lg bg-gray-100 ">
    {#each $wantedAreas as area (area.id)}
        <div class="p-4 flex flex-wrap gap-4 items-start">
          <!-- Area Input -->
          <div class="flex flex-col"
          tabindex="0" 
          role="button"
          on:blur={() => {
            areaSuggestions[area.id] = [];
            areaSuggestions = [...areaSuggestions];
          }}>
            <p class="text-sm font-medium mb-1">Oblast</p>
            <input
              type="text" 
              class="border rounded-sm p-2 w-60"
              bind:value={area.area}
              on:keyup={() => {
                if(area.area.includes(';')) {
                    areaSuggestions[area.id] = [];
                    areaSuggestions = [...areaSuggestions];
                } else{
                  debounceSearchArea(area.area, area.id)}
                }
              }
            />
          
            {#if areaSuggestions[area.id]?.length > 0}
                  <div class="relative top-full left-0 w-60 mt-1 bg-white border rounded-sm shadow-lg z-10 max-h-60 overflow-y-auto">
                    {#each areaSuggestions[area.id] as displayName}
                      <div 
                      role="button"
                      tabindex="0"
                      on:keydown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                selectAreaSuggestion(displayName, area.id)
                              }
                            }}
                        class="p-2 hover:bg-gray-100 cursor-pointer"
                        on:click={() => selectAreaSuggestion(displayName, area.id)}
                      >
                        {displayName}
                      </div>
                    {/each}
                  </div>
                {/if}
            <p class="text-red-500 text-sm">{checkMapCordinatesFormat(area.area)}</p>
          </div>
         
          <!-- Plot Checkbox -->
          <div class="flex flex-col">
            <p class="text-sm font-medium mb-1">Vykreslit ohraničení oblasti</p>
            <div class="h-10 flex items-center">
              <input 
                type="checkbox" 
                class="h-5 w-5 items-center rounded-lg"
                bind:checked={area.plot} 
              />
            </div>
          </div>
          
          <!-- Conditional inputs based on plot checkbox -->
          {#if area.plot}
            <!-- Width Input -->
            <div class="flex flex-col">
              <p class="text-sm font-medium mb-1">Šířka ohraničení (v mm)</p>
              <input 
                type="number" 
                class="border rounded-sm p-2 w-20"
                on:change={()=> changeGroupWidth(area?.group, area.width)}
                min="0.05"
                step="0.1"
                bind:value={area.width} 
              />
            </div>
            
          {#if $wantedAreas.length > 1 && numberOfAreaPlots($wantedAreas) > 1}
            <!-- Group Select -->
            <div class="flex flex-col">
              <p class="text-sm font-medium mb-1">Skupina oblastí</p>
              <select
                class="border rounded-sm p-2 w-40"
                bind:value={area.group}
                on:change={()=>  area.width = getJoinedGroupWidth(area?.group, area.width, area.id)}
              >
                <option value={0}>Žádná</option>
                {#each Array.from({length: numberOfAreaPlots($wantedAreas)}, (_, i) => i) as group}
                  {#if group > 0}
                    <option value={group}>Skupina {group}</option>
                  {/if}
                {/each}
              </select>
            </div>
            {/if}
          {/if}
          
          <!-- Remove Button - hidden for first item -->
          {#if $wantedAreas.length > 1}
          <div class="flex flex-col">
            <p class="text-sm font-medium mb-1">Odstranit oblast</p>
            <button 
            class="h-10 w-10 text-red-500 hover:text-red-700"
            on:click={() => removeArea(area.id)}
              title="Odstranit oblast"
            >
              Odstranit 
            </button>
          </div>
          {/if}
      </div>
    {/each}
    <div class="p-4">
      <button 
      class="flex items-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-sm"
        on:click={addArea}
      >
        Přidat další oblast
      </button>
    </div>
    <div class="p-4 flex flex-wrap gap-4 items-end">
      <div class="flex flex-col">
        <p class="text-sm font-medium mb-1">Vyplnit papír okolím oblastí</p>
          <div class="h-10 flex items-center">
            <input 
              type="checkbox" 
              class="h-5 w-5 items-center rounded-lg"
              bind:checked={$fitPaperSize.fit} 
            />
          </div>
      </div>
      {#if $fitPaperSize.fit}
      <div class="flex flex-col">
        <p class="text-sm font-medium mb-1">Vykreslit ohraničení vyplněné oblasti</p>
          <div class="h-10 flex items-center">
            <input 
              type="checkbox" 
              class="h-5 w-5 items-center rounded-lg"
              bind:checked={$fitPaperSize.plot} 
            />
          </div>
      </div>
      {#if $fitPaperSize.plot}
      <div class="flex flex-col">
        <p class="text-sm font-medium mb-1">Šířka ohraničení (v mm)</p>
          <input
            type="number" 
            class="border rounded-sm p-2 w-20"
            min="0.05"
            step="0.1"
            bind:value={$fitPaperSize.width} 
          />
      </div>
      {/if}
      {/if}
    </div>
  </div>

  {:else if displayedTab == "paper"}
  <!-- paper  -->  
  <div class="p-4 space-y-4 mt-4 rounded-lg bg-gray-100 ">
    <div class="p-4 flex flex-wrap gap-4 items-end">
     <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Velikost papíru</p>
      <select on:change={handleSelectedPaperSizeChange}>
        {#each paperSizes as paper}
          <option value={paper.value}>
            {paper.label}
          </option>
        {/each}
      </select>
    </div>
    <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Šířka (v mm)</p>
      <input
        type="number"
        class="border rounded-sm p-2 w-20"
        bind:value={$paperDimensionsRequest.width}
        min="10"
        step="10"
      />
    </div>
    <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Výška (v mm)</p>
        <input
        type="number"
        class="border rounded-sm p-2 w-20"
        bind:value={$paperDimensionsRequest.height}
        min="10"
        step="10"
      />
    </div>
    <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Orientace papíru</p>
      <select
        class="border rounded-sm p-2 w-40"
        bind:value={$paperDimensionsRequest.orientation}
      >
        <option value="automatic">Automatická</option>
        <option value="portrait">Na výšku</option>
        <option value="landscape">Na šířku</option>
      </select>
    </div>
    {#if $paperDimensionsRequest.width == null || $paperDimensionsRequest.height == null}
    <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Zadán menší rozměr papíru</p>
        <div class="h-10 flex items-center">
          <input 
            type="checkbox" 
            class="h-5 w-5 items-center rounded-lg"
            bind:checked={$paperDimensionsRequest.given_smaller_dimension} 
          />
        </div>
    </div>
    {/if}
    
  </div>
    
  <div class="p-4">
    <p class="text-md font-medium mb-1">
      Výsledná velikost papíru: {$paperDimensions.width}mm x {$paperDimensions.height}mm (šířka x výška)
      </p>
  </div>

    </div>
  
  {/if}

    <div class = "flex justify-end">
      {#if displayedTab == "paper" || displayedTab == "area"}
      <div class="p-4 flex justify-end">
        <button 
          class="bg-blue-500  hover:bg-blue-600 text-white px-8 py-4 rounded-lg ml-4"
          class:bg-gray-500={settingArea}
          class:hover:bg-gray-600={settingArea}
          on:click={getPaperAndZoom}
          disabled = {settingArea}
          >
            Nastavit oblasti a papír
        </button>
      </div>
      {#if $paperDimensions.width > 0 && $paperDimensions.height > 0}
        <button 
          class="text-white px-4 py-2 rounded-lg ml-4 mt-4"
          class:bg-green-500={!gettingMapBorders}
          class:hover:bg-green-600={!gettingMapBorders}
          class:bg-gray-500={gettingMapBorders}
          class:hover:bg-gray-600={gettingMapBorders}
          on:click={getMapBorders}
          disabled={gettingMapBorders}
        >
          Prohlédnou okraje oblastí <br>(vytvořit PDF)
      </button>
    {/if}  
    {/if}
</div>
</div>
