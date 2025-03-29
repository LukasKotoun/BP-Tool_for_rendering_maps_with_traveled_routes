<script lang="ts">
    import { wantedAreas, areasPreviewId, wantedPreviewAreas, paperPreviewDimensions, fitPaperSize, paperDimensions,
        wantPlotBridges, wantPlotTunnels, peaksFilterSensitivity, minPopulationFilter, mapNodesElements, mapWaysElements, mapAreasElements,
        selectedMapTheme, selectedMapFiles, gpxFiles, gpxFileGroups, gpxStyles, mapElementsZoomDesign, displayedTabMapGenerating} from '$lib/stores/mapStore';
    import { paperSizes, mapGeneratingStatusMappingCZ } from '$lib/constants';
    import { checkMapCordinatesFormat, checkFitPaper, parseWantedAreas, searchAreaWhisper, checkPaperDimensions } from '$lib/utils/areaUtils';
    import { getUngrupedFiles } from '$lib/utils/gpxFilesUtils';
    import { transformElementsStructure, mapValue} from '$lib/utils/mapElementsUtils';
    import { MapGeneratingStatus } from '$lib/enums/mapEnums';
    import { onMount } from 'svelte';
    import { Trash2, CirclePlus } from '@lucide/svelte';
    import api from '$lib/axios.config';

    let normalPollingTime = 5000; 
    let previewPollingTime = 3000
    let pollingInterval: number | null = null;
    let debounceTimeout: ReturnType<typeof setTimeout> | null = null;
    let areaSuggestions: string[][] = [];
    let isGenerating = false
    let isPolling = false
    let status = ""
    let jwtToken = ""

    onMount(() => {
        if($paperPreviewDimensions.width == 0 && $paperPreviewDimensions.height == 0){
            $paperPreviewDimensions = { width: 297, height: 210 }
        }
        // on page close terminate running task
        const handleBeforeUnload = (event) => {
            if(jwtToken == null || jwtToken == "") return;
            navigator.sendBeacon(`${import.meta.env.VITE_API_BASE_URL}/terminate_task`, JSON.stringify({token:jwtToken} ));
        };
        window.addEventListener('beforeunload', handleBeforeUnload);
        
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
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
        let parsedPreviewAreas: AreaItemSend[] | null = null
        let mapNodesElementsParsed: MapElementCategorySend = {}
        let mapWaysElementsParsed: MapElementCategorySend = {}
        let mapAreasElementsParsed: MapElementCategorySend = {}
        let fileGroups: GPXFileGroups = {}
        isGenerating = true
        try{
            if(preview){
                if(!checkPaperDimensions($paperPreviewDimensions, false)){
                    alert("Rozměry náhledového papíru musí být vyplněny");
                    isGenerating = false
                    return;
                }
                parsedPreviewAreas = parseWantedAreas($wantedPreviewAreas);
                if(parsedPreviewAreas.length === 0){
                    parsedPreviewAreas = null;
                }

            }
            if(!checkPaperDimensions($paperDimensions, false)){
                alert("Rozměry papíru musí být vyplněny");
                isGenerating = false
                return;
            }

            if(!checkFitPaper($fitPaperSize)){
                alert("Šířka ohraničení vyplněné oblasti musí být vyplněna");
                isGenerating = false
                return;
            }
            
            parsedAreas = parseWantedAreas($wantedAreas);
            if(parsedAreas.length === 0){
                alert("Musí být zadána alespoň jedna oblast");
                isGenerating = false
                return;
            }
            if($selectedMapFiles.length === 0){
                alert("Musí být vybrán alespoň jeden soubor s mapovými daty");
                isGenerating = false
                return;
            }
            
            let ungrupedFiles = getUngrupedFiles($gpxFileGroups, $gpxFiles)
            fileGroups = { ...$gpxFileGroups, default: ungrupedFiles }
            mapNodesElementsParsed = transformElementsStructure($mapNodesElements, 'plot', { width_scale: 1, text_scale: 1 });
            mapWaysElementsParsed = transformElementsStructure($mapWaysElements, 'plot', { width_scale: 1, text_scale: 1 });
            mapAreasElementsParsed = transformElementsStructure($mapAreasElements, 'plot', { width_scale: 1, text_scale: 1 });
        }catch(e){
            console.error(e);
            isGenerating = false
            status = ""
            alert("Chyba při zpracování dat");
            return;
        }

        status = "sending_data"
        const formData = new FormData();
        const data = JSON.stringify({
            osm_files: $selectedMapFiles,
            map_area: parsedAreas,
            map_preview_area: preview ? parsedPreviewAreas: null,
            paper_dimensions: $paperDimensions,
            paper_preview_dimensions: preview ? $paperPreviewDimensions : null,
            gpxs_groups: fileGroups,
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

        $gpxFiles.forEach(file => {
            formData.append("gpxs", file); 
            console.log(file);
        });

        formData.append('config', data);

        api.post(preview? "/generate_map_preview" : "/generate_map_normal", formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
        }).then((response) => {
            jwtToken = response.data.token
            status = response.data.status
            startPollingTaskInfo()
        }).catch((error) => {
            alert("Chyba při odesílání dat na server")
            status = ""
            isGenerating = false
            jwtToken = ""
            console.error(error)
        })
    }

    async function startPollingTaskInfo() {
        if (isPolling || jwtToken == null) return;
        isPolling = true;
        //first polling to keep generating alive - prevent task running if user close window before recieiving token
        api.get('/task_status', {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
            })
            
        pollingInterval = window.setInterval(async () => {
            api.get('/task_status', {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
            }).then((response) => {
                status = response.data.status
                if (response.data.status === 'completed') {
                    stopPollingTaskInfo();
                    downloadMap();
                }else if (response.data.status === 'failed') {
                    stopPollingTaskInfo();
                    status = ""
                    isGenerating = false
                    jwtToken = ""
                    alert("Generování mapy selhalo, zkuste to znovu později")
                }
            }).catch((error) => {
                status = ""
                isGenerating = false
                jwtToken = ""
                stopPollingTaskInfo();
                alert("Generování mapy bylo nečekaně přerušeno, zkuste to znovu později")
                console.error('Polling error:', error);
            });

        }, $displayedTabMapGenerating == "normalMap" ? normalPollingTime : previewPollingTime );
    }
    function stopPollingTaskInfo() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
        isPolling = false;
    }

    function downloadMap(){
        if(jwtToken == null || jwtToken == ""){
            alert("Chyba při stahování mapy")
            return
        }
        api.get("/download_map",{
        headers: {  
            'Authorization': `Bearer ${jwtToken}`
        },
            responseType: 'blob',
        }).then(response => {
            const blob = new Blob([response.data], { 
                type: response.headers['content-type'] 
            });
            const url = window.URL.createObjectURL(blob);
                        const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${$displayedTabMapGenerating == "normalMap" ? "mapa" : "nahled_mapy"}.pdf`);
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(link);
            jwtToken = ""
            terminateTask()
        }).catch(e => {
            terminateTask()
            alert("Chyba při stahování mapy")
            console.error(e);
        });
    }

    function terminateTask(){
        stopPollingTaskInfo();
        if(jwtToken != "" && jwtToken != null){
            api.post('/terminate_task', {token:jwtToken}, {
                headers: {
                    'Authorization': `Bearer ${jwtToken}`,
                    "Content-Type": "application/json"
                },
            }).then((response) => {
            }).catch((error) => {
                console.error("Termination error: ", error)
            })
        }
        status = ""
        isGenerating = false
        jwtToken = ""
    }
    
</script>

{#if isGenerating}
<div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white p-12 rounded-xl shadow-2xl text-center w-3/4 max-w-2xl space-y-6">
        <h1 class="text-2xl font-bold mb-4">{$displayedTabMapGenerating == "normalMap" ? "Generování mapy" : "Generování náhledové mapy" }</h1>
        <h2 class="text-lg font-semibold mb-4">{mapValue(mapGeneratingStatusMappingCZ, status)}</h2>
        <h3 class="text-md font-semibold mb-4">Dejte si kávičku a nevypínejte tuto záložku probíhá tvorba mapy.</h3>
        {#if status != MapGeneratingStatus.SENDING_DATA && status != MapGeneratingStatus.COMPLETED}
        <button 
            on:click={() =>{
                const confirmed = window.confirm("Opravdu chcete ukončit generování mapy?");
                if(!confirmed){
                    return;
                }else{
                    terminateTask()
                }}}
            class="mt-4 px-6 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
        >
           Ukončit generování
        </button>
      {/if}
  </div>
</div>
{/if}

<div class="container mx-auto p-4">
    <div class="flex flex-wrap -mb-px">
        <button 
         class= { $displayedTabMapGenerating == "normalMap" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
                "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                on:click={() => $displayedTabMapGenerating = "normalMap"}>
                Vytvoření celé mapy
        </button>
        <button 
         class= { $displayedTabMapGenerating == "previewMap" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
                "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                on:click={() => $displayedTabMapGenerating = "previewMap"}>
                Vytvoření náhledu mapy
        </button>
     
    </div>

    {#if $displayedTabMapGenerating == "normalMap"}
    <div class="space-y-4 rounded-lg bg-gray-100 ">
        <div class="space-y-4 rounded-lg bg-gray-100 flex justify-center items-center p-6">
            <button class="px-8 py-4 text-xl bg-green-500 text-white font-semibold rounded-lg shadow-lg hover:bg-green-600 transition"
            on:click={() => generateMap(false)}
            disabled={isGenerating}>
                Vytvořit mapu (pdf)
            </button>
        </div>
    </div>
    {:else if $displayedTabMapGenerating == "previewMap"}
   
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
                class="h-10 text-red-500 hover:text-red-700 flex items-center"
                on:click={() => removeArea(area.id)}
                  title="Odstranit oblast"
                >
                <Trash2 class="h-5 w-5 mr-2"/>
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
            <CirclePlus class="h-6 w-6 mr-2"/>
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
