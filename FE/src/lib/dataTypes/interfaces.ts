interface AreaItemStored {
  id: number;
  area: string;
  plot: boolean;
  width?: number;
  group?: number;
}

interface AreaItemSend {
  area: string | number[][];
  plot: boolean;
  width?: number;
  group?: number;
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

interface NominatimResult {
  place_id: number;
  licence: string;
  osm_type: string;
  osm_id: number;
  boundingbox: string[];
  lat: string;
  lon: string;
  display_name: string;
  class: string;
  type: string;
  importance: number;
}