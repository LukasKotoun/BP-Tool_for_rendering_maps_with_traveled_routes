import { writable } from "svelte/store";

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
