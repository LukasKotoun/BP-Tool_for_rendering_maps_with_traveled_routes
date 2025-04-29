from typing import Any

from config import CRS_OSM, CRS_DISPLAY, OUTPUT_PDF_FOLDER, OSM_TMP_FILE_FOLDER, DEFAULT_STYLE, MANDATORY_WAYS
from config import STYLES, FE_EDIT_STYLES_VALIDATION, ALLOWED_WANTED_ELEMENTS_STRUCTURE, FE_EDIT_STYLES_MAPPING, NODES_ALSO_FROM_AREA
from config import PLACES_TO_FILTER_BY_POPULATION, REQ_AREA_KEY_WITH_AREA, REQ_AREA_KEY_TO_GROUP_BY, REQ_AREA_KEY_WITH_BOOLEAN_PLOT
from common.map_enums import ProcessingStatus, SharedDictKeys, BaseConfigKeys, MapConfigKeys, MapThemeVariable, Style
from common.custom_types import DimensionsTuple
from modules.gdf_utils import GdfUtils
from geopandas import GeoDataFrame
from modules.utils import Utils
from modules.osm_data_parser import OsmDataParser
from modules.osm_data_preprocessor import OsmDataPreprocessor
from modules.style_assigner import StyleManager
from modules.plotter import Plotter
from modules.received_structure_processor import ReceivedStructureProcessor


def get_map_area_gdf(wanted_areas_to_display, boundary=False) -> tuple[GeoDataFrame, GeoDataFrame] | GeoDataFrame:
    """Get gdf with map area from wanted areas structure received from FE. Optionally return also gdf with boundaries of areas."""
    map_area_gdf = GdfUtils.get_whole_area_gdf(
        wanted_areas_to_display, REQ_AREA_KEY_WITH_AREA, CRS_OSM, CRS_DISPLAY)

    if (boundary):
        # ------------store bounds to plot and combine area rows in gdf to 1 row------------
        boundary_map_area_gdf = GdfUtils.get_areas_borders_gdf(
            GdfUtils.filter_rows(map_area_gdf, {REQ_AREA_KEY_WITH_BOOLEAN_PLOT: True, Style.WIDTH.value: ''}), REQ_AREA_KEY_TO_GROUP_BY)
        GdfUtils.remove_columns(boundary_map_area_gdf, [
                                boundary_map_area_gdf.geometry.name, Style.WIDTH.value], True)
    GdfUtils.remove_columns(map_area_gdf, [
                            map_area_gdf.geometry.name, Style.WIDTH.value], True)
    map_area_gdf = GdfUtils.combine_rows_gdf(map_area_gdf)
    if (boundary):
        return map_area_gdf, boundary_map_area_gdf
    return map_area_gdf


def process_bridges_and_tunnels(gdf: GeoDataFrame, want_bridges: bool, want_tunnels: bool):
    """Remove or keep bridges and tunnels in gdf. If not wanted any of it it will remove layer and both columns.
    Else it will remove not wanted columns and first set layer for that column to 0."""
    GdfUtils.change_columns_to_numeric(gdf, ['layer'])
    GdfUtils.fill_nan_values(gdf, ['layer'], 0)
    gdf['layer'] = gdf.get('layer', 0)

    # set layer to 0 if there is no bridge or tunnel
    gdf.loc[GdfUtils.get_rows_filter(
        gdf, {'tunnel': '~', 'bridge': '~'}), 'layer'] = 0
    if (not want_bridges and not want_tunnels):
        gdf['layer'] = 0
        GdfUtils.remove_columns(gdf, ['bridge', 'tunnel'])
    elif (not want_bridges):
        if ('layer' in gdf):
            # set layer to 0 in bridges - as normal ways
            gdf.loc[GdfUtils.get_rows_filter(
                gdf, {'bridge': ''}), 'layer'] = 0
        GdfUtils.remove_columns(gdf, ['bridge'])
    elif (not want_tunnels):
        if ('layer' in gdf):
            # set layer to 0 in tunnels - as normal ways
            gdf.loc[GdfUtils.get_rows_filter(
                gdf, {'tunnel': ''}), 'layer'] = 0
        GdfUtils.remove_columns(gdf, ['tunnel'])
    return


