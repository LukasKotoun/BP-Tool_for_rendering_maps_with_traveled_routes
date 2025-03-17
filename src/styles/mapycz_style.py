from common.custom_types import ElementStyles, FeatureStyles
from common.map_enums import Style, TextPositions, MinPlot, MarkerPosition, MarkersCodes, LineCupStyles, MapThemeVariable, BaseConfigKeys
from config import font_awesome_prop, material_design_prop, BASE_OSM_CONFIG
from modules.utils import Utils
"""Edge linestyle is suported only dashed or not dashed (without concrete specification) on not solid lines.
Ploting is turned off by setting color to None with few exceptions.
    Text or marker turn off by setting marker/textcolor to 'None', marker edge or text edge by setting edge to 'None'.
    If want to turn off only marker but text draw like annotation set marker to "None".
"""

# ------------styles--------------

# (filer for split from areas, filter for ploting)
AREAS_OVER_WAYS_FILTER = ([{'highway': ['pedestrian', 'footway']}, {'amenity': ['parking', 'motorcycle_parking']}],
                          [{'highway': ['pedestrian', 'footway'], 'area': 'yes'},
                           {'highway': ['pedestrian', 'footway'],
                               'place': ['square']},
                           {'amenity': ['parking', 'motorcycle_parking']}])

DEFAULT_FONTS = ['Arial Unicode MS', 'DejaVu Sans']

WATER_COLOR_ZOOM_8_10 = "#9fc4e2"
WATER_COLOR_ZOOM_1_7 = "#9abfdc"


UNPAVED_WAY_COLOR = '#9a9173'
NORMAL_WAY_COLOR = '#FFFFFF'
NORMAL_WAY_EDGE_COLOR = '#b5aa91'

GREEN_AREA_COLOR_ZOOM_8_10 = '#d4ebb9'
GREEN_AREA_COLOR_ZOOM_1_7 = '#cfe5b3'
INDUSTRIAL_AREA_COLOR_ZOOM_8_10 = '#e6e2da'
INDUSTRIAL_AREA_COLOR_ZOOM_7 = '#dcdad4'
INDUSTRIAL_AREA_COLOR_ZOOM_5_6 = '#d6d4ce'
RESIDENTAL_AREA_COLOR_ZOOM_8_10 = '#f0e7d5'
RESIDENTAL_AREA_COLOR_ZOOM_7 = '#e8dbbd'
RESIDENTAL_AREA_COLOR_ZOOM_1_6 = '#e2d5b7'

CITY_POINT_COLOR = '#e4d6b7'
CITY_POINT_EDGE_COLOR = '#b5ab8c'

TEXT_EXPAND_PERCENT = 5
MARKER_EXPAND_PERCENT = 5

WATER_COLOR = {"1-7": WATER_COLOR_ZOOM_1_7, "8-10": WATER_COLOR_ZOOM_8_10}


LAND_COLOR = '#f1f0e5'

RESERVATION_EDGE_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier(
    {"10-10": 40, "9-9": 2, '8-8': 2, "7-7": 2, "6-5": 1.5,
     "4-3": 1.2, "2-1": 1.4
     }, Style.WIDTH.value)


DASHED_LAND_WAYS_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier(
    {"10-10": 7, '9-9': 1.1, '8-8': 1.5, "7-4": 2, "3-1": 1.5},
    Style.WIDTH.value)

SMALL_NONDASHED_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier(
    {"10-10": 12, "9-8": 1.1, "7-4": 1.5, "3-1": 1.4},
    Style.WIDTH.value)

SPECIAL_WAYS_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier({
    "10-9": 19, "8-8": 1.4, "7-4": 2, "3-1": 1.5},
    Style.WIDTH.value)

# -------------------gpx-------------------

GPXS_STYLES_SCALE = []
gpxs_styles_default: ElementStyles = [
    ([], {
        Style.COLOR.value: 'Red', Style.WIDTH.value: 1.3,
        Style.ALPHA.value: 0.7, Style.ZINDEX.value: 0, Style.EDGE_ALPHA.value: 0.7,
        Style.EDGE_COLOR.value: None, Style.EDGE_WIDTH_RATIO.value: 0.15,
        Style.EDGE_LINESTYLE.value: "-", Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value,
        Style.LINESTYLE.value: "-", Style.LINE_CAPSTYLE.value: LineCupStyles.ROUND.value,

        Style.START_MARKER_WIDTH.value: 6, Style.START_MARKER_EDGE_RATIO.value: 0.1,
        Style.START_MARKER_COLOR.value: "#18ac0d", Style.START_MARKER_EDGE_COLOR.value: "#FFFFFF", Style.START_MARKER_ALPHA.value: 1.0,

        Style.FINISH_MARKER_WIDTH.value: 6, Style.FINISH_MARKER_EDGE_RATIO.value: 0.1,
        Style.FINISH_MARKER_COLOR.value: "#000000", Style.FINISH_MARKER_EDGE_COLOR.value: "#FFFFFF", Style.FINISH_MARKER_ALPHA.value: 1.0,
        
        Style.GPX_ABOVE_TEXT.value: False, Style.MARKER_LAYER_POSITION.value: MarkerPosition.UNDER_TEXT_OVERLAP.value
    })
]

GPXS_STYLES: ElementStyles = [
    # *folders_styles,  # folder must be first - folder have only some byt file name have all - file name will have only some
    # *root_files_styles,
    *gpxs_styles_default,
]


# -------------------nodes-------------------
# zorder: castle: 28, towers: 29 peaks: 30, place names 40-50,

