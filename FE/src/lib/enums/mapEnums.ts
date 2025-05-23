/**
 * Enums used for map generation status.
 * @author Lukáš Kotoun, xkotou08
 */
export enum MapGeneratingStatus {
  FAILED = "failed",
  STARTING = "starting",
  IN_QUEUE = "in_queue",
  EXTRACTING = "extracting",
  LOADING = "loading",
  FILTERING = "filtering",
  STYLING = "styling",
  PREPARING_FOR_PLOTTING = "preparing_for_plotting",
  AREAS_PLOTTING = "areas_plotting",
  WAYS_PLOTTING = "ways_plotting",
  NODES_PLOTTING = "nodes_plotting",
  GPXS_PLOTTING = "gpxs_plotting",
  FILE_SAVING = "file_saving",
  COMPLETED = "completed",
  SENDING_DATA = "sending_data",
}
