import { writable } from "svelte/store";
import { nodesMapElements, waysMapElements, areasMapElements } from "$lib/constants";

export const wantedAreas = writable<AreaItemStored[]>([]);
export const fitPaperSize = writable<FitPaperSize>({
  fit: false,
  plot: false,
  width: 0.5,
});
export const areasId = writable<number>(0);
export const paperDimension = writable<PaperDimension>({ width: 0, height: 0 });
export const paperDimensionRequest = writable<PaperDimensionRequest>({
  orientation: "automatic",
  given_smaller_dimension: true,
});

export const automaticZoomLevel = writable<number>(undefined);

export const wantPlotTunnels = writable<boolean>(true);

export const wantPlotBridges = writable<boolean>(false);

export const peaksFilterSensitivity = writable<number>(2.5);

export const minPopulationFilter = writable<number>(0);


export const mapNodesElements = writable<MapElementCategory>(nodesMapElements)

export const mapWaysElements = writable<MapElementCategory>(waysMapElements)

export const mapAreasElements = writable<MapElementCategory>(areasMapElements)

// default always available theme
export const wantedMapTheme = writable<string>("mapycz")

export const mapElementsZoomDesign = writable<MapElementsZoomDesign>({
  general: 1,
  nodes: 1,
  ways: 1,
  areas: 1,
})

export const mapElementsWantedZoom = writable<MapElementsWanted>({
  nodes: 1,
  ways: 1,
  areas: 1,
})