NODES_STYLES_SCALE = []
place_styles: ElementStyles = [
    ({'place': 'city', 'capital': 'yes'}, {Style.ZINDEX.value: 51},
     {"4-6": {Style.TEXT_FONT_SIZE.value: 16, Style.TEXT_WEIGHT.value: 'bold'},
      "1-3": {Style.TEXT_FONT_SIZE.value: 13, Style.TEXT_WEIGHT.value: 'bold'},
      "1-2": {Style.WIDTH.value: 5}
      }),

    ([{'place': 'city'}, {'place': 'town', 'capital': 'yes'}], {
        Style.ZINDEX.value: 50,
    },
        {
        "4-10": {Style.TEXT_FONT_SIZE.value: 15},
        "1-3": {Style.TEXT_FONT_SIZE.value: 12},
        "2-7": {Style.TEXT_WEIGHT.value: 'bold'},
        "1-2": {Style.MARKER.value: MarkersCodes.MPL_CIRCLE_MARKER.value, Style.COLOR.value: CITY_POINT_COLOR,
                Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT1.value,
                Style.EDGE_WIDTH_RATIO.value: 0.15, Style.WIDTH.value: 4, Style.EDGE_COLOR.value: CITY_POINT_EDGE_COLOR}
    }),

    ({'place': 'town'}, {
        Style.ZINDEX.value: 49
    },
        {
        "7-10": {Style.TEXT_FONT_SIZE.value: 13},
        "5-6": {Style.TEXT_FONT_SIZE.value: 11.5},
        "4": {Style.TEXT_FONT_SIZE.value: 10},
        "3": {Style.TEXT_FONT_SIZE.value: 9},
        "4-7": {Style.TEXT_WEIGHT.value: 'bold'},
        "1-2": {Style.TEXT_FONT_SIZE.value: 8, Style.MARKER.value: MarkersCodes.MPL_CIRCLE_MARKER.value, Style.COLOR.value: CITY_POINT_COLOR,
                Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT1.value,
                Style.EDGE_WIDTH_RATIO.value: 0.15, Style.WIDTH.value: 3.3, Style.EDGE_COLOR.value: CITY_POINT_EDGE_COLOR}
    }),
    ({'place': 'village'}, {
        Style.ZINDEX.value: 48
    },
        {
        "6-10": {Style.TEXT_FONT_SIZE.value: 10},
        "4-5": {Style.TEXT_FONT_SIZE.value: 8},
        "1-3": {Style.TEXT_FONT_SIZE.value: 7},
        "1-2": {Style.MARKER.value: MarkersCodes.MPL_CIRCLE_MARKER.value, Style.COLOR.value: CITY_POINT_COLOR,
                Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT1.value,
                Style.EDGE_WIDTH_RATIO.value: 0.15, Style.WIDTH.value: 2.8, Style.EDGE_COLOR.value: CITY_POINT_EDGE_COLOR}
    }),

    ({'place': 'suburb'}, {
        Style.ZINDEX.value: 47
    },
        {
        "1-7": {Style.TEXT_COLOR.value: '#454444'},
        "6-10": {Style.TEXT_FONT_SIZE.value: 8},
        "1-5": {Style.TEXT_FONT_SIZE.value: 7},
    }),

    ({'place': 'neighbourhood'}, {
        Style.ZINDEX.value: 46, Style.TEXT_COLOR.value: '#616060', Style.TEXT_FONT_SIZE.value: 6
    }),

    ({'place': 'locality'}, {
        Style.ZINDEX.value: 24, Style.TEXT_COLOR.value: '#616060', Style.TEXT_FONT_SIZE.value: 5
    }),
]


# text color or MARKER color turn of by string "None" instead of None
natural_styles_nodes: ElementStyles = [
    ({'natural': 'peak'}, {
        Style.ZINDEX.value: 30, Style.MIN_PLOT_REQ.value: MinPlot.MARKER_TEXT2.value,
        # marker
        Style.MARKER.value: MarkersCodes.MPL_TRIANGLE.value, Style.MARKER_HORIZONTAL_ALIGN.value: "center",
        Style.TEXT_FONTFAMILY.value: ['Georgia', *DEFAULT_FONTS],
        Style.COLOR.value: "#443833", Style.EDGE_COLOR.value: "None", Style.WIDTH.value: 3,
        # text
        Style.TEXT_WEIGHT.value: 'heavy', Style.TEXT_STYLE.value: 'italic', Style.TEXT_FONT_SIZE.value: 6,
        Style.TEXT_COLOR.value: "#443833", Style.TEXT_OUTLINE_COLOR.value: '#FFFFFF',
        Style.TEXT1_POSITIONS.value: [TextPositions.TOP.value], Style.TEXT2_POSITIONS.value: [TextPositions.BOTTOM.value],
        Style.TEXT_OUTLINE_WIDTH_RATIO.value: 0.3, Style.TEXT_WRAP_LEN.value: 20
    })
]