def convert_loaded_columns(gdf, numeric_columns, round_columns):
    GdfUtils.change_columns_to_numeric(gdf, numeric_columns)
    GdfUtils.convert_numeric_columns_int(gdf, round_columns)


def prepare_styled_columns_gpxs(gpxs_gdf: GeoDataFrame):
    """Preparing styled columns like multipling and creating derivated columns and setting default values."""
    GdfUtils.fill_nan_values(gpxs_gdf, [Style.ZINDEX.value], 0)
    GdfUtils.create_derivated_columns(gpxs_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
                                      Style.EDGE_WIDTH_RATIO.value])
    GdfUtils.create_derivated_columns(gpxs_gdf, Style.START_MARKER_EDGE_WIDTH.value, Style.START_MARKER_WIDTH.value, [
                                      Style.START_MARKER_EDGE_RATIO.value])
    GdfUtils.create_derivated_columns(gpxs_gdf, Style.FINISH_MARKER_EDGE_WIDTH.value, Style.FINISH_MARKER_WIDTH.value, [
                                      Style.FINISH_MARKER_EDGE_RATIO.value])

    GdfUtils.remove_columns(gpxs_gdf, [Style.START_MARKER_EDGE_RATIO.value, Style.FINISH_MARKER_EDGE_RATIO.value,
                                       Style.EDGE_WIDTH_RATIO.value])


def prepare_styled_columns_nodes(nodes_gdf: GeoDataFrame, config):
    """Prepareing styled columns like multipling and creating derivated columns and setting default values."""
    GdfUtils.fill_nan_values(nodes_gdf, [Style.ZINDEX.value], 0)

    GdfUtils.multiply_column_gdf(nodes_gdf, Style.WIDTH.value, [
        Style.FE_WIDTH_SCALE.value], None)
    GdfUtils.multiply_column_gdf(nodes_gdf, Style.TEXT_FONT_SIZE.value, [
                                 Style.FE_TEXT_FONT_SIZE_SCALE.value], None)
    # text outline
    GdfUtils.create_derivated_columns(nodes_gdf, Style.TEXT_OUTLINE_WIDTH.value, Style.TEXT_FONT_SIZE.value, [
                                      Style.TEXT_OUTLINE_WIDTH_RATIO.value])

    # edge - MARKER size and ways width
    GdfUtils.create_derivated_columns(nodes_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
                                      Style.EDGE_WIDTH_RATIO.value])
    old_column_remove = []
    for filter, new_column, old_column, fill in config[BaseConfigKeys.DERIVATE_COLUMNS]:
        GdfUtils.create_derivated_columns(
            nodes_gdf, new_column, old_column, filter=filter, fill=fill)
        old_column_remove.append(old_column)

    GdfUtils.remove_columns(nodes_gdf, [Style.FE_WIDTH_SCALE.value, Style.FE_TEXT_FONT_SIZE_SCALE.value,
                                        Style.EDGE_WIDTH_RATIO.value, Style.TEXT_OUTLINE_WIDTH_RATIO.value, *old_column_remove])


