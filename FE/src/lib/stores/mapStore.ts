import { writable } from "svelte/store";
import { nodesMapElements, waysMapElements, areasMapElements, gpxDefaultStyles } from "$lib/constants";
import { createUniqueFileName } from "$lib/utils/gpxFilesUtils";

//areas
export const areasId = writable<number>(0);
export const wantedAreas = writable<AreaItemStored[]>([]);

//paper
export const fitPaperSize = writable<FitPaperSize>({
  fit: false,
  plot: false,
  width: 0.5,
});
export const paperDimension = writable<PaperDimension>({ width: 0, height: 0 });
export const paperDimensionRequest = writable<PaperDimensionRequest>({
  orientation: "automatic",
  given_smaller_dimension: true,
});
// elements
export const automaticZoomLevel = writable<number>(undefined);
export const wantPlotTunnels = writable<boolean>(true);
export const wantPlotBridges = writable<boolean>(false);
export const peaksFilterSensitivity = writable<number>(2.5);
export const minPopulationFilter = writable<number>(0);

export const mapNodesElements = writable<MapElementCategory>(JSON.parse(JSON.stringify(nodesMapElements)))

export const mapWaysElements = writable<MapElementCategory>(JSON.parse(JSON.stringify(waysMapElements)))

export const mapAreasElements = writable<MapElementCategory>(JSON.parse(JSON.stringify(areasMapElements)))

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

//gpx
function createGpxFileStore(){
  const { subscribe, update, set } = writable<File[]>([]);
  return {
    subscribe,
    addFiles: (newFiles: File[]) => {
      update(existingFiles => {
        let changedFiles = []
        const filesToAdd = newFiles
          .filter(file => file.name.toLowerCase().endsWith('.gpx'))
          .map(file => {
            newFiles = newFiles.filter(f => f !== file)
            const allFiles = [
              ...existingFiles.map(gpxFile => gpxFile), // fully stored files
              ...newFiles, // unprocessed files
              ...changedFiles // processed files
            ];
            const uniqueFile = createUniqueFileName(allFiles, file)
            changedFiles.push(uniqueFile)
            return uniqueFile;
          });

        return [...existingFiles, ...filesToAdd];
      });
    },
    removeFile: (fileName: string) => {
      update(files => files.filter(file => file.name !== fileName));
    },
    reset: () => set([]),
  };

}

// gpx styles
export const gpxFiles = createGpxFileStore()

// store to settings without files in array
export const gpxFileGroups = writable<GPXFileGroups>({});

export const gpxStyles = writable<GpxStyles>({
  group: {
    "default": JSON.parse(JSON.stringify(gpxDefaultStyles))
  },
})