icons_above_styles_nodes: ElementStyles = [
    ({'man_made': 'tower', 'tower:type': ['observation', 'watchtower']}, {
        Style.MIN_PLOT_REQ.value: MinPlot.MARKER.value, Style.ZINDEX.value: 20,
        # marker
        Style.MARKER.value: MarkersCodes.FA_TOWER_OBSERVATION.value, Style.MARKER_FONT_PROPERTIES.value: font_awesome_prop,
        Style.COLOR.value: "#99441e", Style.EDGE_COLOR.value: "#FFFFFF", Style.WIDTH.value: 7,
        Style.EDGE_WIDTH_RATIO.value: 0.15,
        # text
        Style.TEXT_COLOR.value: "#8c7359", Style.TEXT_OUTLINE_COLOR.value: '#FFFFFF', Style.TEXT_FONT_SIZE.value: 5,
        Style.TEXT1_POSITIONS.value: [TextPositions.BOTTOM.value], Style.TEXT_OUTLINE_WIDTH_RATIO.value: 0.2,
        Style.TEXT_WRAP_LEN.value: 20
    }, {
        "6-10": {Style.MARKER_LAYER_POSITION.value: MarkerPosition.ABOVE_NORMAL.value},
        "1-5": {Style.MARKER_LAYER_POSITION.value: MarkerPosition.UNDER_TEXT_OVERLAP.value}
    }),

    ({'historic': ['castle']}, {
        Style.MIN_PLOT_REQ.value: MinPlot.MARKER.value, Style.ZINDEX.value: 19,
        # marker
        Style.MARKER.value: MarkersCodes.MU_CASTLE.value, Style.MARKER_FONT_PROPERTIES.value: material_design_prop,
        Style.COLOR.value: "#846252", Style.EDGE_COLOR.value: "#FFFFFF", Style.WIDTH.value: 7,
        Style.EDGE_WIDTH_RATIO.value: 0.15,
        # text
        Style.TEXT_FONT_SIZE.value: 5,
        Style.TEXT_COLOR.value: "#8c7359", Style.TEXT_OUTLINE_COLOR.value: '#FFFFFF',
        Style.TEXT1_POSITIONS.value: [TextPositions.BOTTOM.value], Style.TEXT_OUTLINE_WIDTH_RATIO.value: 0.2,
        Style.TEXT_WRAP_LEN.value: 20
    }, {
        "6-10": {Style.MARKER_LAYER_POSITION.value: MarkerPosition.NORMAL.value},
        "1-5": {Style.MARKER_LAYER_POSITION.value: MarkerPosition.UNDER_TEXT_OVERLAP.value}
    })
]

nodes_styles_default: ElementStyles = [
    ({'natural': ''}, {
    }),

    ({'place': ''}, {
        Style.TEXT_OUTLINE_WIDTH_RATIO.value: 0.2, Style.MIN_PLOT_REQ.value: MinPlot.TEXT1.value,
        Style.TEXT_COLOR.value: "#000000", Style.TEXT_OUTLINE_COLOR.value: '#FFFFFF',
        Style.TEXT1_POSITIONS.value: [
            TextPositions.TOP.value, TextPositions.BOTTOM.value, TextPositions.RIGHT.value]
    }),
    ([], {
        Style.ALPHA.value: 1, Style.EDGE_ALPHA.value: 1,
        Style.TEXT_FONTFAMILY.value: [*DEFAULT_FONTS],
        Style.TEXT_STYLE.value: 'normal',
        Style.TEXT_WEIGHT.value: 'normal', Style.TEXT_WRAP_LEN.value: 15
    })
]

NODES_STYLES: ElementStyles = [
    *icons_above_styles_nodes,
    *natural_styles_nodes,
    *place_styles,
    *nodes_styles_default,
]
# -------------------ways------------------
# scaled styles - relative to polygon (not paper)
WAYS_STYLES_SCALE = [Style.WIDTH.value]
# dashed highways z index 0-waterways, 1-14 - dashedways, 15-20 - barrier, 21-50 normal ways or areas as ways, 60-70 aeroway, 70-80 - aerialway, 90 - 100 (subway - 20) - railways

highway_styles_bridges_overwrite: ElementStyles = [
    ({'highway': '', 'bridge': ''}, {Style.EDGE_COLOR.value: None,
                                     })]

highway_styles_tunnels: ElementStyles = [
    ([{'highway': ['motorway', 'motorway_link'],
     'tunnel': ''},
      {'highway': ['motorway', 'motorway_link'],
      'covered': ''}
      ],
     {Style.COLOR.value: "#a9de86", Style.EDGE_COLOR.value: "#629157"}),

    ([{'highway': ['trunk', 'trunk_link'], 'tunnel': ''},
      {'highway': ['trunk', 'trunk_link'], 'covered': ''}],
     {Style.COLOR.value: "#a9de86", Style.EDGE_COLOR.value: "#629157"}),

    ([{'highway': ['primary', 'primary_link'], 'tunnel': ''},
      {'highway': ['primary', 'primary_link'], 'covered': ''}],
     {Style.COLOR.value: "#ffe6bd", Style.EDGE_COLOR.value: "#e8a542"}),

    ([{'highway': ['secondary', 'secondary_link'],
     'tunnel': ''},
      {'highway': ['secondary', 'secondary_link'],
       'covered': ''}
      ], {Style.COLOR.value: "#fbf8b0", Style.EDGE_COLOR.value: "#cdc139"}),

    # default color and all edge styles
    ([{'highway': '', 'tunnel': '', 'bridge': '~'}, {'highway': '', 'covered': '', 'bridge': '~'}],
     {Style.EDGE_LINESTYLE.value: (2, (3, 1)),
      Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value,
      Style.COLOR.value: "#FFFFFF", Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR, Style.LINESTYLE.value: "-"})]