def prepare_styled_columns_ways(ways_gdf: GeoDataFrame, config):
    """Preparing styled columns like multipling and creating derivated columns and setting default values."""
    GdfUtils.fill_nan_values(ways_gdf, [Style.ZINDEX.value], 0)

    GdfUtils.multiply_column_gdf(ways_gdf, Style.WIDTH.value, [
        Style.FE_WIDTH_SCALE.value])

    GdfUtils.create_derivated_columns(ways_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
        Style.EDGE_WIDTH_RATIO.value])
    GdfUtils.create_derivated_columns(ways_gdf, Style.EDGE_WIDTH_DASHED_CONNECT.value, Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.value, [
        Style.WIDTH.value])
    GdfUtils.create_derivated_columns(ways_gdf, Style.BRIDGE_WIDTH.value, Style.WIDTH.value, [  # calc bridge size only for bridges
                                      Style.BRIDGE_WIDTH_RATIO.value], {'bridge': ''})
    GdfUtils.create_derivated_columns(ways_gdf, Style.BRIDGE_EDGE_WIDTH.value, Style.BRIDGE_WIDTH.value, [
                                      Style.BRIDGE_EDGE_WIDTH_RATIO.value], {'bridge': ''})

    old_column_remove = []
    for filter, new_column, old_column, fill in config[BaseConfigKeys.DERIVATE_COLUMNS]:
        GdfUtils.create_derivated_columns(
            ways_gdf, new_column, old_column, filter=filter, fill=fill)
        old_column_remove.append(old_column)
    GdfUtils.remove_columns(ways_gdf, [Style.FE_WIDTH_SCALE.value, Style.EDGE_WIDTH_RATIO.value, Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.value,
                                       Style.BRIDGE_WIDTH_RATIO.value, Style.BRIDGE_EDGE_WIDTH_RATIO.value, *old_column_remove])


def prepare_styled_columns_areas(areas_gdf: GeoDataFrame, config):
    """Preparing styled columns like multipling and creating derivated columns and setting default values."""
    GdfUtils.fill_nan_values(areas_gdf, [Style.ZINDEX.value], 0)

    GdfUtils.multiply_column_gdf(areas_gdf, Style.WIDTH.value, [
        Style.FE_WIDTH_SCALE.value])

    GdfUtils.create_derivated_columns(areas_gdf, Style.EDGE_WIDTH.value, Style.WIDTH.value, [
                                      Style.EDGE_WIDTH_RATIO.value])
    old_column_remove = []
    for filter, new_column, old_column, fill in config[BaseConfigKeys.DERIVATE_COLUMNS]:
        GdfUtils.create_derivated_columns(
            areas_gdf, new_column, old_column, filter=filter, fill=fill)
        old_column_remove.append(old_column)

    GdfUtils.remove_columns(areas_gdf, [Style.FE_WIDTH_SCALE.value,
                                        Style.EDGE_WIDTH_RATIO.value, *old_column_remove])


def calc_preview(map_area_gdf: GeoDataFrame, paper_dimensions_mm: DimensionsTuple, fit_paper_size: bool, preview_map_area_gdf: GeoDataFrame, preview_paper_dimensions_mm: DimensionsTuple) -> tuple[float, GeoDataFrame, GeoDataFrame, float]:
    """Calculate data for createing preview of big area in small area and small paper. 
    Create preview area gdf and from that area create preview that will fill whole paper and have same scale as normal map."""

    # calc scaling factor always from expanded are on paper - to get correct sizes of scaled objects
    if (fit_paper_size):
        map_area_gdf = GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm)
        map_area_dimensions = GdfUtils.get_dimensions_gdf(
            map_area_gdf)
        map_scaling_factor = Utils.calc_map_scaling_factor(
            map_area_dimensions, paper_dimensions_mm)
    else:
        map_area_dimensions = GdfUtils.get_dimensions_gdf(map_area_gdf)
        expanded_map_area_dimensions = GdfUtils.get_dimensions_gdf(GdfUtils.expand_gdf_area_fitPaperSize(
            map_area_gdf, paper_dimensions_mm))
        map_scaling_factor = Utils.calc_map_scaling_factor(expanded_map_area_dimensions,
                                                           paper_dimensions_mm)
    # calc bounds so area_zoom_preview will be 1 and will fill whole paper
    paper_fill_bounds = Utils.calc_bounds_to_fill_paper_with_ratio(preview_map_area_gdf.union_all().centroid,
                                                                   preview_paper_dimensions_mm, map_area_dimensions,
                                                                   paper_dimensions_mm)
    preview_map_area_gdf = GdfUtils.create_gdf_from_bounds(
        paper_fill_bounds, CRS_DISPLAY)
    # always from bigger area for correct elevation - and also send to FE při zjištování zoom levelu
    map_scale = Utils.get_scale(GdfUtils.get_bounds_gdf(
        GdfUtils.change_crs(map_area_gdf, CRS_OSM)), paper_dimensions_mm)

    return map_scaling_factor, preview_map_area_gdf, map_area_gdf, map_scale


