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

interface GpxStyleAttributes {
  color?: string | null;
  width?: number;
  alpha?: number;
  zindex?: number;
  linestyle?: string;
  line_capstyle?: string;
  edge_color?: string | null ;
  edge_alpha?: number;
  edge_width_ratio?: number;
  edge_linestyle?: string;
  edge_capstyle?: string;
  gpx_above_text?: boolean;
  start_marker?: string | null;
  start_marker_width?: number;
  start_marker_edge_ratio?: number;
  start_marker_color?: string;
  start_marker_alpha?: number;
  start_marker_edge_color?: string;
  finish_marker?: string | null;
  finish_marker_width?: number;
  finish_marker_edge_ratio?: number;
  finish_marker_color?: string;
  finish_marker_alpha?: number;
  finish_marker_edge_color?: string;
  marker_layer_position?: string;
}
interface GPXFileGroups {
  [groupName: string]: string[];
}
interface GpxStyles {
  general: GpxStyleAttributes;
  group: {[groupName: string]: GpxStyleAttributes};
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

interface GPXFile {
  id: number;
  file: File;
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