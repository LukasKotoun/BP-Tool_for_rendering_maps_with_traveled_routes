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

interface MapElementsZoomDesign {
  general: number;
  nodes: number;
  ways: number;
  areas: number;
}

interface MapElementsWanted {
  nodes: number;
  ways: number;
  areas: number;
}

interface MapElementAttributes {
  plot: boolean;
  width_scale?: number;
  text_scale?: number;
}

interface MapElementCategory {
  [key: string]: MapElementAttributes | MapElementCategory;
}


interface MapElementAttributesSend  {
  width_scale?: number;
  text_scale?: number;
}

interface MapElementCategorySend {
  [key: string]: MapElementAttributesSend | MapElementCategorySend;
}

interface MapElementUpdateRules {
  [key: string]: string[] | boolean;
}

type Dictionary = {
  [key: string]: string; // Define the dictionary as an object with string keys and string values
};

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