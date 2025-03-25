<script lang="ts">
    import { gpxFiles, gpxStyles } from '$lib/stores/mapStore';
    import { gpxGeneralDefault } from '$lib/constants';
    import { FileX, FileText, FileUp } from '@lucide/svelte';
    import GpxGeneralStylesManager from '$lib/managers/gpxGeneralStylesManager.svelte';
    import GpxCategoryStylesManager from './gpxCategoryStylesManager.svelte';

    let fileInput: HTMLInputElement;
    let dragOver = false;
    let displayedTab = 'groupStyle'

    function handleFileSelect(event: Event) {
      const input = event.target as HTMLInputElement;
      if (input.files) {
        gpxFiles.addFiles(Array.from(input.files));
        // Reset file input
        if (fileInput) fileInput.value = '';
      }
    }
  
    function handleDragOver(event: DragEvent) {
      event.preventDefault();
      dragOver = true;
    }
  
    function handleDragLeave() {
      dragOver = false;
    }
  
    function handleDrop(event: DragEvent) {
      event.preventDefault();
      dragOver = false;
      
      if (event.dataTransfer?.files) {
        gpxFiles.addFiles(Array.from(event.dataTransfer.files));
      }
    }
  
    function removeFile(id: number) {
      gpxFiles.removeFile(id);
    }

    function resetGeneralToDefault() {
      $gpxStyles.general = JSON.parse(JSON.stringify(gpxGeneralDefault));
    }

    const LINESTYLES = ['-', '--', '- -'];
    const CAPSTYLES = ['round', 'butt', 'projecting'];
    const CAPSTYLE_MAPPING_CZ = {
      round: 'Zaoblený ()',
      butt: 'Useknutý []',
      projecting: 'Prodloužený useknutý [ ]'
    };
    const MARKER_LAYER_POSITIONS = ['above_text', 'under_text'];
    const MARKER_LAYER_POSITION_MAPPING_CZ = {
      above_text: 'Nad textem',
      under_text: 'Pod textem'
    };
    const MARKERS = ['finish', 'start', null];
    const MARKER_MAPPING_CZ= {
      null: 'Žádná',
      start: 'Start - kolečko/bod', 
      finish: 'Cíl - vlajka'
    };

  </script>
    <div class="container mx-auto p-4">
      <h1 class="text-2xl font-bold mb-4">Náhrání tras a nastavení vzhledu</h1>
      <div class="text-md text-center text-gray-500 border-b border-gray-200 dark:text-gray-400 dark:border-gray-700">
        <div class="flex flex-wrap -mb-px">
              <button 
               class= { displayedTab == "upload" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg ":
                      "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                      on:click={() => displayedTab = "upload"}>
                      Náhrání GPX souborů
              </button>
              <button  class= { displayedTab == "globalStyle" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
                      "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                      on:click={() => displayedTab = "globalStyle"}>
                      Obecný vzhled
              </button>
              <button class= { displayedTab == "groupStyle" ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg":
                      "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
                      on:click={() => displayedTab = "groupStyle"}>
                      Skupiny
              </button>
        </div>
      </div>
    {#if displayedTab == "upload"}
    <div class="space-y-4 rounded-lg bg-gray-100 ">
      <div class="p-4 flex flex-wrap gap-4 items-start">
            <div 
            role="none"
              class="w-full mx-auto p-6 bg-white rounded-lg shadow-md"
              on:dragover={handleDragOver}
              on:dragleave={handleDragLeave}
              on:drop={handleDrop}
            >
              <div 
                class={`
                  border-2 border-dashed rounded-lg p-8 text-center transition-colors 
                  ${dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
                `}
              >
                <input 
                  type="file" 
                  multiple 
                  accept=".gpx"
                  bind:this={fileInput}
                  on:change={handleFileSelect}
                  class="hidden"
                  id="gpx-file-input"
                />
                <label 
                  for="gpx-file-input" 
                  class="cursor-pointer flex flex-col items-center space-y-4"
                >
                  <FileUp class="w-12 h-12 text-gray-500" />
                  <p class="text-gray-600">
                    Přetáhněte soubory nebo 
                    <span class="text-blue-600 hover:underline">klikněte pro vybrání</span>
                  </p>
                </label>
              </div>
            
              {#if $gpxFiles.length > 0}
                <div class="mt-6">
                  <h2 class="text-lg font-semibold mb-4">Nahrané soubory</h2>
                  <ul class="space-y-2">
                    {#each $gpxFiles as file (file.id)}
                      <li 
                        class="flex items-center justify-between p-3 bg-gray-100 rounded-lg"
                      >
                        <div class="flex items-center space-x-3">
                          <FileText class="w-6 h-6 text-gray-500" />
                          <span class="text-gray-700">{file.file.name}</span>
                        </div>
                        <button 
                          on:click={() => removeFile(file.id)}
                          class="text-red-500 hover:bg-red-100 p-2 rounded-full"
                          title="Remove file"
                        >
                          <FileX class="w-5 h-5" />
                        </button>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}
            </div>
        </div>
      </div>
    {:else if displayedTab == "globalStyle"}
    <GpxGeneralStylesManager />
    {:else if displayedTab == "groupStyle"}
    <GpxCategoryStylesManager />
    {/if}

    </div>
