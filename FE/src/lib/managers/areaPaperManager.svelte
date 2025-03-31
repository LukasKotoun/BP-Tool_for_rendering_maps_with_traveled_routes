<script lang="ts">
  import { onMount } from "svelte";
  import {
    wantedAreas,
    fitPaperSize,
    paperDimensions,
    paperDimensionsRequest,
    automaticZoomLevel,
    areasId,
    selectedMapFiles,
    mapElementsZoomDesign,
    mapElementsWantedZoom,
  } from "$lib/stores/mapStore";

  import {
    displayedTabMapAreas,
    settingAreaAndPaper,
    gettingMapBorders,
    avilableMapFiles,
  } from "$lib/stores/frontendStore";

  import api from "$lib/axios.config";
  import {
    checkMapCordinatesFormat,
    checkFitPaper,
    parseWantedAreas,
    numberOfAreaPlots,
    searchAreaWhisper,
    checkPaperDimensions,
  } from "$lib/utils/areaUtils";
  import { paperSizes, mapDataNamesMappingCZ } from "$lib/constants";
  import { mapValue } from "$lib/utils/mapElementsUtils";
  import { Trash2, CirclePlus } from "@lucide/svelte";
  import InfoToolTip from "$lib/components/infoToolTip.svelte";
  import LoadingSpinner from "$lib/components/loadingSpinner.svelte";

  let areaSuggestions: string[][] = [];
  const defaultWidth = 0.45;
  let numberOfAreasPlotVar = 0;

  let debounceTimeout: ReturnType<typeof setTimeout> | null = null;
  let mapFileSearchTerm = "";

  onMount(() => {
    if ($wantedAreas.length === 0) {
      const newArea: AreaItemStored = {
        id: $areasId++,
        area: "Česko",
        plot: true,
        width: defaultWidth,
        group: 0,
      };
      $wantedAreas = [newArea];
    }
  });

  function addArea() {
    const newArea: AreaItemStored = {
      id: $areasId++,
      area: "",
      plot: true,
      width: defaultWidth,
    };
    $wantedAreas = [...$wantedAreas, newArea];
  }

  function removeArea(id: number) {
    $wantedAreas = $wantedAreas.filter((area) => area.id !== id);
  }

  function handleSelectedPaperSizeChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    const selectedSize = JSON.parse(selectedValue) as PaperDimensions;
    $paperDimensionsRequest.width = selectedSize.width;
    $paperDimensionsRequest.height = selectedSize.height;
  }

  function changeGroupWidth(
    group: number | undefined,
    width: number | undefined
  ): void {
    if (group == null || group <= 0 || width == null) {
      return;
    }
    $wantedAreas = $wantedAreas.map((area) =>
      area.group != null && area.group > 0 && area.group === group
        ? { ...area, width: width }
        : area
    );
  }

  function getJoinedGroupWidth(
    group: number | undefined,
    myWidth: number | undefined,
    myId: number
  ): number {
    if (myWidth == null) {
      return defaultWidth;
    }
    if (group == null || group <= 0) {
      return myWidth;
    }
    const groupAreas = $wantedAreas.filter((area) => area.group === group);
    if (groupAreas.length === 0) {
      return myWidth;
    }
    for (let area of groupAreas) {
      if (area.id !== myId) {
        return area.width ?? myWidth;
      }
    }
    return myWidth;
  }

  function getPaperAndZoom() {
    let parsedAreas;
    try {
      if (!checkPaperDimensions($paperDimensionsRequest, true)) {
        alert("Alespoň jede z rozměrů papíru musí být vyplněn");
        return;
      }

      parsedAreas = parseWantedAreas($wantedAreas);
      if (parsedAreas.length === 0) {
        alert("Musí být zadána alespoň jedna oblast");
        return;
      }
    } catch (e) {
      console.error(e);
      alert("Chyba při zpracování souřadnic oblastí");
      return;
    }
    $settingAreaAndPaper = true;
    api
      .post(
        "/paper_and_zoom",
        {
          map_area: parsedAreas,
          paper_dimensions: {
            width:
              $paperDimensionsRequest.width === undefined
                ? null
                : $paperDimensionsRequest.width,
            height:
              $paperDimensionsRequest.height === undefined
                ? null
                : $paperDimensionsRequest.height,
          },
          given_smaller_paper_dimension:
            $paperDimensionsRequest.given_smaller_dimension,
          wanted_orientation: $paperDimensionsRequest.orientation,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((response) => {
        $paperDimensions.height = response.data.height;
        $paperDimensions.width = response.data.width;
        $automaticZoomLevel = response.data.zoom_level;
        if ($automaticZoomLevel != undefined) {
          $mapElementsZoomDesign.nodes = $automaticZoomLevel;
          $mapElementsZoomDesign.ways = $automaticZoomLevel;
          $mapElementsZoomDesign.areas = $automaticZoomLevel;
          $mapElementsZoomDesign.general = $automaticZoomLevel;
          $mapElementsWantedZoom.nodes = $automaticZoomLevel;
          $mapElementsWantedZoom.ways = $automaticZoomLevel;
          $mapElementsWantedZoom.areas = $automaticZoomLevel;
        }

        $settingAreaAndPaper = false;
      })
      .catch((e) => {
        console.error(e);
        if (e.response?.status === 400) {
          alert("Některé zadané oblasti nemají správný formát");
        } else if (e.response?.status === 404) {
          alert("Některou se zadaných oblastí se nepodařilo nalézt");
        } else {
          alert(
            "Nastala chyba při zpracování požadavku, zkuste to znovu za chvíli"
          );
        }
        $settingAreaAndPaper = false;
      });
  }

  async function getMapBorders() {
    let parsedAreas;
    try {
      if (!checkPaperDimensions($paperDimensions, false)) {
        alert("Alespoň jede z rozměrů papíru musí být vyplněn");
        return;
      }

      if (!checkFitPaper($fitPaperSize)) {
        alert("Šířka ohraničení vyplněné oblasti musí být vyplněna");
        return;
      }

      parsedAreas = parseWantedAreas($wantedAreas);
      if (parsedAreas.length === 0) {
        alert("Musí být zadána alespoň jedna oblast");
        return;
      }
    } catch (e) {
      console.error(e);
      alert("Chyba při zpracování oblasti a papíru");
      return;
    }
    $gettingMapBorders = true;

    api
      .post(
        "/generate_map_borders",
        {
          map_area: parsedAreas,
          paper_dimensions: $paperDimensions,
          fit_paper_size: $fitPaperSize,
        },
        {
          responseType: "blob",
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((response) => {
        const blob = new Blob([response.data], {
          type: response.headers["content-type"],
        });
        const url = window.URL.createObjectURL(blob);

        // Create a temporary link element to trigger the download
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "mapa_okraje.pdf");
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
        $gettingMapBorders = false;
      })
      .catch((e) => {
        if (e.response?.status === 400) {
          alert("Některé zadané oblasti nemají správný formát");
        } else if (e.response?.status === 404) {
          alert("Některou se zadaných oblastí se nepodařilo nalézt");
        } else {
          alert(
            "Nastala chyba při zpracování požadavku, zkuste to znovu za chvíli"
          );
        }
        console.error("Getting map areas borders: " + e);
        $gettingMapBorders = false;
      });
  }

  $: filteredMapFiles = $avilableMapFiles.filter(
    (file) =>
      (file.toLowerCase().includes(mapFileSearchTerm.toLowerCase()) &&
        !$selectedMapFiles.includes(file)) ||
      (mapValue(mapDataNamesMappingCZ, file)
        .toLowerCase()
        .includes(mapFileSearchTerm.toLowerCase()) &&
        !$selectedMapFiles.includes(file))
  );

  function addMapFile(file: string) {
    $selectedMapFiles = [...$selectedMapFiles, file];
  }

  function removeMapFile(file: string) {
    $selectedMapFiles = $selectedMapFiles.filter((item) => item !== file);
  }

  function debounceSearchArea(query: string, id: number) {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(async () => {
      searchAreaWhisper(query)
        .then((areas) => {
          areaSuggestions[id] = areas;
        })
        .catch((e) => {
          console.error(e);
        });
    }, 200);
  }

  function selectAreaSuggestion(newAreaValue: string, id: number): void {
    $wantedAreas = $wantedAreas.map((area) =>
      area.id === id ? { ...area, area: newAreaValue } : area
    );
    areaSuggestions[id] = [];
    areaSuggestions = [...areaSuggestions]; // Trigger reactivity
  }
  $: {
    numberOfAreasPlotVar = numberOfAreaPlots($wantedAreas);
  }
</script>

<div class="container mx-auto p-4">
  <div class="border-b dark:text-gray-400 border-gray-200 dark:border-gray-700">
    <div class="flex flex-wrap -mb-px">
      <button
        class={$displayedTabMapAreas == "mapData"
          ? "inline-block p-4 text-black border-b-2 border-blue-600 rounded-t-lg "
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300"}
        on:click={() => ($displayedTabMapAreas = "mapData")}
      >
        Mapová data <InfoToolTip
          width="w-60"
          borderColor={$displayedTabMapAreas == "mapData"
            ? "border-gray-600"
            : "border-gray-300"}
          text="Vyberte mapová data, která budou použity pro vytvoření mapy.
             Například pro Českou republiku s přizpůsobením na papír je potřeba vybrat mapová data pro ČR a okolní země, které se na papíru mohou zobrazit
             tedy: Česko, Slovensko, Polsko, Rakousko a Německo."
        />
      </button>
      <button
        class={$displayedTabMapAreas == "area"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg "
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
        on:click={() => ($displayedTabMapAreas = "area")}
      >
        Oblasti
        <InfoToolTip
          borderColor={$displayedTabMapAreas == "area"
            ? "border-gray-600"
            : "border-gray-300"}
          text="Oblasti, které budou vykresleny na mapě"
        />
      </button>
      <button
        class={$displayedTabMapAreas == "paper"
          ? "inline-block p-4 text-black border-b-2 border-blue-600 rounded-t-lg"
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
        on:click={() => ($displayedTabMapAreas = "paper")}
      >
        Papír
        <InfoToolTip
          borderColor={$displayedTabMapAreas == "paper"
            ? "border-gray-600"
            : "border-gray-300"}
          text="Papír (Velikost papíru) na který bude mapa vykreslená"
        />
      </button>
    </div>
  </div>
  {#if $displayedTabMapAreas == "mapData"}
    <div class="space-y-4 p-4 rounded-lg bg-gray-100">
      <div class="p-2 flex flex-wrap gap-4 items-start">
        <h2 class="text-xl font-bold mb-2">Vybraná mapová data :</h2>
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
          <p
            class="flex items-center mt-1 px-2 py-1 rounded text-sm text-gray-500"
          >
            Žádná mapová data nebyla vybrána
          </p>
        {/if}

        <input
          type="text"
          bind:value={mapFileSearchTerm}
          placeholder="Vyhledat mapová data..."
          class="w-full rounded p-2 mb-2"
        />
        <p>Dostupná data:</p>
        <div class="w-full border rounded max-h-100 overflow-y-auto">
          {#each filteredMapFiles as mapFile}
            <div
              role="button"
              tabindex="0"
              on:keydown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  addMapFile(mapFile);
                }
              }}
              class="p-2 bg-white hover:bg-gray-100 cursor-pointer"
              on:click={() => addMapFile(mapFile)}
            >
              {mapValue(mapDataNamesMappingCZ, mapFile)}
            </div>
          {:else}
            <div class="bg-white p-2 text-gray-500">
              {mapFileSearchTerm == ""
                ? "Žádná další dostupná data"
                : "Žádná data neodpovídají vyhledávání"}
            </div>
          {/each}
        </div>
      </div>
    </div>
  {:else if $displayedTabMapAreas == "area"}
    <div class="space-y-4 p-4 rounded-lg bg-gray-100">
      {#each $wantedAreas as area (area.id)}
        <div class="p-4 flex flex-wrap gap-4 items-start">
          <!-- Area Input -->
          <div
            class="flex flex-col"
            tabindex="0"
            role="button"
            on:blur={() => {
              areaSuggestions[area.id] = [];
              areaSuggestions = [...areaSuggestions];
            }}
          >
            <p class="text-sm font-medium mb-1">
              Oblast <InfoToolTip
                text="Zadajte názve oblasti (např. Brno, Česko nebo Třebíč, Česká Republika), 
                nebo minimálně 3 souřadnice tvořící polygon ve formátu 'zeměpisná delka,zeměpisná šiřka;delka,šiřka;delka,šiřka'
                 (příklad souřadnic pro ČR. 16.3776, 49.31; 16.6, 49.3; 16.4,49.1)"
                position="right"
                size="sm"
              />
            </p>
            <input
              type="text"
              class="border rounded-sm p-2 w-60"
              bind:value={area.area}
              on:keyup={() => {
                if (area.area.includes(";")) {
                  areaSuggestions[area.id] = [];
                  areaSuggestions = [...areaSuggestions];
                } else {
                  debounceSearchArea(area.area, area.id);
                }
              }}
            />

            {#if areaSuggestions[area.id]?.length > 0}
              <div
                class="relative top-full left-0 w-60 mt-1 bg-white border rounded-sm shadow-lg z-10 max-h-60 overflow-y-auto"
              >
                {#each areaSuggestions[area.id] as displayName}
                  <div
                    role="button"
                    tabindex="0"
                    on:keydown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        selectAreaSuggestion(displayName, area.id);
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
            {#if checkMapCordinatesFormat(area.area) != ""}
              <p class="text-red-500 text-sm">
                {checkMapCordinatesFormat(area.area)} <InfoToolTip
                text=" Pokud jsou souřadnice neplatné, považují se za oblast podle názvu. 
                Pokud tedy zadáváte název oblasti nikoliv souřadnice, tuto chybu můžete ignorovat."
                position="right"
                size="sm"
              />
              </p>
            {/if}
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
                on:change={() => changeGroupWidth(area?.group, area.width)}
                min="0.05"
                step="0.1"
                bind:value={area.width}
              />
            </div>

            {#if $wantedAreas.length > 1 && numberOfAreasPlotVar > 1}
              <!-- Group Select -->
              <div class="flex flex-col">
                <p class="text-sm font-medium mb-1">
                  Skupina oblastí <InfoToolTip
                    text="U oblastí ve stejné skupině nebudou vykresleny společné okraje oblastí."
                    position="right"
                    size="sm"
                  />
                </p>
                <select
                  class="border rounded-sm p-2 w-40"
                  bind:value={area.group}
                  on:change={() =>
                    (area.width = getJoinedGroupWidth(
                      area?.group,
                      area.width,
                      area.id
                    ))}
                >
                  <option value={0}>Žádná</option>
                  {#each Array.from({ length: numberOfAreasPlotVar }, (_, i) => i) as group}
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
                class="h-10 text-red-500 hover:text-red-700 flex items-center"
                on:click={() => removeArea(area.id)}
                title="Odstranit oblast"
              >
                <Trash2 class="h-5 w-5 mr-2" />
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
          <CirclePlus class="h-5 w-5 mr-2" />
          Přidat další oblast
        </button>
      </div>
      <div class="p-4 flex flex-wrap gap-4 items-end">
        <div class="flex flex-col">
          <p class="text-sm font-medium mb-1">
            Vyplnit papír okolím oblastí <InfoToolTip
              text="Upraví (rozšíří) vybranout oblast tak, aby vyplnila celý papír."
              position="right"
              size="sm"
            />
          </p>
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
            <p class="text-sm font-medium mb-1">
              Vykreslit ohraničení vyplněné oblasti <InfoToolTip
                text="Vykreslí okraje na obvodu papíru."
                position="right"
                size="sm"
              />
            </p>
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
  {:else if $displayedTabMapAreas == "paper"}
    <!-- paper  -->
    <div class="p-4 space-y-4 mt-4 rounded-lg bg-gray-100">
      <div class="p-4 flex flex-wrap gap-4 items-end">
        <div class="flex flex-col">
          <p class="text-sm font-medium mb-1">
            Velikost papíru <InfoToolTip
              text="Pokud je u vlastního papíru vyplněn pouze jeden rozměr, druhý bude po stisknutí tlačítka 'Nastavit oblasti a papír' dopočítán,
        na základě zvolené oblasti."
              position="right"
              size="sm"
            />
          </p>
          <select on:change={handleSelectedPaperSizeChange}>
            {#each paperSizes as paper}
              <option
                value={paper.value}
                selected={((JSON.parse(paper.value) as PaperDimensions).width ==
                  $paperDimensionsRequest.width &&
                  (JSON.parse(paper.value) as PaperDimensions).height ==
                    $paperDimensionsRequest.height) ||
                  ((JSON.parse(paper.value) as PaperDimensions).width ==
                    $paperDimensionsRequest.height &&
                    (JSON.parse(paper.value) as PaperDimensions).height ==
                      $paperDimensionsRequest.width)}
              >
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
          <p class="text-sm font-medium mb-1">
            Orientace papíru <InfoToolTip
              text="Při automatické orientaci papíru bude zvolena orientace, která nejlépe odpovídá zadaným oblastem."
              position="right"
              size="sm"
            />
          </p>
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
            <p class="text-sm font-medium mb-1">
              Zadán menší rozměr papíru <InfoToolTip
                text="Pokud je zvolena tato možnost, zadaný rozměr bude při dopočítávání brán jako minimální velikost papíru, jinak jako maximální."
                position="right"
                size="sm"
              />
            </p>
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
          Výsledná velikost papíru : {$paperDimensions.width}mm x {$paperDimensions.height}mm
          (šířka x výška) <InfoToolTip
            text="Velikost papíru která bude použita pro generování, nastaví se po stisknutí tlačítka 'Nastavit oblasti a papír'."
            position="right"
            size="sm"
          />
        </p>
      </div>
    </div>
  {/if}
  <div class="flex justify-end">
    {#if $displayedTabMapAreas == "paper" || $displayedTabMapAreas == "area"}
      <div class="p-4 flex justify-end">
        <button
          class="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-lg ml-4"
          class:bg-gray-500={$settingAreaAndPaper}
          class:hover:bg-gray-600={$settingAreaAndPaper}
          on:click={getPaperAndZoom}
          disabled={$settingAreaAndPaper}
        >
          <LoadingSpinner isVisible={$settingAreaAndPaper} speed="fast" />
          Nastavit oblasti a papír
        </button>
      </div>
      {#if checkPaperDimensions($paperDimensions, false) && checkFitPaper($fitPaperSize) && parseWantedAreas($wantedAreas).length > 0}
        <button
          class="text-white px-4 py-2 rounded-lg ml-4 mt-4"
          class:bg-green-500={!$gettingMapBorders}
          class:hover:bg-green-600={!$gettingMapBorders}
          class:bg-gray-500={$gettingMapBorders}
          class:hover:bg-gray-600={$gettingMapBorders}
          on:click={getMapBorders}
          disabled={$gettingMapBorders}
        >
          <LoadingSpinner isVisible={$gettingMapBorders} />
          Prohlédnou okraje oblastí <br />(vytvořit PDF)
        </button>
      {/if}
    {/if}
  </div>
</div>
