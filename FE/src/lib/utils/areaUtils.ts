import axios from "axios";

export function checkMapCordinatesFormat(input: string): string {
    if(!input.includes(';')){
      return ""
    }else{
      const pairs = input.trim().split(';');

      if (pairs.length === 1 && !pairs[0].includes(',')) {
        return "Souřadnice musí být pary x, y (E, N) hodnot";
      }
      for (let pair of pairs) {
        const values = pair.split(',');
        
        if (values.length !== 2) {
        return "Souřadnice musí mít přesně 2 hodnoty oddělené středníkem (x,y; x,y; x,y)";
        }
        
        const x = parseFloat(values[0]);
        const y = parseFloat(values[1]);
        
        if (isNaN(x) || isNaN(y)) {
          return "Nevalidní čísla v souřadnicích"
        }
      }

      if(pairs.length < 3){
          return "Oblast se musí skládat alespoň ze 3 bodů";
      }
      return ""
    }
  }

export function checkFitPaper(fitPaperSize: FitPaperSize): boolean {
    if(fitPaperSize.plot == true && fitPaperSize.width == null){
      return false;
    }
    return true;
  }

// Function to parse coordinates string into array
export function parseWantedArea(input: string): number[][] | string {
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
export function parseWantedAreas(areas: AreaItemStored[]): AreaItemSend[] 
    {
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

// Get maximum groups for an area
export function numberOfAreaPlots(areas: AreaItemStored[]): number {
    let count: number = 0;
    areas.forEach(area => {
      if (area.plot){
        count++;
      }
    }); 
    return count;
  }

export async function searchAreaWhisper(query: string): Promise<string[]> {
  return new Promise((resolve, reject) => {
    if (!query || query.length < 1) {
      return resolve([]);
    }

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
        resolve(data.map(item => item.display_name) as string[]);
      }
    }).catch(e => {
      return reject(e);
    });
  });
  }