highway_styles_main: ElementStyles = [
    ({'highway': 'motorway'}, {Style.COLOR.value: '#9bd772', Style.ZINDEX.value: 50,
                               Style.EDGE_COLOR.value: "#629157"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 42, "9": 1.3, "8": 1.5, "7": 1.8, "6": 1.9, "5": 0.8,
            "4": 1.6, "3": 1.6, "2": 1.6, "1-1": 1.4},
            Style.WIDTH.value),
        "6-8": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
        "4-5": {Style.EDGE_WIDTH_RATIO.value: 1 + 2,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 2,
                Style.PLOT_WITHOUT_CROSSING.value: True},
        "2-3": {Style.EDGE_WIDTH_RATIO.value: 1 + 2.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 2.5,
                Style.PLOT_WITHOUT_CROSSING.value: True},
        "1": {Style.EDGE_WIDTH_RATIO.value: 1 + 3,
              Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 3,
              Style.PLOT_WITHOUT_CROSSING.value: True}
    }),

    ({'highway': 'trunk'}, {Style.COLOR.value: '#9bd772', Style.ZINDEX.value: 49,
     Style.EDGE_COLOR.value: "#629157"},
     {
         **Utils.cumulative_zoom_size_multiplier({
             "10": 42, "9": 1.3, "8": 1.4, "7": 1.7, "6": 1.8, "5": 1.4,
             "4": 1.6, "3": 1.7, "2": 1.6, "1-1": 1.4},
             Style.WIDTH.value),
         "6-7": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.6,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.6},
         "3-5": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.8,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.8},
        "1-2": {Style.EDGE_WIDTH_RATIO.value: 1 + 1.3,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 1.3}
    }),

    ({'highway': 'primary'}, {Style.COLOR.value: '#ffcc78', Style.ZINDEX.value: 48,
     Style.EDGE_COLOR.value: "#e8a542"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 42, "9": 1.3, "8": 1.4, "7": 1.7, "6": 1.8, "5": 1.3,
            "4": 1.6, "3": 1.7, "2": 1.6, "1-1": 1.4},
            Style.WIDTH.value),
         "6-8": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.6,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.6},
         "2-5": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.8,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.8},
        "1": {Style.EDGE_WIDTH_RATIO.value: 1 + 1.3,
              Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 1.3},
    }),

    ({'highway': 'secondary'}, {Style.COLOR.value: '#faef75', Style.ZINDEX.value: 47,
                                Style.WIDTH.value: 20, Style.EDGE_COLOR.value: "#cdc139"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 40, "9": 1.2, "8": 1.4, "7": 1.8, "6": 1.5,
            "5": 1.5, "4": 1.6, "1-3": 1.6},
            Style.WIDTH.value),
        "7-9": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
        "1-6": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.7},
    }),

    ({'highway': 'tertiary'}, {Style.ZINDEX.value: 46, Style.COLOR.value: NORMAL_WAY_COLOR,
                               Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 40, "9": 1.2, "8": 1.4, "7": 1.8, "6": 1.5,
            "5": 1.5, "1-4": 1.2},
            Style.WIDTH.value),
        "7-9": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
        "1-6": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.7},
    }),

    ({'highway': 'motorway_link'}, {Style.COLOR.value: '#9bd772', Style.ZINDEX.value: 45,
     Style.EDGE_COLOR.value: "#629157"}),

    ({'highway': 'trunk_link'}, {Style.COLOR.value: '#9bd772', Style.ZINDEX.value: 44,
                                 Style.EDGE_COLOR.value: "#629157"}),

    ({'highway': 'primary_link'}, {Style.COLOR.value: '#ffcc78', Style.ZINDEX.value: 43,
                                   Style.EDGE_COLOR.value: "#e8a542"}),

    ({'highway': ['motorway_link', 'trunk_link', 'primary_link']}, {}, {
        **Utils.cumulative_zoom_size_multiplier({
            "9-10": 32, "8": 1.3, "7": 1.8, "6": 1.8, "5": 1.3,
            "4": 1.7, "3": 1.6, "2": 1.4, "1": 1.4},
            Style.WIDTH.value),
        "9": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
              Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
        "1-8": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.8,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.8}
    }),

    ({'highway': 'secondary_link'}, {Style.COLOR.value: '#faef75', Style.ZINDEX.value: 42,
     Style.EDGE_COLOR.value: "#cdc139"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "9-10": 30, "8": 1.3, "7": 1.7, "6": 1.6, "5": 1.3,
            "1-4": 1.6},
            Style.WIDTH.value),
        "9": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
              Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
        "1-8": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.8,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.8}
    }),

    ({'highway': 'tertiary_link'}, {Style.ZINDEX.value: 41}),

    ({'highway': ['residential', 'unclassified', 'pedestrian', 'tertiary_link']},
     {Style.ZINDEX.value: 40, Style.COLOR.value: NORMAL_WAY_COLOR,
      Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR},
     {
        **Utils.cumulative_zoom_size_multiplier(
            {"9-10": 27, "8": 1.3, "7": 1.8, "6-3": 1.8, "2-1": 1.5}, Style.WIDTH.value),
        "7-8": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
        "1-6": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.8,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.8},
    }),
]

highway_styles_surface_special_and_paths: ElementStyles = [

    # to non dashed
    ({'highway': ['track', 'cycleway'],
      'surface': ['asphalt'],
      'tracktype': ('~grade3', '~grade4', '~grade5'),
      },
     {Style.ZINDEX.value: 35, Style.COLOR.value: "#d4d2cf", Style.EDGE_COLOR.value: "#a49d84",
      Style.LINESTYLE.value: "-", Style.EDGE_LINESTYLE.value: "-"},
     {
        **SPECIAL_WAYS_CUMULATIVE_SIZE,
        "1-8": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.7},

        "8-10": {Style.COLOR.value: "#ebe8e4", Style.EDGE_COLOR.value: "#9a9275"},
        "7": {Style.COLOR.value: "#e1dedb", Style.EDGE_COLOR.value: "#a2967c"}}),

    ([{'highway': ['path', 'track'],
      'surface': ['asphalt', 'concrete', 'paving_stones', 'sett', 'cobblestone',
                  'compacted', 'fine_gravel'],
       'tracktype': ('~grade3', '~grade4', '~grade5')},
      {'highway': ['path', 'track'],
        'tracktype': ['grade1', 'grade2']}],
     {Style.ZINDEX.value: 33, Style.COLOR.value: NORMAL_WAY_COLOR, Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR,
      Style.LINESTYLE.value: "-", Style.EDGE_LINESTYLE.value: "-"},
     {
        **SMALL_NONDASHED_CUMULATIVE_SIZE,
        "9": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
              Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
        # on smaller zoom, change to line without edge
        "1-8": {Style.COLOR.value: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.value: None,
                Style.PLOT_ON_BRIDGE.value: True}
    }),

    ({'highway': ['footway'],
      'surface': ['unpaved', 'gravel', 'pebblestone', 'rock', 'dirt',
                  'ground', 'grass', 'sand', 'mud', 'woodchips']},
     {Style.COLOR.value: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.value: None,
      Style.LINESTYLE.value: (3, (5, 4)), Style.ZINDEX.value: 10,
      Style.PLOT_ON_BRIDGE.value: False},
     {**DASHED_LAND_WAYS_CUMULATIVE_SIZE,
      "1-6": {Style.PLOT_ON_BRIDGE.value: True}}
     ),
]

