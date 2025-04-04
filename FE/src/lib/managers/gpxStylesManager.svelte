<script lang="ts">
  import { gpxStyles } from "$lib/stores/mapStore";
  import { displayedTabGpxGroupsStyle } from "$lib/stores/frontendStore";
  import { mapValue } from "$lib/utils/mapElementsUtils";
  import InfoToolTip from "$lib/components/infoToolTip.svelte";
  import {
    gpxDefaultStyles,
    LINESTYLES,
    CAPSTYLES,
    MARKER_LAYER_POSITIONS,
    MARKERS,
    CAPSTYLE_MAPPING_CZ,
    MARKER_MAPPING_CZ,
    MARKER_LAYER_POSITION_MAPPING_CZ,
  } from "$lib/constants";


  const minMM = 0.05;
  const minRange = 0;
  const maxRatio = 5;
  const maxAlpha = 1;

  let defaultColor = JSON.parse(JSON.stringify(gpxDefaultStyles)).color;
  function resetGroupToDefault(groupName: string) {
    $gpxStyles.group[groupName] = JSON.parse(JSON.stringify(gpxDefaultStyles));
  }
</script>

<div class="p-6 bg-gray-100">
  <div
    class="text-md text-center text-gray-500 border-b border-gray-200 dark:text-gray-400 dark:border-gray-700"
  >
    <div class="flex flex-wrap -mb-px">
      {#each Object.entries($gpxStyles.group) as [groupName, styles]}
        <button
          class={$displayedTabGpxGroupsStyle == groupName
            ? "inline-block p-4 text-black  border-b-2 border-blue-600 rounded-t-lg "
            : "inline-block p-4 border-b-2 border-transparent rounded-t-lg hover:text-gray-600 hover:border-gray-300 "}
          on:click={() => ($displayedTabGpxGroupsStyle = groupName)}
        >
          {groupName != "default" ? groupName : "Nezařazené"}
        </button>
      {/each}
    </div>
  </div>
  {#each Object.entries($gpxStyles.group) as [groupName, styles]}
    {#if $displayedTabGpxGroupsStyle == groupName}
      <div class="mx-auto bg-white shadow-md rounded-lg p-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Main Line Attributes -->
          <div class="space-y-6 bg-gray-50 p-4 rounded">
            <h3 class="text-xl font-semibold border-b pb-2">Hlavní vzhled</h3>
            <div class="flex items-center space-x-4">
              <p class="w-1/3">Vykreslit:</p>
              <input
                type="checkbox"
                checked={$gpxStyles.group[groupName].color != null}
                class="w-5 h-5 items-center rounded-lg"
                on:change={() =>
                  ($gpxStyles.group[groupName].color = $gpxStyles.group[
                    groupName
                  ].color
                    ? null
                    : defaultColor)}
              />
            </div>
            <div class="flex items-center space-x-4">
              <p class="w-1/3">Barva:</p>
              {#if $gpxStyles.group[groupName].color == null}
                <input type="color" class="w-full h-10" disabled />
              {:else}
                <input
                  type="color"
                  bind:value={$gpxStyles.group[groupName].color}
                  class="w-full h-10"
                />
              {/if}
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Šířka (v mm):</p>
              <input
                type="number"
                min={minMM}
                step="0.1"
                bind:value={$gpxStyles.group[groupName].width}
                class="w-full p-2 border rounded"
              />
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Viditelnost:</p>
              <input
                type="range"
                min={minRange}
                max={maxAlpha}
                step="0.1"
                bind:value={$gpxStyles.group[groupName].alpha}
                class="w-full"
              />
              <span>{$gpxStyles.group[groupName].alpha.toFixed(1)}</span>
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">
                Z-index: <InfoToolTip
                  text="Pozice vrstvy oproti ostatním skupinám. Čím vyšší číslo, tím výše je vrstva vykreslena (přes ostatní)."
                  position="right"
                  size="sm"
                />
              </p>
              <input
                type="number"
                min={minRange}
                step="1"
                value={$gpxStyles.group[groupName].zindex}
                class="w-full p-2 border rounded"
              />
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Styl čáry:</p>
              <select
                bind:value={$gpxStyles.group[groupName].linestyle}
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
                bind:value={$gpxStyles.group[groupName].line_capstyle}
                class="w-full p-2 border rounded"
              >
                {#each CAPSTYLES as style}
                  <option value={style}
                    >{mapValue(CAPSTYLE_MAPPING_CZ, style)}</option
                  >
                {/each}
              </select>
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Vykreslit přes texty:</p>
              <input
                type="checkbox"
                bind:checked={$gpxStyles.group[groupName].gpx_above_text}
                class="w-5 h-5 items-center rounded-lg"
              />
            </div>
          </div>

          <!-- Edge Attributes -->
          <div class="space-y-6 bg-gray-50 p-4 rounded">
            <h3 class="text-xl font-semibold border-b pb-2">Vzhled okrajů</h3>
            <div class="flex items-center space-x-4">
              <p class="w-1/3">Vykreslit:</p>
              <input
                type="checkbox"
                checked={$gpxStyles.group[groupName].edge_color != null}
                class="w-5 h-5 items-center rounded-lg"
                on:change={() =>
                  ($gpxStyles.group[groupName].edge_color = $gpxStyles.group[
                    groupName
                  ].edge_color
                    ? null
                    : defaultColor)}
              />
            </div>
            <div class="flex items-center space-x-4">
              <p class="w-1/3">Barva:</p>
              {#if $gpxStyles.group[groupName].edge_color == null}
                <input type="color" class="w-full h-10" disabled />
              {:else}
                <input
                  type="color"
                  bind:value={$gpxStyles.group[groupName].edge_color}
                  class="w-full h-10"
                />
              {/if}
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Viditelnost:</p>
              <input
                type="range"
                min={minRange}
                max={maxAlpha}
                step="0.1"
                bind:value={$gpxStyles.group[groupName].edge_alpha}
                class="w-full"
              />
              <span>{$gpxStyles.group[groupName].edge_alpha.toFixed(1)}</span>
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Poměr okraje k hlavní velikosti:</p>
              <input
                type="range"
                min={minRange}
                max={maxRatio}
                step="0.1"
                bind:value={$gpxStyles.group[groupName].edge_width_ratio}
                class="w-full"
              />
              <span
                >{$gpxStyles.group[groupName].edge_width_ratio.toFixed(1)}</span
              >
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Styl okraje:</p>
              <select
                bind:value={$gpxStyles.group[groupName].edge_linestyle}
                class="w-full"
              >
                {#each LINESTYLES as style}
                  <option value={style}>{style}</option>
                {/each}
              </select>
            </div>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Styl konců okrajů:</p>
              <select
                bind:value={$gpxStyles.group[groupName].edge_capstyle}
                class="w-full p-2 border rounded"
              >
                {#each CAPSTYLES as style}
                  <option value={style}
                    >{mapValue(CAPSTYLE_MAPPING_CZ, style)}</option
                  >
                {/each}
              </select>
            </div>
          </div>

          <!-- Marker Attributes -->
          <div class="space-y-6 bg-gray-50 p-4 rounded">
            <h3 class="text-xl font-semibold border-b pb-2">
              Označení začátku a konce
            </h3>

            <div class="flex items-center space-x-4">
              <p class="w-1/3">Pozice ikon:</p>
              <select
                bind:value={$gpxStyles.group[groupName].marker_layer_position}
                class="w-full p-2 border rounded"
              >
                {#each MARKER_LAYER_POSITIONS as position}
                  <option value={position}
                    >{mapValue(
                      MARKER_LAYER_POSITION_MAPPING_CZ,
                      position
                    )}</option
                  >
                {/each}
              </select>
            </div>

            <!-- Start Marker Section -->
            <div class="space-y-6 border-t pt-4 mt-4">
              <h4 class="font-semibold mb-2">Označení začátku</h4>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Ikona:</p>
                <select
                  bind:value={$gpxStyles.group[groupName].start_marker}
                  class="w-full p-2 border rounded"
                >
                  {#each MARKERS as marker}
                    <option value={marker}
                      >{mapValue(MARKER_MAPPING_CZ, marker)}</option
                    >
                  {/each}
                </select>
              </div>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Velikost (v mm):</p>
                <input
                  type="number"
                  min={minMM}
                  step="0.1"
                  bind:value={$gpxStyles.group[groupName].start_marker_width}
                  class="w-full p-2 border rounded"
                />
              </div>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Barva:</p>
                <input
                  type="color"
                  bind:value={$gpxStyles.group[groupName].start_marker_color}
                  class="w-full h-10"
                />
              </div>

              <div class="flex items-center space-x-4">
                <p class="">Viditelnost:</p>
                <input
                  type="range"
                  min={minRange}
                  max={maxAlpha}
                  step="0.1"
                  bind:value={$gpxStyles.group[groupName].start_marker_alpha}
                  class="w-full"
                />
                <span
                  >{$gpxStyles.group[groupName].start_marker_alpha.toFixed(
                    1
                  )}</span
                >
              </div>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Barva okraje:</p>
                <input
                  type="color"
                  bind:value={
                    $gpxStyles.group[groupName].start_marker_edge_color
                  }
                  class="w-full h-10"
                />
              </div>
              <div class="flex items-center space-x-4">
                <p class="w-1/3">Poměr okraje:</p>
                <input
                  type="range"
                  min={minRange}
                  max="10"
                  step="0.1"
                  bind:value={
                    $gpxStyles.group[groupName].start_marker_edge_ratio
                  }
                  class="w-full"
                />
                <span
                  >{$gpxStyles.group[groupName].start_marker_edge_ratio.toFixed(
                    1
                  )}</span
                >
              </div>
            </div>

            <!-- Finish Marker Section -->
            <div class="border-t space-y-6 pt-4 mt-4">
              <h4 class="font-semibold mb-2">Označení konce</h4>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Ikona:</p>
                <select
                  bind:value={$gpxStyles.group[groupName].finish_marker}
                  class="w-full p-2 border rounded"
                >
                  {#each MARKERS as marker}
                    <option value={marker}
                      >{mapValue(MARKER_MAPPING_CZ, marker)}</option
                    >
                  {/each}
                </select>
              </div>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Velikost (v mm):</p>
                <input
                  type="number"
                  min={minMM}
                  step="0.1"
                  bind:value={$gpxStyles.group[groupName].finish_marker_width}
                  class="w-full p-2 border rounded"
                />
              </div>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Barva:</p>
                <input
                  type="color"
                  bind:value={$gpxStyles.group[groupName].finish_marker_color}
                  class="w-full h-10"
                />
              </div>

              <div class="flex items-center space-x-4">
                <p class="">Viditlenost:</p>
                <input
                  type="range"
                  min={minRange}
                  max={maxAlpha}
                  step="0.1"
                  bind:value={$gpxStyles.group[groupName].finish_marker_alpha}
                  class="w-full"
                />
                <span
                  >{$gpxStyles.group[groupName].finish_marker_alpha.toFixed(
                    1
                  )}</span
                >
              </div>

              <div class="flex items-center space-x-4">
                <p class="w-1/3">Barva okraje:</p>
                <input
                  type="color"
                  bind:value={
                    $gpxStyles.group[groupName].finish_marker_edge_color
                  }
                  class="w-full h-10"
                />
              </div>

              <div class="flex items-center space-x-4">
                <p>Poměr okraje:</p>
                <input
                  type="range"
                  min={minRange}
                  max={maxRatio}
                  step="0.1"
                  bind:value={
                    $gpxStyles.group[groupName].finish_marker_edge_ratio
                  }
                  class="w-full"
                />
                <span
                  >{$gpxStyles.group[
                    groupName
                  ].finish_marker_edge_ratio.toFixed(1)}</span
                >
              </div>
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-center space-x-4">
          <button
            on:click={() => resetGroupToDefault(groupName)}
            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            Obnovit na výchozí nastavení
          </button>
        </div>
      </div>
    {/if}
  {/each}
</div>
