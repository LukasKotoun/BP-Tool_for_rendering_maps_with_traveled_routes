<script lang="ts">
  import MapElementsManager from "$lib/managers/mapElementsManager.svelte";
  import AreaPaperManager from "$lib/managers/areaPaperManager.svelte";
  import GpxManager from "$lib/managers/gpxManager.svelte";
  import MapGeneratingManager from "$lib/managers/mapGeneratingManager.svelte";
  import logo from '$lib/imgs/logo.webp';
  import {
    checkFitPaper,
    parseWantedAreas,
    checkPaperDimensions,
  } from "$lib/utils/areaUtils";
  import { onMount } from "svelte";
  import api from "$lib/axios.config";
  import { Save, Upload, ChevronLeft, ChevronRight } from "@lucide/svelte";

  import {
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
    gpxStyles,
  } from "$lib/stores/mapStore";

  import {
    avilableMapThemes,
    avilableMapFiles,
  } from "$lib/stores/frontendStore";

  let displayedTab = "areaPaper";
  let canGoToNextPageBool = false;

  onMount(() => {
    api
      .get("/available_map_themes")
      .then((response) => {
        $avilableMapThemes = response.data.map_themes;
        if ($selectedMapTheme == "" && $avilableMapThemes.includes("mapycz")) {
          $selectedMapTheme = "mapycz";
        } else if (
          $selectedMapTheme != "" &&
          !$avilableMapThemes.includes($selectedMapTheme)
        ) {
          if ($avilableMapThemes.length > 0) {
            $selectedMapTheme = $avilableMapThemes[0];
          }
        }
      })
      .catch((error) => {
        alert(
          "Nepodařilo se načíst dostupné mapové podklady - nastaven výchozí podklad mapycz"
        );
        $selectedMapTheme = "mapycz";
        $avilableMapThemes = ["mapycz"];
        console.error(error);
      });

    api
      .get("/available_osm_files")
      .then((response) => {
        $avilableMapFiles = response.data.osm_files;
        if ($avilableMapFiles.includes("cz") && $selectedMapFiles.length == 0) {
          $selectedMapFiles = ["cz"];
        } else if ($selectedMapFiles.length != 0) {
          $selectedMapFiles = $selectedMapFiles.filter((file) =>
            $avilableMapFiles.includes(file)
          );
        }
      })
      .catch((error) => {
        alert(
          "Nepodařilo se načíst dostupné mapové soubory - nastaven výchozí soubor pro českou republiku"
        );
        if ($selectedMapFiles.length == 0) {
          $selectedMapFiles = ["cz"];
        }
        console.error("loading map files error", error);
      });
  });

  function saveToFile() {
    try {
      let gpxFilesGroupsFiltered = Object.fromEntries(
        Object.keys($gpxFileGroups).map((key) => [key, []])
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
        gpxStyles: $gpxStyles,
      };

      const jsonData = JSON.stringify(storeData, null, 2);

      const finalFilename = "map_settings.json";
      const blob = new Blob([jsonData], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = finalFilename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error saving store data to JSON:", error);
    }
  }

  function loadToStores(data: StoreData) {
    if (data.areasId != null) {
      $areasId = data.areasId;
    }
    if (data.wantedAreas != null) {
      $wantedAreas = data.wantedAreas;
    }
    if (data.areasPreviewId != null) {
      $areasPreviewId = data.areasPreviewId;
    }
    if (data.wantedPreviewAreas != null) {
      $wantedPreviewAreas = data.wantedPreviewAreas;
    }
    if (data.paperPreviewDimensions != null) {
      $paperPreviewDimensions = data.paperPreviewDimensions;
    }
    if (data.fitPaperSize != null) {
      $fitPaperSize = data.fitPaperSize;
    }
    if (data.paperDimensions != null) {
      $paperDimensions = data.paperDimensions;
    }
    if (data.paperDimensionsRequest != null) {
      $paperDimensionsRequest = data.paperDimensionsRequest;
    }
    if (data.automaticZoomLevel != null) {
      $automaticZoomLevel = data.automaticZoomLevel;
    }
    if (data.wantPlotTunnels != null) {
      $wantPlotTunnels = data.wantPlotTunnels;
    }
    if (data.wantPlotBridges != null) {
      $wantPlotBridges = data.wantPlotBridges;
    }
    if (data.peaksFilterSensitivity != null) {
      $peaksFilterSensitivity = data.peaksFilterSensitivity;
    }
    if (data.minPopulationFilter != null) {
      $minPopulationFilter = data.minPopulationFilter;
    }
    if (data.mapNodesElements != null) {
      $mapNodesElements = data.mapNodesElements;
    }
    if (data.mapWaysElements != null) {
      $mapWaysElements = data.mapWaysElements;
    }
    if (data.mapAreasElements != null) {
      $mapAreasElements = data.mapAreasElements;
    }
    if (data.mapElementsZoomDesign != null) {
      $mapElementsZoomDesign = data.mapElementsZoomDesign;
    }
    if (data.mapElementsWantedZoom != null) {
      $mapElementsWantedZoom = data.mapElementsWantedZoom;
    }
    if (data.gpxFileGroups != null) {
      $gpxFileGroups = data.gpxFileGroups;
    }
    if (data.gpxStyles != null) {
      $gpxStyles = data.gpxStyles;
    }
    if (data.selectedMapTheme != null) {
      //check if selectedMapTheme is in available map themes
      if ($avilableMapThemes.includes(data.selectedMapTheme)) {
        $selectedMapTheme = data.selectedMapTheme;
      } else {
        alert(
          "Mapový podklad z uloženého nastavení není dostupný. Nastaven výchozí podklad"
        );
      }
    }
    if (data.selectedMapFiles != null) {
      //check if selectedMapFiles are in available map files
      const selectedMapFilesFiltered = data.selectedMapFiles.filter((file) =>
        $avilableMapFiles.includes(file)
      );
      if (selectedMapFilesFiltered.length == data.selectedMapFiles.length) {
        $selectedMapFiles = data.selectedMapFiles;
      } else {
        alert(
          "Některé mapové data z uloženého nastavení nejsou dostupné, byly použity pouze dostupná data nebo výchozí data"
        );
        if (selectedMapFilesFiltered.length > 0) {
          $selectedMapFiles = selectedMapFilesFiltered;
        }
      }
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
          alert(
            "Nepodařilo se načíst nastavení ze souboru. Zkontrolujte formát JSON."
          );
        }
      };

      reader.onerror = () => {
        alert("Error reading file");
      };

      reader.readAsText(file);
    } catch (error) {
      alert("Chyba při načítání souboru");
    }
    input.value = "";
  }

  $: {
    displayedTab;
    $fitPaperSize;
    $paperDimensions;
    $wantedAreas;
    $selectedMapFiles;
    canGoToNextPageBool = canGoToNextPage() == "";
  }

  function canGoToNextPage(): string {
    if (displayedTab == "areaPaper") {
      if ($selectedMapFiles.length === 0) {
        return "Musí být vybrány alespoň jedny mapové data";
      }
      if (parseWantedAreas($wantedAreas).length === 0) {
        return "Musí být zadána alespoň jedna oblast";
      }
      if (!checkFitPaper($fitPaperSize)) {
        return "Šířka ohraničení vyplněné oblasti musí být vyplněna";
      }
      if (!checkPaperDimensions($paperDimensions, false)) {
        return "Rozměry papíru musí být vyplněny (pomocí 'Nastavit oblasti a papíru')";
      }
    }
    return "";
  }

  function handleNext(): void {
    let alertMessage = canGoToNextPage();
    if (alertMessage != "") {
      alert(alertMessage);
      return;
    }
    if (displayedTab == "areaPaper") {
      displayedTab = "gpx";
    } else if (displayedTab == "gpx") {
      displayedTab = "mapElements";
    } else if (displayedTab == "mapElements") {
      displayedTab = "generating";
    }
  }

  function handlePrevious(): void {
    if (displayedTab == "gpx") {
      displayedTab = "areaPaper";
    } else if (displayedTab == "mapElements") {
      displayedTab = "gpx";
    } else if (displayedTab == "generating") {
      displayedTab = "mapElements";
    }
  }
