import { writable } from "svelte/store";
import { nodesMapElements, waysMapElements, areasMapElements, gpxGeneralDefault, defaultGpxGroupName } from "$lib/constants";
import { createUniqueFileName } from "$lib/utils/gpxFilesUtils";

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

//custom store for gpx file storing





function createGpxFileStore(){
  const { subscribe, update, set } = writable<GPXFile[]>([]);
  let counter = 0;
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
              ...existingFiles.map(gpxFile => gpxFile.file), // fully stored files
              ...newFiles, // unprocessed files
              ...changedFiles // processed files
            ];
            const uniqueFile = createUniqueFileName(allFiles, file)
            changedFiles.push(uniqueFile)
            return {
              id: counter++,
              file: uniqueFile
            };
          });

        return [...existingFiles, ...filesToAdd];
      });
    },
    removeFile: (id: number) => {
      update(files => files.filter(file => file.id !== id));
    },
    reset: () => set([]),
  };
}export const gpxFileGroups = writable<GPXFileGroups>({});

export const gpxFiles = createGpxFileStore()

export const gpxStyles = writable<GpxStyles>({
  general: {},
  group: {
    "default": JSON.parse(JSON.stringify(gpxGeneralDefault))
  },
})

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
