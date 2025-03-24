<script lang="ts">
  import { onMount } from 'svelte';
  import { wantedAreas, fitPaperSize, paperDimension, paperDimensionRequest, automaticZoomLevel, areasId } from '$lib/stores/mapStore';
  import api from '$lib/axios.config';
  import { checkMapCordinatesFormat, checkFitPaper, parseWantedAreas, numberOfAreaPlots } from '$lib/utils/areaUtils';
  import axios from 'axios'
  import { paperSizes } from '$lib/constants';

  let areaSuggestions: string[][] = [];
  const defaultWidth = 0.5;
  let settingArea = false;
  let gettingMapBorders = false;
  let gettingSuggestions = false;

  let debounceTimeout: ReturnType<typeof setTimeout> | null = null;

 

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
  
 
  // Function to add a new area
  function addArea() {
    const newArea: AreaItemStored = {
      id: $areasId++,
      area: "",
      plot: true,
      width: defaultWidth
    };
    $wantedAreas = [...$wantedAreas, newArea];
  }

  // Function to remove an area
  function removeArea(id: number) {
    $wantedAreas = $wantedAreas.filter(area => area.id !== id);
  }

  function handleSelectedPaperSizeChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    const selectedSize = JSON.parse(selectedValue) as PaperDimension; 
    $paperDimensionRequest.width = selectedSize.width;
    $paperDimensionRequest.height = selectedSize.height;
  }

  function checkPaperDimensionRequest(request: PaperDimensionRequest): boolean {
    if(request.width == null && request.height == null){
      return false;
    }

    return true;
  }

  function changeGroupWidth(group: number, width: number): void {
    if(group == null || group <= 0){
      return;
    }
    $wantedAreas = $wantedAreas.map(area => 
      area.group != null && area.group > 0 && area.group === group ? { ...area, width: width } : area
      );
  }


  function getJoinedGroupWidth(group: number, myWidth: number, myId: number): number {
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
      if(!checkPaperDimensionRequest($paperDimensionRequest)){
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
        paper_dimensions: {width: $paperDimensionRequest.width === undefined ? null : $paperDimensionRequest.width,
           height: $paperDimensionRequest.height === undefined ? null : $paperDimensionRequest.height}, 
        given_smaller_paper_dimension: $paperDimensionRequest.given_smaller_dimension,
        wanted_orientation: $paperDimensionRequest.orientation,
      }, {
        headers: {
          "Content-Type": "application/json"
        }
      }).then(response => {
        $paperDimension.height = response.data.height;
        $paperDimension.width = response.data.width;
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
      if(!checkPaperDimensionRequest($paperDimensionRequest)){
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
        paper_dimensions: $paperDimension, 
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

const searchAreaWhisper = async (query: string, id: number): Promise<void> => {
  if (!query || query.length < 1) {
    areaSuggestions[id] = [];
    return;
  }

  gettingSuggestions = true;
  //todo do env
    axios.get(import.meta.env.VITE_API_NOMINATIM_URL,{
      params: {
      format: 'json',
      featureType: 'country, state, city, settlement',  
      q: query,
      namedetails: 0,
      limit: 5,
    },     
      headers: {
          'Accept-Language': 'cs-CZ'
        }
    }).then(response => {
      if (response.status === 200) {

        const polygonResults = response.data.filter((result: any) => {
            return result.osm_type && 
                  (result.osm_type === 'relation');
          });
        const data: NominatimResult[] = polygonResults;
        
        areaSuggestions[id] = data.map(item => item.display_name);
      }
      gettingSuggestions = false;
    }).catch(e => {
      gettingSuggestions = false;
      alert("Chyba při získávání nápovědy")
      console.log(e);
      areaSuggestions[id] = [];
    });
}

let debounceSearchArea = (query: string, id: number) => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      searchAreaWhisper(query, id)
    }, 200);
   }

const selectAreaSuggestion = (newAreaValue: string, id: number): void => {
  $wantedAreas = $wantedAreas.map(area => 
    area.id === id ? { ...area, area: newAreaValue } : area
    );
  areaSuggestions[id] = [];
  areaSuggestions = [...areaSuggestions]; // Trigger reactivity
};

</script>
<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Mapové oblasti a nastavení papíru</h1>
  <div class="space-y-4 rounded-lg bg-gray-100 ">
    <h2 class="p-2 text-xl font-bold">Mapové oblasti</h2>
    {#each $wantedAreas as area (area.id)}
        <div class="p-4 flex flex-wrap gap-4 items-start">
          <!-- Area Input -->
          <div class="flex flex-col">
            <p class="text-sm font-medium mb-1">Oblast</p>
            <input
              type="text" 
              class="border rounded p-2 w-60"
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
                  <div class="relative top-full left-0 w-60 mt-1 bg-white border rounded shadow-lg z-10 max-h-60 overflow-y-auto">
                    {#each areaSuggestions[area.id] as displayName}
                      <div 
                      role="button"
                      tabindex="0"
                      on:keydown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                searchAreaWhisper(area.area, area.id);
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
                class="border rounded p-2 w-20"
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
                class="border rounded p-2 w-40"
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
      class="flex items-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
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
                class="border rounded p-2 w-20"
                min="0.05"
                step="0.1"
                bind:value={$fitPaperSize.width} 
              />
      </div>
      {/if}
      {/if}
    </div>
  </div>

  <!-- fit paper  -->  
  

  <div class="space-y-4 mt-4 rounded-lg bg-gray-100 ">
    <h2 class="p-2 text-xl font-bold">Nastavení papíru</h2>
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
        class="border rounded p-2 w-20"
        bind:value={$paperDimensionRequest.width}
        min="10"
        step="10"
      />
    </div>
    <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Výška (v mm)</p>
        <input
        type="number"
        class="border rounded p-2 w-20"
        bind:value={$paperDimensionRequest.height}
        min="10"
        step="10"
      />
    </div>
    <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Orientace papíru</p>
      <select
        class="border rounded p-2 w-40"
        bind:value={$paperDimensionRequest.orientation}
      >
        <option value="automatic">Automatická</option>
        <option value="portrait">Na výšku</option>
        <option value="landscape">Na šířku</option>
      </select>
    </div>
    {#if $paperDimensionRequest.width == null || $paperDimensionRequest.height == null}
    <div class="flex flex-col">
      <p class="text-sm font-medium mb-1">Zadán menší rozměr papíru</p>
        <div class="h-10 flex items-center">
          <input 
            type="checkbox" 
            class="h-5 w-5 items-center rounded-lg"
            bind:checked={$paperDimensionRequest.given_smaller_dimension} 
          />
        </div>
    </div>
    {/if}
    
  </div>
    <div class="p-4 flex justify-end">
        <button 
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded ml-4"
        class:bg-gray-500={settingArea}
        class:hover:bg-gray-600={settingArea}
        on:click={getPaperAndZoom}
        disabled = {settingArea}
      >
       Nastavit oblasti a papír
      </button>
</div>

  <div class="p-4">
    <p class="text-md font-medium mb-1">
    Výsledná velikost papíru: {$paperDimension.width}mm x {$paperDimension.height}mm (šířka x výška)
      </p>
  </div>
    
    </div>
    <div class = "flex justify-end">
      {#if $paperDimension.width > 0 && $paperDimension.height > 0}
      <button 
        class="text-white px-4 py-2 rounded ml-4 mt-4"
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
    
      
  </div>
  </div>
