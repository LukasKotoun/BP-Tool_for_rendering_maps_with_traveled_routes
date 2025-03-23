<script lang="ts">
    import { onMount } from 'svelte';
  
    type Category = 0 | 1 | 2 | 3 | 4 | 5;
  
    interface AreaItem {
      id: number;
      area: string;
      plot: boolean;
      width?: number;
      category?: Category;
    }

    interface PaperDimensionRequest {
      width?: number;
      height?: number;
      orientation: "portrait" | "landscape" | "automatic";
      given_smaller_dimension?: boolean;
    }

    interface PaperDimension {
      width: number;
      height: number;
    }

    interface FitPaperSize {
      fit: boolean;
      plot: boolean;
      width?: number;
     }
     
    const paperSizes = [
    { label: "Vlastní", value: JSON.stringify({ width: null, height: null }) },
    { label: "A0 (1189 × 841 mm)", value: JSON.stringify({ height: 841, width: 1189 }) },
    { label: "A1 (841 × 594 mm)", value: JSON.stringify({ height: 594, width: 841 }) },
    { label: "A2 (594 × 420 mm)", value: JSON.stringify({ height: 420, width: 594 }) },
    { label: "A3 (420 × 297 mm)", value: JSON.stringify({ height: 297, width: 420 }) },
    { label: "A4 (297 × 210 mm)", value: JSON.stringify({ height: 210, width: 297 }) },
    { label: "A5 (297 × 148 mm)", value: JSON.stringify({ height: 148, width: 210 }) },
    { label: "A6 (148 × 105 mm)", value: JSON.stringify({ height: 105, width: 148 }) },
  ];

    let fitPaperSize: FitPaperSize = {
      fit: false,
      plot: false,
      width: 1.5
    };
    
    let dataValidatedOnBe = false;
    let finalPaperDimensions: PaperDimension = {
      width: 0,
      height: 0
    };
    let areas: AreaItem[] = [];
    let paperRequestData: PaperDimensionRequest = {
      orientation: "automatic",
      given_smaller_dimension: false
    };
    let paperCustomSize = false
    let nextId = 0;

    onMount(() => {
      addArea();
    });
    

    // Function to add a new area
    function addArea() {
      const newArea: AreaItem = {
        id: nextId++,
        area: "",
        plot: true,
        width: 1.5
      };
      areas = [...areas, newArea];
    }
  
    // Function to remove an area
    function removeArea(id: number) {
      areas = areas.filter(area => area.id !== id);
    }

    function handleSelectedPaperSizeChange(event: Event) {
      const selectedValue = (event.target as HTMLSelectElement).value;
      const selectedSize = JSON.parse(selectedValue) as PaperDimension; 
      paperRequestData.width = selectedSize.width;
      paperRequestData.height = selectedSize.height;
      if(selectedSize.width == null && selectedSize.height == null){
        paperCustomSize = true;
      }
    }

    function checkPaperDimensionRequest(request: PaperDimensionRequest): boolean {
      if(request.width == null && request.height == null){
        return false;
      }
      
      if(request.width == null || request.height == null && request.given_smaller_dimension == null){
        return false;
      }
      
      return true;
    }
  
    // Function to parse coordinates string into array
    function parseWantedArea(input: string): number[][] | string {
        if(!input.includes(';')){
          return input
        }

      const pairs = input.trim().split(';');

      // Check if this might be a single coordinate without semicolons
      if (pairs.length === 1 && !pairs[0].includes(',')) {
        throw new Error("Invalid format: coordinates must be pairs of x,y values");
      }
      
      let coordinates = pairs.map(pair => {
        const values = pair.split(',');
        
        if (values.length !== 2) {
          throw new Error(`Invalid coordinate pair: ${pair} - must have exactly two values separated by comma`);
        }
        
        const x = parseFloat(values[0]);
        const y = parseFloat(values[1]);
        
        if (isNaN(x) || isNaN(y)) {
          throw new Error(`Invalid numbers in pair: ${pair}`);
        }
        
        return [x, y];
      });

      if(coordinates.length < 3){
        throw new Error("Area polygon must have at least 3 points");
      }
      return coordinates;

    }
  
    // Function to get output without IDs
    function parseWantedAreas(areas: AreaItem[]): {
      area: string | number[][];
      plot: boolean;
      width?: number;
      category?: number;
    }[] {
      // remove id and parse area if have cordinates
      let areasParsed = areas.map(area => {
        if(area.area.trim() !== ""){
          const {id, ...rest} = area

            let parsedArea = parseWantedArea(area.area);
            return {
            ...rest,
            area: parsedArea
          };
        }else{
          return null;
        }}).filter(area => area !== null);

        return areasParsed;
    }
  
    // Get maximum category for an area
    function numberOfAreaPlots(): number {
      let count: number = 0;
      areas.forEach(area => {
        if (area.plot){
          count++;
        }
      }); 
      return count;
    }
  
    function getPaperAndZoom() {
      let outputAreas
      try{
        outputAreas = parseWantedAreas(areas);
        
      }catch(e){
        console.error(e);
        alert("Chyba při zpracování souřadnic");
        return;
      }
      
      console.log(fitPaperSize);
      console.log(outputAreas);
      if(checkPaperDimensionRequest(paperRequestData)){
        console.log(paperRequestData);
    }else{
      alert("Není zadán rozměr papíru");
      return;
    }
  }
    function getMapBorders() {
      let outputAreas
      try{
        outputAreas = parseWantedAreas(areas);
        
      }catch(e){
        console.error(e);
        alert("Chyba při zpracování souřadnic");
        return;
      }
      
      console.log(fitPaperSize);
      console.log(outputAreas);
      if(checkPaperDimensionRequest(paperRequestData)){
        console.log(paperRequestData);
    }else{
      alert("Není zadán rozměr papíru");
      return;
    }
  }
