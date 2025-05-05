/**
 * Stores for frontend pages settings.
 * @author Lukáš Kotoun, xkotou08
 */
import { writable } from "svelte/store";

export const avilableMapThemes = writable<string[]>([]);
export const avilableMapFiles = writable<string[]>([]);

export const displayedTabMapAreas = writable<string>("mapData");
export const settingAreaAndPaper = writable<boolean>(false);
export const gettingMapBorders = writable<boolean>(false);

export const displayedTabGpxFiles = writable<string>("upload");
export const displayedTabGpxGroupsStyle = writable<string>("default");
export const displayedTabMapGenerating = writable<string>("normalMap");

export const displayedElementsCategory = writable<string>("nodes");