highway_styles_special_and_paths: ElementStyles = [

    ({'highway': 'service'}, {Style.ZINDEX.value: 37, Style.COLOR.value: NORMAL_WAY_COLOR,
                              Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR}),

    ({'highway': 'raceway'}, {Style.COLOR.value: NORMAL_WAY_COLOR, Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR,
                              Style.ZINDEX.value: 35},
     {"7-10": {Style.COLOR.value: '#e1dedb',
               Style.EDGE_COLOR.value: "#a8a483"}
      }),

    ({'highway': ['raceway', 'service']}, {},
     {
        **SPECIAL_WAYS_CUMULATIVE_SIZE,
        "1-9": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.7},
    }),


    ({'highway': 'cycleway'}, {Style.ZINDEX.value: 36, Style.COLOR.value: NORMAL_WAY_COLOR,
                               Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR}, {
        "1-8": {Style.COLOR.value: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.value: None, Style.LINESTYLE.value: "-",
                Style.LINE_CAPSTYLE.value: LineCupStyles.ROUND.value, Style.PLOT_ON_BRIDGE.value: True}
    }),

    ({'highway': 'steps'}, {Style.COLOR.value: NORMAL_WAY_COLOR, Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR,
                            Style.LINESTYLE.value: (2, (3, 0.2)),
                            Style.LINE_CAPSTYLE.value: LineCupStyles.BUTT.value,
                            Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value,
                            Style.PLOT_ON_BRIDGE.value: False, Style.ZINDEX.value: 31},
     {"1-8": {Style.COLOR.value: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.value: None, Style.LINESTYLE.value: "-",
              Style.LINE_CAPSTYLE.value: LineCupStyles.ROUND.value, Style.PLOT_ON_BRIDGE.value: True}}),

    ({'highway': 'footway'}, {Style.ZINDEX.value: 30, Style.COLOR.value: NORMAL_WAY_COLOR,
                              Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR},
     {"1-8": {Style.COLOR.value: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.value: None, Style.LINESTYLE.value: "-",
              Style.LINE_CAPSTYLE.value: LineCupStyles.ROUND.value}
      }),

    ({'highway': ['footway', 'steps', 'cycleway']}, {},
     {**SMALL_NONDASHED_CUMULATIVE_SIZE,
      "9": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
            Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.5},
      }),


    ({'highway': 'track'}, {Style.ZINDEX.value: 14, Style.COLOR.value: UNPAVED_WAY_COLOR, Style.LINESTYLE.value: (7, (10, 4)),
     Style.EDGE_COLOR.value: None, Style.PLOT_ON_BRIDGE.value: False},
     {"1-7": {Style.PLOT_ON_BRIDGE.value: True}}),
    ({'highway': 'path'}, {Style.ZINDEX.value: 13, Style.COLOR.value: UNPAVED_WAY_COLOR, Style.LINESTYLE.value: (3, (5, 4)),
     Style.EDGE_COLOR.value: None, Style.PLOT_ON_BRIDGE.value: False},
     {"1-7": {Style.PLOT_ON_BRIDGE.value: True}}),
    ({'highway': ['path', 'track']}, {}, {
        **DASHED_LAND_WAYS_CUMULATIVE_SIZE
    }
    ),
]


railway_remove_on_zoom: ElementStyles = [
    ({'railway': ['rail', 'disused', 'light_rail', "monorail", "subway"],
      'service': ['crossover', 'siding', 'spur', 'yard']}, {
    }, {}, {
        "1-6": {Style.COLOR.value: None, Style.EDGE_COLOR.value: None}})
]

railway_styles_bridges_overwrite: ElementStyles = [
    ({'railway': ['funicular', 'subway'], 'bridge': ''}, {
        Style.BRIDGE_EDGE_COLOR.value: None, Style.BRIDGE_COLOR.value: None
    }),
    ({'railway': ['subway'], 'bridge': ''}, {
        Style.COLOR.value: '#FFFFFF',
        Style.EDGE_COLOR.value: '#939393',
        Style.LINESTYLE.value: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
        Style.LINE_CAPSTYLE.value: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value,
    })
]

railway_styles_tunnels: ElementStyles = [
    ([{'railway': ['rail', 'light_rail', "monorail", 'miniature'], 'tunnel': ''},
     {'railway': ['rail', 'light_rail', "monorail", 'miniature'], 'covered': ''}], {
        Style.COLOR.value: None, Style.EDGE_LINESTYLE.value: (3, (7, 4)),
        Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value
    }),

    ([{'railway': 'tram', 'tunnel': ''},
     {'railway': 'tram', 'covered': ''}], {
        Style.LINESTYLE.value: (3, (7, 4)),
        Style.LINE_CAPSTYLE.value: LineCupStyles.BUTT.value
    }),

    ([{'railway': 'funicular', 'tunnel': ''},
     {'railway': 'funicular', 'covered': ''}], {
        Style.COLOR.value: None,
        Style.EDGE_WIDTH_RATIO.value: 0.4,
        Style.EDGE_LINESTYLE.value: (2, (3, 2)),
        Style.LINE_CAPSTYLE.value: LineCupStyles.BUTT.value,
    })
]

railway_styles_service: ElementStyles = [
    ({'railway': ['rail', 'disused', 'light_rail', "monorail", "subway"],
      'service': ['crossover', 'siding', 'spur', 'yard']}, {
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 8, "9": 1.2, "8": 1.8, "4-7": 1.7, "1-3": 1.5}, Style.WIDTH.value)
    })]