</script>
  
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Mapové oblasti a nastavení papíru</h1>
    <div class="space-y-4 rounded-lg bg-gray-100 ">
      <h2 class="p-2 text-xl font-bold">Mapové oblasti</h2>
      {#each areas as area (area.id)}
        <div class="p-4">
          <div class="flex flex-wrap gap-4 items-end">
            <!-- Area Input -->
            <div class="flex flex-col">
              <p class="text-sm font-medium mb-1">Oblast</p>
              <input
                type="text" 
                class="border rounded p-2 w-60"
                bind:value={area.area}
              />
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
                  
                  min="0.1" 
                  step="0.1"
                  bind:value={area.width} 
                />
              </div>
              
            {#if areas.length > 1 && numberOfAreaPlots() > 1}
              <!-- Category Select -->
              <div class="flex flex-col">
                <p class="text-sm font-medium mb-1">Skupina oblastí</p>
                <select
                  class="border rounded p-2 w-40"
                  bind:value={area.category}
                >
                  <option value={0}>Žádná</option>
                  {#each Array.from({length: numberOfAreaPlots()}, (_, i) => i) as category}
                    {#if category > 0}
                      <option value={category}>Skupina {category}</option>
                    {/if}
                  {/each}
                </select>
              </div>
              {/if}
            {/if}
            
            <!-- Remove Button - hidden for first item -->
            {#if areas.length > 1}
              <button 
                class="inline-flex items-center justify-center h-10 w-10 text-red-500 hover:text-red-700"
                on:click={() => removeArea(area.id)}
                title="Odstranit oblast"
              >
                Odstranit 
              </button>
            {/if}
          </div>
        </div>
      {/each}
      <div class="p-4">
        <button 
        class="flex items-center bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          on:click={addArea}
        >
          Přidat oblast
        </button>
      </div>
      <div class="p-4 flex flex-wrap gap-4 items-end">
        <div class="flex flex-col">
          <p class="text-sm font-medium mb-1">Vyplnit papír okolím oblastí</p>
            <div class="h-10 flex items-center">
              <input 
                type="checkbox" 
                class="h-5 w-5 items-center rounded-lg"
                bind:checked={fitPaperSize.fit} 
              />
            </div>
        </div>
        {#if  fitPaperSize.fit}
        <div class="flex flex-col">
          <p class="text-sm font-medium mb-1">Vykreslit ohraničení vyplněné oblasti</p>
            <div class="h-10 flex items-center">
              <input 
                type="checkbox" 
                class="h-5 w-5 items-center rounded-lg"
                bind:checked={fitPaperSize.plot} 
              />
            </div>
        </div>
        {#if fitPaperSize.plot}
        <div class="flex flex-col">
          <p class="text-sm font-medium mb-1">Šířka ohraničení (v mm)</p>
                <input 
                  type="number" 
                  class="border rounded p-2 w-20"
                  min="0.1" 
                  step="0.1"
                  bind:value={fitPaperSize.width} 
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
          bind:value={paperRequestData.width}
          min="10"
          step="10"
        />
      </div>
      <div class="flex flex-col">
        <p class="text-sm font-medium mb-1">Výška (v mm)</p>
          <input
          type="number"
          class="border rounded p-2 w-20"
          bind:value={paperRequestData.height}
          min="10"
          step="10"
        />
      </div>
      <div class="flex flex-col">
        <p class="text-sm font-medium mb-1">Orientace papíru</p>
        <select
          class="border rounded p-2 w-40"
          bind:value={paperRequestData.orientation}
        >
          <option value="automatic">Automatická</option>
          <option value="portrait">Na výšku</option>
          <option value="landscape">Na šířku</option>
        </select>
      </div>
      {#if paperRequestData.width == null || paperRequestData.height == null}
      <div class="flex flex-col">
        <p class="text-sm font-medium mb-1">Zadán menší rozměr papíru</p>
          <div class="h-10 flex items-center">
            <input 
              type="checkbox" 
              class="h-5 w-5 items-center rounded-lg"
              bind:checked={paperRequestData.given_smaller_dimension} 
            />
          </div>
      </div>
      {/if}
      
    </div>
    <div class="p-4 flex justify-end">
    <button 
    class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded ml-4  mt-4"
    on:click={getPaperAndZoom}
  >
    Nastavit oblasti a papír
  </button>
</div>

    <div class="p-4">
      <p class="text-sm font-medium mb-1">
      Výsledná velikost papíru: {finalPaperDimensions.width}mm x {finalPaperDimensions.height}mm (šířka x výška)
        </p>
    </div>
      
      </div>
      <div class = "flex justify-end">
        {#if finalPaperDimensions.width > 0 && finalPaperDimensions.height > 0}
        <button 
          class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded ml-4  mt-4"
          on:click={getMapBorders}
        >
          Prohlédnou oblasti
      </button>
      {/if}
      
        
    </div>
    </div>
