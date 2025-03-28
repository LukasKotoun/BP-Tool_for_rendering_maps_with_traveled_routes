
<script lang="ts">
    import { wantedAreas, areasPreviewId, wantedPreviewAreas, paperPreviewDimensions, fitPaperSize, PaperDimensions,
        wantPlotBridges, wantPlotTunnels, peaksFilterSensitivity, minPopulationFilter, mapNodesElements, mapWaysElements, mapAreasElements,
        selectedMapTheme, selectedMapFiles, gpxFiles, gpxFileGroups, gpxStyles, mapElementsZoomDesign} from '$lib/stores/mapStore';
    import { paperSizes, mapDataNamesMappingCZ } from '$lib/constants';
    
    import { checkMapCordinatesFormat, checkFitPaper, parseWantedAreas, searchAreaWhisper, 
        checkPaperDimensions
    } from '$lib/utils/areaUtils';
    import { transformElementsStructure } from '$lib/utils/mapElementsUtils';
    import { onMount } from 'svelte';
    import api from '$lib/axios.config';
    import { json } from '@sveltejs/kit';
    let pollingTime = 15000; // 15 seconds
    let pollingInterval: number | null = null;
    let debounceTimeout: ReturnType<typeof setTimeout> | null = null;
    let displayedTab = "previewMap"
    let areaSuggestions: string[][] = [];
    let isGenerating = false
    let isPolling = false
    let statusMessage = ""
    let status = ""
    let generatingMessage = ""
    let jwtToken = ""

    onMount(() => {
        if($paperPreviewDimensions.width == 0 && $paperPreviewDimensions.height == 0){
            $paperPreviewDimensions = { width: 297, height: 210 }
        }
    });
        
    function addArea() {
        const newArea: AreaItemStored = {
        id: $areasPreviewId++,
        area: "",
        plot: false,
        };
        $wantedPreviewAreas = [...$wantedPreviewAreas, newArea];
    }

    function removeArea(id: number) {
        $wantedPreviewAreas = $wantedPreviewAreas.filter(area => area.id !== id);
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

    function handleSelectedPaperSizeChange(event: Event) {
        const selectedValue = (event.target as HTMLSelectElement).value;
        const selectedSize = JSON.parse(selectedValue) as PaperDimensions; 
        $paperPreviewDimensions.width = selectedSize.width;
        $paperPreviewDimensions.height = selectedSize.height;
    }

    function flipPaper(){
        $paperPreviewDimensions = { width: $paperPreviewDimensions.height, height: $paperPreviewDimensions.width };
    }
    
    function selectAreaSuggestion(newAreaValue: string, id: number): void{
        $wantedPreviewAreas = $wantedPreviewAreas.map(area => 
            area.id === id ? { ...area, area: newAreaValue } : area
            );
        areaSuggestions[id] = [];
        areaSuggestions = [...areaSuggestions]; // Trigger reactivity
    };

    function generateMap(preview: boolean = false){
    let parsedAreas: AreaItemSend[] = []
    let parsedPreviewAreas: AreaItemSend[] | null = []
    let mapNodesElementsParsed: MapElementCategorySend = {}
    let mapWaysElementsParsed: MapElementCategorySend = {}
    let mapAreasElementsParsed: MapElementCategorySend = {}
    try{
        if(preview){
            if(!checkPaperDimensions($paperPreviewDimensions, false)){
                alert("Rozměry náhledového papíru musí být vyplněny");
                return;
            }
            parsedPreviewAreas = parseWantedAreas($wantedPreviewAreas);
            if(parsedPreviewAreas.length === 0){
                parsedPreviewAreas = null;
            }

        }
        if(!checkPaperDimensions($PaperDimensions, false)){
            alert("Rozměry papíru musí být vyplněny");
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
        if($selectedMapFiles.length === 0){
            alert("Musí být vybrán alespoň jeden soubor s mapovými daty");
            return;
        }

        mapNodesElementsParsed = transformElementsStructure($mapNodesElements, 'plot', { width_scale: 1, text_scale: 1 });
        mapWaysElementsParsed = transformElementsStructure($mapWaysElements, 'plot', { width_scale: 1, text_scale: 1 });
        mapAreasElementsParsed = transformElementsStructure($mapAreasElements, 'plot', { width_scale: 1, text_scale: 1 });
    }catch(e){
      console.error(e);
      alert("Chyba při zpracování dat");
      return;
    }
        generatingMessage = preview ? "Generování náhledové mapy" : "Generování mapy";
        isGenerating = true
        status = ""
        statusMessage = "Odesílání dat na server"
        const formData = new FormData();
        const data = JSON.stringify({
            osm_files: $selectedMapFiles,
            map_area: parsedAreas,
            map_preview_area: parsedPreviewAreas,
            paper_dimensions: $PaperDimensions,
            paper_preview_dimensions: $paperPreviewDimensions,
            gpxs_groups: $gpxFileGroups,
            map_theme: $selectedMapTheme,
            fit_paper_size: $fitPaperSize,
            plot_bridges: $wantPlotBridges,
            plot_tunnels: $wantPlotTunnels,
            peaks_filter_sensitivity: $peaksFilterSensitivity,
            min_place_population: $minPopulationFilter,
            wanted_categories_and_styles_edit:{
                nodes: mapNodesElementsParsed,
                ways: mapWaysElementsParsed,
                areas: mapAreasElementsParsed
            },
            gpxs_styles: $gpxStyles,
            styles_zoom_levels: $mapElementsZoomDesign
        })
        for (const file in $gpxFiles) {
            formData.append('gpxs', file);
        }
        formData.append('config', data);

        api.post(preview? "/generate_map_preview" : "/generate_map_normal", formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
        }).then((response) => {
            jwtToken = response.data.token
            statusMessage = "Mapa byla úspěšně vygenerována"
            pollTaskInfo()
        }).catch((error) => {
            alert("Chyba při odesílání dat na server")
            statusMessage = ""
            status = ""
            isGenerating = false
            jwtToken = ""
            console.error(error)
        })


    }

    async function pollTaskInfo() {
        if (isPolling || jwtToken == null || jwtToken == "") return;
        isPolling = true;
        api.get('/task_status', {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        }).then((response) => {
                status = response.data.status
                statusMessage = response.data.message;
                if (response.data.status === 'complete') {
                    stopPolling();
                }
        }).catch((error) => {
            if(error.response.status === 404){
            stopPolling();
            alert("Generování mapy bylo nečekaně přerušeno, zkuste to znovu později")
            statusMessage = ""
            status = ""
            isGenerating = false
            jwtToken = ""
            return
        }
        console.error('Pooling error', error);
            statusMessage = 'Error checking status. Retrying...';
            console.error('Polling error:', error);
        });


        pollingInterval = window.setInterval(async () => {
            api.get('/task_status', {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
            }).then((response) => {
                status = response.data.status
                statusMessage = response.data.message || 'Processing...';
                if (response.data.status === 'complete') {
                    stopPolling();
                }
            }).catch((error) => {
                if(error.response.status === 404){
                stopPolling();
                alert("Generování mapy bylo nečekaně přerušeno, zkuste to znovu později")
                statusMessage = ""
                status = ""
                isGenerating = false
                jwtToken = ""
                return
            }
            console.error('Pooling error', error);
                statusMessage = 'Error checking status. Retrying...';
                console.error('Polling error:', error);
            });

        }, pollingTime); // 15 seconds
    }
    function stopPolling() {
    // Clear the interval
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
   
    isPolling = false;
    }

    function terminateTask(){
        const confirmed = window.confirm("Opravdu chcete ukončit generování mapy?");
        if(!confirmed){
            return
        }
        statusMessage = ""
        status = ""
        isGenerating = false
        jwtToken = ""
        api.delete('/terminate_task', {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        }).then((response) => {
           
        }).catch((error) => {
                console.error(error)
        })
    }

</script>
{#if isGenerating}
<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white p-12 rounded-xl shadow-2xl text-center w-3/4 max-w-2xl space-y-6">
        <h1 class="text-2xl font-bold mb-4">{generatingMessage}</h1>
        <h2 class="text-2xl font-bold mb-4">{statusMessage}</h2>
    {#if status == "success"}
        <p>Stáhnout mapu</p>
    {/if}

      <button 
        on:click={terminateTask}
        class="mt-4 px-6 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
      >
        Ukončit generování
      </button>
  </div>
</div>
{/if}

<div class="container mx-auto p-4">
    <div class="flex flex-wrap -mb-px">
        <button 
         class= { displayedTab == "normalMap" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
                "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                on:click={() => displayedTab = "normalMap"}>
                Vytvoření celé mapy
        </button>
        <button 
         class= { displayedTab == "previewMap" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
                "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                on:click={() => displayedTab = "previewMap"}>
                Vytvoření náhledu mapy
        </button>
     
    </div>

    {#if displayedTab == "normalMap"}
    <div class="space-y-4 rounded-lg bg-gray-100 ">
        <div class="space-y-4 rounded-lg bg-gray-100 flex justify-center items-center p-6">
            <button class="px-8 py-4 text-xl bg-green-500 text-white font-semibold rounded-lg shadow-lg hover:bg-green-600 transition"
            on:click={() => generateMap(false)}
            disabled={isGenerating}>
                Vytvořit mapu (pdf)
            </button>
        </div>
    </div>
    {:else if displayedTab == "previewMap"}
   
    <div class="space-y-4 p-4 rounded-lg bg-gray-100 ">
        {#each $wantedPreviewAreas as area (area.id)}
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
                         
              <!-- Remove Button - hidden for first item -->
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
          </div>
        {/each}
        <div class="p-4">
          <button 
          class="flex items-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-sm"
            on:click={addArea}
          >
            Přidat náhledovou oblast
          </button>
        </div>

        <div class="p-4 flex flex-wrap gap-4 items-end">
            <div class="flex flex-col">
        <p class="text-sm font-medium mb-1">Velikost papíru</p>
            <select on:change={handleSelectedPaperSizeChange}>
              {#each paperSizes as paper}
                {#if !((JSON.parse(paper.value) as PaperDimensions).width == null || (JSON.parse(paper.value) as PaperDimensions).height == null)}
                  <option value={paper.value} selected={
                  (JSON.parse(paper.value) as PaperDimensions).width == $paperPreviewDimensions.width &&
                   (JSON.parse(paper.value) as PaperDimensions).height == $paperPreviewDimensions.height ||
                   (JSON.parse(paper.value) as PaperDimensions).width == $paperPreviewDimensions.height &&
                   (JSON.parse(paper.value) as PaperDimensions).height == $paperPreviewDimensions.width}>
                   {paper.label}</option>
                {/if}
              {/each}
            </select>
            </div>
            <div class="flex flex-col">
                <button class="px-4 py-2 bg-blue-500 text-white rounded-sm shadow hover:bg-blue-600 transition"
                on:click={flipPaper}>
                    Otočit
                </button>
            </div>
          </div>
          <div class="p-4">
            <p class="text-md font-medium mb-1">
              Výsledná velikost náhledu: {$paperPreviewDimensions.width}mm x {$paperPreviewDimensions.height}mm (šířka x výška)
              </p>
          </div>
    </div>
    <div class="space-y-4 rounded-lg flex justify-center items-center p-6">
        <button class="px-8 py-4 text-xl bg-green-500 text-white font-semibold rounded-lg shadow-lg hover:bg-green-600 transition"
        on:click={() => generateMap(true)}
        disabled={isGenerating}>
            Vytvořit náhledovou mapu (pdf)
        </button>
    </div>

    {/if}
</div>