railway_styles: ElementStyles = [
    # for osm light_rail, monorail is just line, subway is line but with different color

    ({'railway': ['rail', 'disused', 'light_rail', "monorail", 'miniature']}, {
        Style.COLOR.value: '#FFFFFF', Style.EDGE_COLOR.value: '#707070',
        Style.LINESTYLE.value: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.value: 1 + 0.5,
        Style.LINE_CAPSTYLE.value: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value,
        Style.ZINDEX.value: 100
    }),
    # 3
    ({'railway': 'subway'}, {
        Style.COLOR.value: '#939392', Style.LINESTYLE.value: (3, (7, 4)),
        Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value,
        Style.EDGE_COLOR.value: None,
        Style.ZINDEX.value: 20
    }),

    ({'railway': ['rail', 'disused', 'light_rail', "monorail", 'miniature', "subway"]}, {},
     {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 11, "9": 1.2, "8": 1.6, "7": 2.1,
                "6": 2.3, "5": 2, "2-4": 1.3, "1": 1.3},
            Style.WIDTH.value)
    }),

    ({'railway': 'funicular'}, {
        Style.ZINDEX.value: 99,
        Style.COLOR.value: '#FFFFFF',
        Style.EDGE_COLOR.value: '#474747',
        Style.LINESTYLE.value: (0, (5, 5)), Style.EDGE_LINESTYLE.value: (0, (5, 5)),
        Style.EDGE_WIDTH_RATIO.value: 1 + 0.8, Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.value: 0.4,
        Style.LINE_CAPSTYLE.value: LineCupStyles.ROUND.value, Style.EDGE_CAPSTYLE.value: LineCupStyles.ROUND.value
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "8-9": 2, "7": 2,
                "1-6": (1.8, {Style.LINESTYLE.value: (0, (4, 8))})},
            Style.WIDTH.value),
    }),

    ({'railway': 'tram'}, {
        Style.COLOR.value: '#404040'
    },
        {**Utils.cumulative_zoom_size_multiplier(
         {"10": 4, "9": 1.5, "6-8": 1.2, "1-5": 1.3},
         Style.WIDTH.value)}
    ),

]


aerialway_styles: ElementStyles = [
    ({'aerialway': ['cable_car', 'gondola', 'mixed_lift']}, {
        Style.COLOR.value: '#FFFFFF',
        Style.EDGE_LINESTYLE.value: "--",
        Style.LINESTYLE.value: (0, (4, 5)), Style.EDGE_WIDTH_RATIO.value: 1 + 0.6,
        Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.value: 0.3, Style.ZINDEX.value: 80
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "8-9": 2, "7": 2,
                "3-6": 1.8, "1-2": 1.5},
            Style.WIDTH.value),
        "1-6": {Style.LINESTYLE.value: (0, (4, 8))}
    }),

    ({'aerialway': ['chair_lift']}, {
        Style.LINESTYLE.value: (0, (3, 5)),
        Style.EDGE_LINESTYLE.value: '-', Style.EDGE_WIDTH_RATIO.value: 0.3,
        Style.ZINDEX.value: 79
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "9": 1.5, "8": 1.3, "7": 1.6,
                "3-6": 2.4, "1-2": 1.5},
            Style.WIDTH.value),
        "1-6": {Style.LINESTYLE.value: (0, (3, 8))}
    }),
]

aeroway_styles: ElementStyles = [
    ({'aeroway': 'runway'}, {
        Style.ZINDEX.value: 70,
        Style.LINE_CAPSTYLE.value: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.value: LineCupStyles.BUTT.value,
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 60, "9": 2, "8": 1.3, "5-7": 1.7, "1-4": 1.5},
            Style.WIDTH.value),
        "6": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.3},
        "1-5": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.6},
    }),
    ({'aeroway': 'taxiway'}, {
        Style.WIDTH.value: 30,
        Style.ZINDEX.value: 69,
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 30, "8-9": 1.5, "7": 1.3, "5-6": 1.6, "1-4": 2},
            Style.WIDTH.value),
        "1-6": {Style.EDGE_WIDTH_RATIO.value: 1 + 0.5},
    }),
]

waterway_styles_tunnels: ElementStyles = [
    ([{'waterway': '', 'tunnel': '', 'intermittent': "yes"},
     {'waterway': '', 'covered': '', 'intermittent': "yes"}], {
     Style.LINESTYLE.value: (0, (1, 1)), Style.EDGE_COLOR.value: None}),
    ([{'waterway': '', 'tunnel': ''},
      {'waterway': '', 'covered': ''}], {Style.LINESTYLE.value: "--", Style.EDGE_COLOR.value: None})]

waterway_styles: ElementStyles = [
    ({'waterway': '', 'intermittent': "yes"}, {Style.LINESTYLE.value: (0, (1, 1)),
                                               Style.EDGE_COLOR: None}),
    ({'waterway': ['river']}, {}, {
        **Utils.cumulative_zoom_size_multiplier(
            {"8-10": 65, "7": 2, "6": 2, "5": 1.8,
                "4": 1.1, "3": 1.2, "2": 1.7, "1": 1.8},
            Style.WIDTH.value)
    }),

    ({'waterway': ['canal']}, {}, {
        **Utils.cumulative_zoom_size_multiplier(
            {"8-10": 30, "7": 1.8, "6": 1.7, "3-5": 1.7, "1-2": 1.4},
            Style.WIDTH.value)
    }),
]


