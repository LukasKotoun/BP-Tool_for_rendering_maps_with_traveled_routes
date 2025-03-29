import { writable } from "svelte/store";

export const avilableMapThemes = writable<string[]>([]);
export const avilableMapFiles = writable<string[]>([]);

export const automaticZoomLevelChangedElements = writable<boolean>(false);

export const displayedTabMapAreas = writable<string>("mapData");
export const settingAreaAndPaper = writable<boolean>(false);
export const gettingMapBorders = writable<boolean>(false);


export const displayedTabGpxFiles = writable<string>("upload");
export const displayedTabGpxGroupsStyle = writable<string>("default");
export const displayedTabMapGenerating = writable<string>("normalMap");