def plot_map_borders(file_id, map_area_gdf, boundary_map_area_gdf, paper_dimension_mm, area_color):
    plotter = Plotter(map_area_gdf, paper_dimension_mm,
                      0, 0, None, 0, 0)

    plotter.init(area_color, None, False)

    plotter.area_boundary(boundary_map_area_gdf,
                          color="black")
    plotter.clip()

    folder = Utils.ensure_dir_exists(OUTPUT_PDF_FOLDER)

    pdf_name = f'{folder}bounds_{file_id}.pdf'
    plotter.generate_pdf(pdf_name)
    return pdf_name


def generate_map(config: dict[MapConfigKeys, any], task_id: str, shared_dict: dict[str, Any], lock) -> None:
    """Main function for generating map. It will create map from wanted areas and styles and save it to pdf file."""
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.EXTRACTING.value
        }
    map_area_gdf = config[MapConfigKeys.MAP_AREA.value]

    # extract area to new osm file
    osm_data_preprocessor = OsmDataPreprocessor(
        config[MapConfigKeys.OSM_FILES.value], OSM_TMP_FILE_FOLDER, task_id, shared_dict, lock)
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.FILES.value: [*shared_dict[task_id][SharedDictKeys.FILES.value], osm_data_preprocessor.osm_output_file],
        }

    osm_file = osm_data_preprocessor.extract_areas(
        config[MapConfigKeys.MAP_AREA.value], CRS_OSM)
    # prepare all structures
    wanted_categories, styles_size_edits = ReceivedStructureProcessor.transform_wanted_elements_to_backend_structures(
        config[MapConfigKeys.WANTED_CATEGORIES_AND_STYLE_EDIT.value], FE_EDIT_STYLES_VALIDATION.keys(),
        list(ALLOWED_WANTED_ELEMENTS_STRUCTURE.keys()), FE_EDIT_STYLES_MAPPING)

    map_theme, base_config = STYLES.get(
        config[MapConfigKeys.MAP_THEME.value], DEFAULT_STYLE)

    for var_name, var_value in map_theme['variables'].items():
        map_theme['variables'][var_name] = StyleManager.convert_variables_from_dynamic(
            var_value, config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['general'])

    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.LOADING.value
        }
    # get categories that are in wanted and also should be loaded from areas
    wanted_nodes_from_area = {
        key: [value for value in wanted_categories['nodes']
              [key] if value in NODES_ALSO_FROM_AREA[key]]
        for key in wanted_categories['nodes'] if key in NODES_ALSO_FROM_AREA
    }
    # ------------loading osm data------------
    osm_file_parser = OsmDataParser(
        wanted_categories['nodes'],
        wanted_nodes_from_area,
        {**wanted_categories['ways'], **MANDATORY_WAYS},
        wanted_categories['areas'],
        nodes_additional_columns=base_config['nodes'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        ways_additional_columns=base_config['ways'][BaseConfigKeys.ADDITIONAL_COLUMNS],
        areas_additional_columns=base_config['areas'][BaseConfigKeys.ADDITIONAL_COLUMNS]
    )

    nodes_gdf, ways_gdf, areas_gdf = osm_file_parser.create_gdf(
        osm_file, CRS_OSM, CRS_DISPLAY)
    gpxs_gdf = config[MapConfigKeys.GPXS.value]

    Utils.remove_file(osm_file)
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.FILTERING.value,
            SharedDictKeys.FILES.value: [file for file in shared_dict[task_id][SharedDictKeys.FILES.value] if file != osm_file],
        }

    if (config[MapConfigKeys.MAP_OUTER_AREA.value] is not None):
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, config[MapConfigKeys.MAP_OUTER_AREA.value])
    else:
        nodes_gdf = GdfUtils.get_rows_inside_area(
            nodes_gdf, config[MapConfigKeys.MAP_AREA.value])

    convert_loaded_columns(nodes_gdf, base_config['nodes']
                           [BaseConfigKeys.NUMERIC_COLUMNS], base_config['nodes'][BaseConfigKeys.ROUND_COLUMNS])
    convert_loaded_columns(ways_gdf, base_config['ways']
                           [BaseConfigKeys.NUMERIC_COLUMNS], base_config['ways'][BaseConfigKeys.ROUND_COLUMNS])
    convert_loaded_columns(areas_gdf, base_config['areas']
                           [BaseConfigKeys.NUMERIC_COLUMNS], base_config['areas'][BaseConfigKeys.ROUND_COLUMNS])

    # ------------prefiltering nodes by importance------------
    if (config[MapConfigKeys.PEAKS_FILTER_RADIUS.value] is not None
            and config[MapConfigKeys.PEAKS_FILTER_RADIUS.value] > 0):
        nodes_gdf = GdfUtils.filter_peaks(
            nodes_gdf,
            config[MapConfigKeys.PEAKS_FILTER_RADIUS.value])
    if (config[MapConfigKeys.MIN_PLACE_POPULATION.value] is not None
            and config[MapConfigKeys.MIN_PLACE_POPULATION.value] > 0):
        nodes_gdf = GdfUtils.filter_place_by_population(
            nodes_gdf, PLACES_TO_FILTER_BY_POPULATION, config[MapConfigKeys.MIN_PLACE_POPULATION.value])

    # get coastline and determine where is land and where water
    coast_gdf, ways_gdf = GdfUtils.filter_rows(
        ways_gdf, {'natural': 'coastline'}, compl=True)
    bg_gdf = GdfUtils.create_background_gdf(
        map_area_gdf, coast_gdf, map_theme['variables'][MapThemeVariable.WATER_COLOR.value],
        map_theme['variables'][MapThemeVariable.LAND_COLOR.value])

    process_bridges_and_tunnels(ways_gdf, config[MapConfigKeys.PLOT_BRIDGES.value],
                                config[MapConfigKeys.PLOT_TUNNELS.value])

    # Style objects
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.STYLING.value
        }
    ways_gdf = GdfUtils.merge_lines_gdf(ways_gdf, [])

    # assing zoom specific styles
    gpxs_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['gpxs'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['general'])
    nodes_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['nodes'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['nodes'])
    ways_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['ways'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['ways'])
    areas_styles = StyleManager.convert_from_dynamic(
        map_theme['styles']['areas'], config[MapConfigKeys.STYLES_ZOOM_LEVELS.value]['areas'])
    # combine styles
    gpxs_styles = [*config[MapConfigKeys.GPXS_STYLES.value], *gpxs_styles]
    nodes_styles = [*nodes_styles, *styles_size_edits['nodes']]
    ways_styles = [*ways_styles, *styles_size_edits['ways']]
    areas_styles = [*areas_styles, *styles_size_edits['areas']]

    map_scaling_factor = config[MapConfigKeys.MAP_SCALING_FACTOR.value]
    StyleManager.scale_styles(
        gpxs_styles, map_theme['variables'][MapThemeVariable.GPXS_STYLES_SCALE.value], map_scaling_factor)
    StyleManager.scale_styles(
        nodes_styles, map_theme['variables'][MapThemeVariable.NODES_STYLES_SCALE.value], map_scaling_factor)
    StyleManager.scale_styles(
        ways_styles, map_theme['variables'][MapThemeVariable.WAYS_STYLES_SCALE.value], map_scaling_factor)
    StyleManager.scale_styles(
        areas_styles, map_theme['variables'][MapThemeVariable.AREAS_STYLES_SCALE.value], map_scaling_factor)

    StyleManager.assign_styles(gpxs_gdf, gpxs_styles)
    StyleManager.assign_styles(
        nodes_gdf, nodes_styles, base_config['nodes'][BaseConfigKeys.DONT_CATEGORIZE])
    StyleManager.assign_styles(
        ways_gdf, ways_styles, base_config['ways'][BaseConfigKeys.DONT_CATEGORIZE])
    StyleManager.assign_styles(
        areas_gdf, areas_styles, base_config['areas'][BaseConfigKeys.DONT_CATEGORIZE])

    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.PREPARING_FOR_PLOTTING.value
        }

    # ------------prepare styled columns------------
    prepare_styled_columns_gpxs(gpxs_gdf)
    prepare_styled_columns_nodes(nodes_gdf, base_config['nodes'])
    prepare_styled_columns_ways(ways_gdf, base_config['ways'])
    prepare_styled_columns_areas(areas_gdf, base_config['areas'])

    # ------------filter nodes by min req------------
    nodes_gdf = GdfUtils.filter_nodes_min_req(nodes_gdf)

    areas_gdf['area_size'] = areas_gdf.geometry.area
    bg_gdf['area_size'] = bg_gdf.area

    # -----sort-----
    GdfUtils.sort_gdf_by_columns(
        bg_gdf, ['area_size'], ascending=False, na_position='last')

    # sort by population and ele - main sort is by zindex in plotter
    GdfUtils.sort_gdf_by_columns(
        nodes_gdf, ['population', 'ele'], ascending=False, na_position='last')

    # first by area (from biggest to smallest) and then by zindex smallest to biggest
    GdfUtils.sort_gdf_by_columns(
        areas_gdf, ['area_size'], ascending=False, na_position='last')
    GdfUtils.sort_gdf_by_columns(
        areas_gdf, [Style.ZINDEX.value], ascending=True, na_position='first', stable=True)

    # merge ways that should be ploted with areas
    areas_with_ways_filter = map_theme['variables'][MapThemeVariable.AREAS_WITH_WAYS_FILTER.value]
    areas_with_ways, areas_gdf = GdfUtils.filter_rows(
        areas_gdf,  areas_with_ways_filter[0], compl=True)
    areas_with_ways = GdfUtils.filter_rows(
        areas_with_ways, areas_with_ways_filter[1])
    if (not areas_with_ways.empty and not ways_gdf.empty):
        ways_gdf = GdfUtils.combine_gdfs([ways_gdf, areas_with_ways])

    # ------------plot------------
    plotter = Plotter(map_area_gdf, config[MapConfigKeys.PAPER_DIMENSION_MM.value],
                      map_theme['variables'][MapThemeVariable.TEXT_BOUNDS_OVERFLOW_THRESHOLD.value],
                      map_theme['variables'][MapThemeVariable.TEXT_WRAP_NAMES_LENGTH.value],
                      config[MapConfigKeys.MAP_OUTER_AREA.value],
                      map_theme['variables'][MapThemeVariable.TEXT_BB_EXPAND_PERCENT.value],
                      map_theme['variables'][MapThemeVariable.MARKER_BB_EXPAND_PERCENT.value])
    plotter.init(
        map_theme['variables'][MapThemeVariable.LAND_COLOR.value], bg_gdf)
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.AREAS_PLOTTING.value
        }
    plotter.areas(areas_gdf)
    del areas_gdf

    plotter.area_boundary(config[MapConfigKeys.MAP_AREA_BOUNDARY.value],
                          color="black")
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.WAYS_PLOTTING.value
        }
    plotter.ways(ways_gdf)
    del ways_gdf
    # must be before nodes
    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.GPXS_PLOTTING.value
        }
    plotter.gpxs(gpxs_gdf)
    plotter.clip()
    del gpxs_gdf

    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.STATUS.value: ProcessingStatus.NODES_PLOTTING.value
        }

    plotter.nodes(nodes_gdf)
    del nodes_gdf

    folder = Utils.ensure_dir_exists(OUTPUT_PDF_FOLDER)

    pdf_name = f'{folder}map_{task_id}.pdf'

    with lock:
        shared_dict[task_id] = {
            **shared_dict[task_id],
            SharedDictKeys.FILES.value: [*shared_dict[task_id][SharedDictKeys.FILES.value], pdf_name],
            SharedDictKeys.STATUS.value:  ProcessingStatus.FILE_SAVING.value
        }
    plotter.generate_pdf(pdf_name)