ways_styles_default: ElementStyles = [
    ({'highway': ''}, {
        Style.EDGE_WIDTH_RATIO.value: 1 + 0.3,
        Style.COLOR.value: NORMAL_WAY_COLOR,
        Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR
    }),
    ({'highway': '', 'bridge': ''}, {
        Style.BRIDGE_EDGE_LINESTYLE.value: '-', Style.BRIDGE_LINESTYLE.value: '-',
        Style.BRIDGE_WIDTH_RATIO.value: 1, Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.3,
        Style.BRIDGE_EDGE_COLOR.value: "#83877e", Style.BRIDGE_COLOR.value: "#FFFFFF",
        Style.PLOT_ON_BRIDGE.value: True
    }),

    ({'railway': ''}, {
        Style.ZINDEX.value: 90
    }),

    ({'railway': '', 'bridge': ''}, {
        Style.BRIDGE_EDGE_LINESTYLE.value: '-', Style.BRIDGE_LINESTYLE.value: '-',
        Style.BRIDGE_EDGE_COLOR.value: '#707070', Style.BRIDGE_COLOR.value: "#FFFFFF",
        Style.BRIDGE_WIDTH_RATIO.value: 1 + 1.6, Style.BRIDGE_EDGE_WIDTH_RATIO.value: 1 + 0.3,
        Style.PLOT_ON_BRIDGE.value: True,
    }),

    ({'aeroway': ''}, {
        Style.COLOR.value: NORMAL_WAY_COLOR, Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR,
        Style.EDGE_WIDTH_RATIO.value: 1 + 0.2,
    }),

    ({'aerialway': ''}, {
        Style.COLOR.value: '#606060',
        Style.EDGE_COLOR.value: '#606060', Style.EDGE_LINESTYLE.value: '-',
        Style.LINESTYLE.value: (0, (0.1, 3)), Style.EDGE_WIDTH_RATIO.value: 0.3,
        Style.ZINDEX.value: 70
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "9": 1.5, "8": 1.2, "7": 1.5,
                "1-6": (2.2, {Style.LINESTYLE.value: (0, (0.1, 8))})},
            Style.WIDTH.value)
    }),

    ({'barrier': ''}, {
        Style.ZINDEX.value: 15,
        Style.COLOR.value: "#909090"
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"9-10": 8, "5-8": 1.5, "1-4": 1.4},
            Style.WIDTH.value),
    }),

    ({'route': 'ferry'}, {
        Style.COLOR.value: '#7394b4', Style.LINESTYLE.value: (0, (5, 4)),
        Style.ZINDEX.value: 1, Style.EDGE_COLOR.value: None
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 8, "9": 1.5, "8": 1.8, "7": 1.7, "6": 2, "5": 2,
             "4": 2.1, "3": 2, '2': 2, '1': 1.3},
            Style.WIDTH.value),
    }),

    ({'waterway': ''}, {
        Style.COLOR.value: WATER_COLOR_ZOOM_1_7,
        Style.ZINDEX.value: 0, Style.EDGE_COLOR.value: None
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"9-10": 10, "8": 1.7, "7": 1.8, "6": 2, "3-5": 2, "1-2": 1.4},
            Style.WIDTH.value),
        "8-10": {Style.COLOR.value: WATER_COLOR_ZOOM_8_10}}),


    ([], {
        Style.ALPHA.value: 1.0, Style.EDGE_ALPHA.value: 1.0,
        Style.LINESTYLE.value: '-', Style.EDGE_LINESTYLE.value: '-',
        Style.LINE_CAPSTYLE.value: LineCupStyles.ROUND.value, Style.EDGE_CAPSTYLE.value: LineCupStyles.ROUND.value,
    }),
]


WAYS_STYLES: ElementStyles = [
    *railway_remove_on_zoom,
    *railway_styles_bridges_overwrite,
    *railway_styles_tunnels,
    *railway_styles_service,
    *railway_styles,

    *aerialway_styles,

    *aeroway_styles,

    *highway_styles_bridges_overwrite,
    *highway_styles_tunnels,

    *highway_styles_main,

    *highway_styles_surface_special_and_paths,
    *highway_styles_special_and_paths,

    *waterway_styles_tunnels,
    *waterway_styles,

    *ways_styles_default,
]


# -------------------areas-------------------
AREAS_STYLES_SCALE = [Style.WIDTH.value]


landuse_styles_area: ElementStyles = [

    ({'landuse': ['vineyard', 'orchard']}, {Style.COLOR.value: '#e1ebbe'}),

    ({'landuse': ['basin', 'salt_pond']}, {Style.COLOR.value: WATER_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.value: WATER_COLOR_ZOOM_8_10}}),
    ({'landuse': ['forest', 'recreation_ground', 'meadow', 'grass', 'cemetery']},
     {Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_1_7}, {
        "8-10": {Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_8_10}}),

    ({'landuse': 'cemetery'}, {}, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 5, "9": 1.6}, Style.WIDTH.value),
        "9-10": {Style.EDGE_COLOR.value: '#ada994',
                 Style.EDGE_ALPHA.value: 1, Style.EDGE_LINESTYLE.value: '-'}
    }),

    ({'landuse': ['allotments', 'retail', 'residential', 'garages', 'commercial']}, {},
     {"8-10": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_8_10},
      "7": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_7},
      "1-6": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),

    ({'landuse': ['industrial', 'farmyard', 'brownfield', 'landfill']},
     {},
     {"8-10": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_8_10},
      "7": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_7},
      "5-6": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_5_6},
      "1-4": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),

    ({'landuse': 'quarry'},
     {},
     {"8-10": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_8_10},
      "7": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_7},
      "1-6": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_5_6}}),
]

leisure_styles_area: ElementStyles = [
    ({'leisure': ['garden', 'park']}, {Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_8_10}}),
    ({'leisure': ['golf_course', 'playground', 'pitch']},
     {Style.COLOR.value: '#e3edc6',
      Style.EDGE_ALPHA.value: 1, Style.EDGE_LINESTYLE.value: '-',
      Style.EDGE_COLOR.value: '#b5c48b'}, {
          **Utils.cumulative_zoom_size_multiplier({
              "10": 4, "9": 1.4, "8": 1.4, "7": 1.4},
              Style.WIDTH.value)
    }),
    ({'leisure': ['sports_centre']},
     {Style.COLOR.value: '#def7d3', Style.EDGE_ALPHA.value: 1, Style.EDGE_LINESTYLE.value: '-',
      Style.EDGE_COLOR.value: '#b5c48b'}, {
          **Utils.cumulative_zoom_size_multiplier({
              "10": 4, "9": 1.4, "8": 1.4, "7": 1.4},
              Style.WIDTH.value)
    }),
    ({'leisure': 'swimming_pool'}, {Style.COLOR.value: WATER_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.value: WATER_COLOR_ZOOM_8_10}}),
]

