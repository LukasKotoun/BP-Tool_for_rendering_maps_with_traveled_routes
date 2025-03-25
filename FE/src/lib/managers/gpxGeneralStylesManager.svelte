<script lang="ts">
    import { gpxStyles } from '$lib/stores/mapStore';
    import { gpxGeneralDefault } from '$lib/constants';

    import {mapValue} from '$lib/utils/mapElementsUtils';


    function resetGeneralToDefault() {
      $gpxStyles.general = JSON.parse(JSON.stringify(gpxGeneralDefault));
    }

    // todo to constants
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

<div class="p-6 bg-gray-100 min-h-screen">
    <div class=" mx-auto bg-white shadow-md rounded-lg p-6">          
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Main Line Attributes -->
            <div class="space-y-4 bg-gray-50 p-4 rounded">
                <h3 class="text-xl font-semibold border-b pb-2">Hlavní vzhled</h3>
                <div class="flex items-center space-x-4">
                  <p class="w-1/3">Vykreslit:</p>
                  <input 
                      type="checkbox" 
                      checked={$gpxStyles.general.color != null}
                      class="w-5 h-5 items-center rounded-lg"
                      on:change="{() => $gpxStyles.general.color = $gpxStyles.general.color ? null : gpxGeneralDefault.color}"
                  />
              </div>
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Barva:</p>
                    <input 
                        type="color" 
                        bind:value={$gpxStyles.general.color} 
                        class="w-full h-10"
                    />
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Šířka (v mm):</p>
                    <input 
                        type="number" 
                        min="0.05" 
                        step="0.1" 
                        bind:value={$gpxStyles.general.width} 

                        class="w-full p-2 border rounded"
                    />
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Viditelnost:</p>
                    <input 
                        type="range" 
                        min="0" 
                        max="1" 
                        step="0.1" 
                        bind:value={$gpxStyles.general.alpha} 
                        class="w-full"
                    />
                    <span>{$gpxStyles.general.alpha.toFixed(1)}</span>
                </div>
                
                <!-- <div class="flex items-center space-x-4">
                    <p class="w-1/3">Z-index:</p>
                    <input 
                        type="number" 
                        min="0" 
                        step="1"
                        value={$gpxStyles.general.zindex} 

                        class="w-full p-2 border rounded"
                    />
                </div> -->
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Styl čáry:</p>
                    <select 
                    bind:value={$gpxStyles.general.linestyle}

                        class="w-full p-2 border rounded"
                    >
                        {#each LINESTYLES as style}
                            <option value={style}>{style}</option>
                        {/each}
                    </select>
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Styl konců čáry:</p>
                    <select
                    bind:value={$gpxStyles.general.line_capstyle}

                        class="w-full p-2 border rounded"
                    >
                        {#each CAPSTYLES as style}
                            <option value={style}>{mapValue(CAPSTYLE_MAPPING_CZ,style)}</option>
                        {/each}
                    </select>
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Vykreslit přes texty:</p>
                    <input 
                        type="checkbox" 
                        checked={$gpxStyles.general.gpx_above_text}

                        class="w-5 h-5 items-center rounded-lg"
                    />
                </div>
            </div>

            <!-- Edge Attributes -->
            <div class="space-y-4 bg-gray-50 p-4 rounded">
                <h3 class="text-xl font-semibold border-b pb-2">Vzhled okrajů</h3>
                <div class="flex items-center space-x-4">
                  <p class="w-1/3">Vykreslit:</p>
                  <input
                      type="checkbox" 
                      checked={$gpxStyles.general.edge_color != null}
                      class="w-5 h-5 items-center rounded-lg"
                      on:change="{() => $gpxStyles.general.edge_color = $gpxStyles.general.edge_color ? null : gpxGeneralDefault.color}"
                  />
              </div>
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Barva:</p>
                    <input 
                        type="color" 
                        bind:value={$gpxStyles.general.edge_color} 

                        class="w-full h-10"
                    />
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Viditelnost:</p>
                    <input 
                        type="range" 
                        min="0" 
                        max="1" 
                        step="0.1" 
                        bind:value={$gpxStyles.general.edge_alpha} 

                        class="w-full"
                    />
                    <span>{$gpxStyles.general.edge_alpha.toFixed(1)}</span>
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Poměr okraje k hlavní velikosti:</p>
                    <input 
                        type="range" 
                        min="0"
                        max="10"  
                        step="0.1" 
                        bind:value={$gpxStyles.general.edge_width_ratio} 

                        class="w-full p-2 border rounded"
                    />
                     <span>{$gpxStyles.general.edge_width_ratio.toFixed(1)}</span>
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Styl okraje:</p>
                    <select 
                    bind:value={$gpxStyles.general.edge_linestyle}

                        class="w-full p-2 border rounded"
                    >
                        {#each LINESTYLES as style}
                            <option value={style}>{style}</option>
                        {/each}
                    </select>
                </div>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Styl konců okrajů:</p>
                    <select 
                    bind:value={$gpxStyles.general.edge_capstyle}

                        class="w-full p-2 border rounded"
                    >
                        {#each CAPSTYLES as style}
                        <option value={style}>{mapValue(CAPSTYLE_MAPPING_CZ, style)}</option>
                        {/each}
                    </select>
                </div>
            </div>

            <!-- Marker Attributes -->
            <div class="space-y-4 bg-gray-50 p-4 rounded ">
                <h3 class="text-xl font-semibold border-b pb-2">Označení začátku a konce</h3>
                
                <div class="flex items-center space-x-4">
                    <p class="w-1/3">Pozice ikon:</p>
                    <select 
                    bind:value={$gpxStyles.general.marker_layer_position}
                        class="w-full p-2 border rounded"
                    >
                        {#each MARKER_LAYER_POSITIONS as position}
                            <option value={position}>{mapValue(MARKER_LAYER_POSITION_MAPPING_CZ, position)}</option>
                        {/each}
                    </select>
                </div>

                <!-- Start Marker Section -->
                <div class="border-t pt-4 mt-4">
                    <h4 class="font-semibold mb-2">Označení začátku</h4>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Ikona:</p>
                        <select 
                        bind:value={$gpxStyles.general.start_marker}

                            class="w-full p-2 border rounded"
                        >
                            {#each MARKERS as marker}
                                <option value={marker}>{mapValue(MARKER_MAPPING_CZ, marker)}</option>
                            {/each}
                        </select>
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Velikost (v mm):</p>
                        <input 
                            type="number" 
                             min="0.05"
                            step="0.1" 
                            bind:value={$gpxStyles.general.start_marker_width} 

                            class="w-full p-2 border rounded"
                        />
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Barva:</p>
                        <input 
                            type="color" 
                            bind:value={$gpxStyles.general.start_marker_color} 

                            class="w-full h-10"
                        />
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="">Viditelnost:</p>
                        <input 
                            type="range" 
                            min="0" 
                            max="1" 
                            step="0.1" 
                            bind:value={$gpxStyles.general.start_marker_alpha} 

                            class="w-full p-2 border rounded"
                        />
                        <span>{$gpxStyles.general.start_marker_alpha.toFixed(1)}</span>
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Barva okraje:</p>
                        <input 
                            type="color" 
                            bind:value={$gpxStyles.general.start_marker_edge_color} 

                            class="w-full h-10"
                        />
                    </div>
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Poměr okraje:</p>
                        <input 
                        type="range" 
                        min="0"
                        max="10"  
                        step="0.1" 
                        bind:value={$gpxStyles.general.start_marker_edge_ratio} 

                        class="w-full p-2 border rounded"
                    />
                     <span>{$gpxStyles.general.start_marker_edge_ratio.toFixed(1)}</span>
                    </div>
                </div>

                <!-- Finish Marker Section -->
                <div class="border-t pt-4 mt-4">
                    <h4 class="font-semibold mb-2">Označení konce</h4>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Ikona:</p>
                        <select 
                        bind:value={$gpxStyles.general.finish_marker}

                            class="w-full p-2 border rounded"
                        >
                            {#each MARKERS as marker}
                            <option value={marker}>{mapValue(MARKER_MAPPING_CZ, marker)}</option>
                            {/each}
                        </select>
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Velikost (v mm):</p>
                        <input 
                            type="number" 
                            min="0.05"
                            step="0.1" 
                            bind:value={$gpxStyles.general.finish_marker_width} 

                            class="w-full p-2 border rounded"
                        />
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Barva:</p>
                        <input 
                            type="color" 
                            bind:value={$gpxStyles.general.finish_marker_color} 

                            class="w-full h-10"
                        />
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="">Viditlenost:</p>
                        <input 
                            type="range" 
                            min="0" 
                            max="1" 
                            step="0.1" 
                            bind:value={$gpxStyles.general.finish_marker_alpha} 
                            class="w-full p-2 border rounded"
                        />
                        <span>{$gpxStyles.general.finish_marker_alpha.toFixed(1)}</span>
                    </div>
                    
                    <div class="flex items-center space-x-4">
                        <p class="w-1/3">Barva okraje:</p>
                        <input 
                            type="color" 
                            bind:value={$gpxStyles.general.finish_marker_edge_color} 
                            class="w-full h-10"
                        />
                    </div>
                    
                    <div class="flex items-center space-x-4">
                      <p>Poměr okraje:</p>
                      <input 
                      type="range" 
                      min="0"
                      max="10"  
                      step="0.1" 
                      bind:value={$gpxStyles.general.finish_marker_edge_ratio} 
                      class="w-full p-2 border rounded"
                  />
                   <span>{$gpxStyles.general.finish_marker_edge_ratio.toFixed(1)}</span>
                    
                    </div>
                </div>
            </div>
        </div>
        
         <div class="mt-6 flex justify-center space-x-4">
            <button 
                on:click={resetGeneralToDefault}
                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
            >
                Obnovit na výchozí nastavení
            </button>
            
            <button 
                on:click={() => console.log(JSON.stringify($gpxStyles.general, null, 2))}
                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
            >
                Log Current Configuration
            </button>
        </div>
    </div>
</div>