</script>

<div class="container mx-auto p-4">
  <div class="flex flex-col sm:flex-row items-center justify-between w-full p-4 bg-white border-b gap-4">
    <div class="flex items-center w-full sm:w-auto justify-center sm:justify-start">
      <img
        src={logo}
        alt="Logo"
        class="w-10 h-10 mr-2"/>
      <h1 class="text-lg font-medium">GeoPrint</h1>
    </div>
    <div class="flex space-x-2 justify-center sm:justify-end w-full sm:w-auto">
      <button
        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        on:click={saveToFile}
      >
        <div class="flex items-center">
          <Save class="w-5 h-5 mr-2" />
          Uložit nastavení
        </div>
      </button>
      {#if displayedTab == "areaPaper"}
        <button
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          on:click={() => document.getElementById("file-input").click()}
        >
          <div class="flex items-center">
            <Upload class="w-5 h-5 mr-2" />
            Nahrát nastavení
          </div>
        </button>
      {/if}

      <input
        id="file-input"
        type="file"
        accept=".json,application/json"
        on:change={loadJsonObjectFromFile}
        class="hidden"
      />
    </div>
  </div>
  <div class="border-b border-gray-700">
    <div class="flex flex-wrap -mb-px">
      <button
        class={displayedTab == "areaPaper"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg "
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg"}
        on:click={() => (displayedTab = "areaPaper")}
      >
        Nastavení oblasti a papíru
      </button>
      <button
        disabled={["areaPaper"].includes(displayedTab)}
        class={displayedTab == "gpx"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg "
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg"}
        class:text-gray-400={["areaPaper"].includes(displayedTab)}
        on:click={() => (displayedTab = "gpx")}
      >
        Nastavení a nahrání tras (gpx)
      </button>
      <button
        disabled={["areaPaper", "gpx"].includes(displayedTab)}
        class={displayedTab == "mapElements"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg"
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg"}
        class:text-gray-400={["areaPaper", "gpx"].includes(displayedTab)}
        on:click={() => {
          displayedTab = "mapElements";
        }}
      >
        Nastavení mapových prvků
      </button>
      <button
        disabled={["areaPaper", "gpx", "mapElements"].includes(displayedTab)}
        class={displayedTab == "generating"
          ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg"
          : "inline-block p-4 border-b-2 border-transparent rounded-t-lg"}
        class:text-gray-400={["areaPaper", "gpx", "mapElements"].includes(
          displayedTab
        )}
        on:click={() => (displayedTab = "generating")}
      >
        Vygenerování mapy
      </button>
    </div>
  </div>

  {#if displayedTab == "areaPaper"}
    <AreaPaperManager />
  {:else if displayedTab == "gpx"}
    <GpxManager />
  {:else if displayedTab == "mapElements"}
    <MapElementsManager />
  {:else if displayedTab == "generating"}
    <MapGeneratingManager />
  {/if}

  <div
    class={`flex ${displayedTab == "areaPaper" ? "justify-end" : "justify-between"}  p-4`}
  >
    {#if displayedTab != "areaPaper"}
      <button
        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        on:click={handlePrevious}
      >
        <div class="flex items-center">
          <ChevronLeft class="w-5 h-5 mr-2" />
          Zpět
        </div>
      </button>
    {/if}
    {#if displayedTab != "generating"}
      <button
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        class:bg-gray-400={!canGoToNextPageBool}
        class:hover:bg-gray-400={!canGoToNextPageBool}
        on:click={handleNext}
      >
        <div class="flex items-center">
          Další
          <ChevronRight class="w-5 h-5 ml-2" />
        </div>
      </button>
    {/if}
  </div>
</div>