# dynamic change color based on zoom level
building_styles_area: ElementStyles = [
    ({'building': ['church', 'synagogue', 'cathedral', 'temple', 'monastery']}, {}, {
        "8-10": {Style.COLOR.value: '#908b84'}}),

    ([{'building': ['university', 'hospital', 'public', 'clinic', 'supermarket']},
      {'building': '', 'historic': ''}], {}, {  # same as historic..
        "8-10": {Style.COLOR.value: '#bab09a'}}),

    ({'building': ['industrial', 'warehouse']}, {}, {
        "8-10": {Style.COLOR.value: '#d4d1cc'},
        "7": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_7},
        "5-6": {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_5_6}}),
]

natural_styles_area: ElementStyles = [

    ({'natural': ['heath', 'scrub', 'grassland', 'wood']}, {Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_1_7},
     {
        "8-10": {Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_8_10}
    }),

    ({'natural': 'water'}, {Style.COLOR.value: WATER_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.value: WATER_COLOR_ZOOM_8_10}}),
]

amenity_styles_area: ElementStyles = [
    ({'amenity': 'grave_yard'}, {
        Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_1_7,
    }, {
        "8-10": {Style.COLOR.value: GREEN_AREA_COLOR_ZOOM_8_10},
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 5, "9": 1.6}, Style.WIDTH.value),
        "9-10": {Style.EDGE_COLOR.value: '#ada994',
                 Style.EDGE_ALPHA.value: 1, Style.EDGE_LINESTYLE.value: '-'}}),
]

boundary_styles: ElementStyles = [
    ({'boundary': 'national_park'}, {
        Style.COLOR.value: None, Style.EDGE_ALPHA.value: 1, Style.ZINDEX.value: 1
    }, {
        "6-10": {Style.EDGE_COLOR.value: '#a4c280'},
        "4-5": {Style.EDGE_COLOR.value: '#a3be85', Style.COLOR.value: '#a3be85', Style.ALPHA.value: 0.4},
        "1-3": {Style.EDGE_COLOR.value: '#779e47', Style.COLOR.value: '#779e47', Style.ALPHA.value: 0.4},
        **RESERVATION_EDGE_CUMULATIVE_SIZE
    }),
]
areas_with_ways: ElementStyles = [
    ([{'highway': ['pedestrian', 'footway']},
      {'amenity': ['parking', 'motorcycle_parking']}], {
        Style.COLOR.value: '#FFFFFF', Style.ZINDEX.value: 41,
        Style.EDGE_COLOR.value: NORMAL_WAY_EDGE_COLOR,
        Style.EDGE_ALPHA.value: 1, Style.EDGE_LINESTYLE.value: '-'
    }, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 6, "9": 1.6, "8": 1.8, "7": 1.8, "4-6": 1.6},
            Style.WIDTH.value)
    }),
]

area_styles_default: ElementStyles = [
    ({'boundary': ''}, {
        Style.COLOR.value: None, Style.EDGE_COLOR.value: None,
        Style.EDGE_LINESTYLE.value: '-'
    }),

    # ({'natural': ''}, {Style.COLOR.value: None}),
    # ({'landuse': ''},  {Style.COLOR.value: None}),
    # ({'leisure': ''}, {Style.COLOR.value: None}),

    ({'aeroway': ''}, {Style.COLOR.value: INDUSTRIAL_AREA_COLOR_ZOOM_5_6}),
    ({'building': ''}, {Style.COLOR.value: '#e1d4bb'},
     {"7": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_7},
      "1-6": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),

    ({'amenity': ''}, {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_8_10},
     {"7": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_7},
      "1-6": {Style.COLOR.value: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),


    ([], {
        Style.ALPHA.value: 1.0
    })
]

AREAS_STYLES: ElementStyles = [
    *areas_with_ways,
    *boundary_styles,
    *natural_styles_area,
    *landuse_styles_area,
    *leisure_styles_area,
    *building_styles_area,
    *amenity_styles_area,
    *area_styles_default
]

MAPYCZ_BASE_OSM_CONFIG = BASE_OSM_CONFIG.copy()
# check what to do with gpx styles
MAPYCZ_STYLE: dict[str, dict[str, any]] = {
    "variables": {
        MapThemeVariable.GPXS_STYLES_SCALE: GPXS_STYLES_SCALE,
        MapThemeVariable.NODES_STYLES_SCALE: NODES_STYLES_SCALE,
        MapThemeVariable.WAYS_STYLES_SCALE: WAYS_STYLES_SCALE,
        MapThemeVariable.AREAS_STYLES_SCALE: AREAS_STYLES_SCALE,
        MapThemeVariable.WATER_COLOR: WATER_COLOR,
        MapThemeVariable.LAND_COLOR: LAND_COLOR,
        MapThemeVariable.AREAS_OVER_WAYS_FILTER: AREAS_OVER_WAYS_FILTER,
        MapThemeVariable.TEXT_BB_EXPAND_PERCENT: TEXT_EXPAND_PERCENT,
        MapThemeVariable.MARKER_BB_EXPAND_PERCENT: MARKER_EXPAND_PERCENT,
    },
    "styles": {
        'gpxs': GPXS_STYLES,
        'nodes': NODES_STYLES,
        'ways': WAYS_STYLES,
        'areas': AREAS_STYLES
    }
}
