from common.custom_types import ElementStyles, FeatureStyles
from common.map_enums import Style, TextPositions, MinPlot, MarkerPosition, MarkersCodes, LineCupStyles, MapThemeVariable
from config import font_awesome_prop, material_design_prop
from modules.utils import Utils
#! edge linestyle is suported only dashed or not dashed on not solid lines
#! ploting is turned of by setting color to None
#! text or marker turn of by setting marker/textcolor to 'None', marker edge or text edge by setting edge to 'None' and same for center
# if want to turn of only like only marker but text print like annotation set marker to "None"
# ------------styles--------------
# all from styles to dict and that export
# non scaled styles - relative to paper size (not polygons)
GPXS_STYLES_SCALE = []
# (filer for split from areas, filter for ploting)
AREAS_OVER_WAYS_FILTER = ([{'highway': ['pedestrian', 'footway']}, {'amenity': ['parking', 'motorcycle_parking']}],
                          [{'highway': ['pedestrian', 'footway'], 'area': 'yes'},
                           {'highway': ['pedestrian', 'footway'],
                               'place': ['square']},
                           {'amenity': ['parking', 'motorcycle_parking']}])

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

RESERVATION_EDGE_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier(
    {"10-10": 40, "9-9": 2, '8-8': 2, "7-7": 2, "6-5": 1.5,
     "4-3": 1.2, "2-1": 1.4
     }, Style.WIDTH.name)

WATER_COLOR = {"1-7": WATER_COLOR_ZOOM_1_7, "8-10": WATER_COLOR_ZOOM_8_10}
LAND_COLOR = '#f1f0e5'

DASHED_LAND_WAYS_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier(
    {"10-10": 7, '9-9': 1.1, '8-8': 1.5, "7-4": 2, "3-1": 1.5},
    Style.WIDTH.name)

SMALL_NONDASHED_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier(
    {"10-10": 12, "9-8": 1.1, "7-4": 1.5, "3-1": 1.4},
    Style.WIDTH.name)

SPECIAL_WAYS_CUMULATIVE_SIZE = Utils.cumulative_zoom_size_multiplier({
    "10-9": 19, "8-8": 1.4, "7-4": 2, "3-1": 1.5},
    Style.WIDTH.name)

# -------------------gpx-------------------
root_files_styles: ElementStyles = [
    ({'fileName': 'Grilovačka.gpx'}, {Style.COLOR.name: "Red"}),
]

folders_styles: ElementStyles = [
    ({'folder': 'pěšky'}, {Style.COLOR.name: "Blue"}),
    ({'folder': 'Kolo testování'}, {Style.WIDTH.name: 1, Style.ALPHA.name: 0.7}),
    ({'folder': 'Kolo'}, {Style.COLOR.name: "Purple"}),
]

gpxs_styles_default: ElementStyles = [
    ({'fileName': ''}, {Style.COLOR.name: 'Red', Style.WIDTH.name: 1,
     Style.ALPHA.name: 0.7,  Style.ZINDEX.name: 0}),
    ({'folder': ''}, {Style.COLOR.name: 'Orange', Style.WIDTH.name: 1,
     Style.ALPHA.name: 0.7,  Style.ZINDEX.name: 0}),
    ([], {Style.COLOR.name: 'Green', Style.WIDTH.name: 1, Style.ALPHA.name: 1.0, Style.LINESTYLE.name: "-",
          Style.START_MARKER.name: "o",
          Style.START_MARKER_WIDTH.name: 2, Style.START_MARKER_EDGE_RATIO.name: 0.1,
          Style.START_MARKER_COLOR.name: "#18ac0d", Style.START_MARKER_EDGE_COLOR.name: "#FFFFFF", Style.START_MARKER_ALPHA.name: 1.0,
          Style.FINISH_MARKER.name: "\uf11e",
          Style.FINISH_MARKER_HORIZONTAL_ALIGN.name: "left", Style.FINISH_MARKER_VERTICAL_ALIGN.name: "bottom",
          Style.FINISH_MARKER_WIDTH.name: 12, Style.FINISH_MARKER_EDGE_RATIO.name: 0.1,
          Style.FINISH_MARKER_COLOR.name: "#000000", Style.FINISH_MARKER_EDGE_COLOR.name: "#FFFFFF", Style.FINISH_MARKER_ALPHA.name: 1.0,
          Style.FINISH_MARKER_FONT_PROPERTIES.name: font_awesome_prop,
          Style.GPX_ABOVE_TEXT.name: True, Style.MARKER_LAYER_POSITION.name: MarkerPosition.UNDER_TEXT_OVERLAP
          })
]

GPXS_STYLES: ElementStyles = [
    *folders_styles,  # folder must be first - folder have only some byt file name have all
    *root_files_styles,
    *gpxs_styles_default,
]


# -------------------nodes-------------------
# zorder: castle: 28, towers: 29 peaks: 30, place names 40-50,

NODES_STYLES_SCALE = []
place_styles: ElementStyles = [
    ({'place': 'city', 'capital': 'yes'}, {Style.ZINDEX.name: 51},
     {"4-6": {Style.TEXT_FONT_SIZE.name: 16, Style.TEXT_WEIGHT.name: 'bold'},
      "1-3": {Style.TEXT_FONT_SIZE.name: 13, Style.TEXT_WEIGHT.name: 'bold'},
      "1-2": {Style.WIDTH.name: 5}
      }),

    ([{'place': 'city'}, {'place': 'town', 'capital': 'yes'}], {
        Style.ZINDEX.name: 50,
    },
        {
        "4-10": {Style.TEXT_FONT_SIZE.name: 15},
        "1-3": {Style.TEXT_FONT_SIZE.name: 12},
        "2-7": {Style.TEXT_WEIGHT.name: 'bold'},
        "1-2": {Style.MARKER.name: "o", Style.COLOR.name: CITY_POINT_COLOR, Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                Style.EDGE_WIDTH_RATIO.name: 0.15, Style.WIDTH.name: 4, Style.EDGE_COLOR.name: CITY_POINT_EDGE_COLOR}
    }),

    ({'place': 'town'}, {
        Style.ZINDEX.name: 49
    },
        {
        "7-10": {Style.TEXT_FONT_SIZE.name: 13},
        "5-6": {Style.TEXT_FONT_SIZE.name: 12},
        "4": {Style.TEXT_FONT_SIZE.name: 11.5},
        "3": {Style.TEXT_FONT_SIZE.name: 9},
        "4-7": {Style.TEXT_WEIGHT.name: 'bold'},
        "1-2": {Style.TEXT_FONT_SIZE.name: 8, Style.MARKER.name: "o", Style.COLOR.name: CITY_POINT_COLOR, Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                Style.EDGE_WIDTH_RATIO.name: 0.15, Style.WIDTH.name: 3.3, Style.EDGE_COLOR.name: CITY_POINT_EDGE_COLOR}
    }),
    ({'place': 'village'}, {
        Style.ZINDEX.name: 48
    },
        {
        "6-10": {Style.TEXT_FONT_SIZE.name: 10},
        "4-5": {Style.TEXT_FONT_SIZE.name: 8},
        "1-3": {Style.TEXT_FONT_SIZE.name: 7},
        "1-2": {Style.MARKER.name: "o", Style.COLOR.name: CITY_POINT_COLOR, Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                Style.EDGE_WIDTH_RATIO.name: 0.15, Style.WIDTH.name: 2.8, Style.EDGE_COLOR.name: CITY_POINT_EDGE_COLOR}
    }),

    ({'place': 'suburb'}, {
        Style.ZINDEX.name: 47
    },
        {
        "1-7": {Style.TEXT_COLOR.name: '#454444'},
        "6-10": {Style.TEXT_FONT_SIZE.name: 8},
        "1-5": {Style.TEXT_FONT_SIZE.name: 7},
    }),

    ({'place': 'neighbourhood'}, {
        Style.ZINDEX.name: 46, Style.TEXT_COLOR.name: '#616060', Style.TEXT_FONT_SIZE.name: 6
    }),

    ({'place': 'locality'}, {
        Style.ZINDEX.name: 24, Style.TEXT_COLOR.name: '#616060', Style.TEXT_FONT_SIZE.name: 5
    }),
]


# text color or MARKER color turn of by string "None" instead of None
natural_styles_nodes: ElementStyles = [
    ({'natural': 'peak'}, {
        Style.ZINDEX.name: 30, Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT2.name,
        # marker
        Style.MARKER.name: "^", Style.MARKER_HORIZONTAL_ALIGN.name: "center", Style.TEXT_FONTFAMILY.name: 'Georgia',
        Style.COLOR.name: "#443833", Style.EDGE_COLOR.name: "None", Style.WIDTH.name: 3,
        # text
        Style.TEXT_WEIGHT.name: 'heavy', Style.TEXT_STYLE.name: 'italic', Style.TEXT_FONT_SIZE.name: 6,
        Style.TEXT_COLOR.name: "#443833", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF',
        Style.TEXT1_POSITIONS.name: [TextPositions.TOP], Style.TEXT2_POSITIONS.name: [TextPositions.BOTTOM],
        Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.3, Style.TEXT_WRAP_LEN.name: 20
    })
]

icons_above_styles_nodes: ElementStyles = [
    ({'man_made': 'tower', 'tower:type': ['observation', 'watchtower']}, {
        Style.MIN_PLOT_REQ.name: MinPlot.MARKER.name, Style.ZINDEX.name: 20,
        # marker
        Style.MARKER.name: MarkersCodes.FA_TOWER_OBSERVATION.value, Style.MARKER_FONT_PROPERTIES.name: font_awesome_prop,
        Style.COLOR.name: "#99441e", Style.EDGE_COLOR.name: "#FFFFFF", Style.WIDTH.name: 7,
        Style.EDGE_WIDTH_RATIO.name: 0.15, Style.MARKER_LAYER_POSITION.name: MarkerPosition.ABOVE_NORMAL,
        # text
        Style.TEXT_COLOR.name: "#8c7359", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF', Style.TEXT_FONT_SIZE.name: 5,
        Style.TEXT1_POSITIONS.name: [TextPositions.BOTTOM], Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2,
        Style.TEXT_WRAP_LEN.name: 20
    }),

    ({'historic': ['castle']}, {
        Style.MIN_PLOT_REQ.name: MinPlot.MARKER.name, Style.ZINDEX.name: 19,
        # marker
        Style.MARKER.name: MarkersCodes.MU_CASTLE.value, Style.MARKER_FONT_PROPERTIES.name: material_design_prop,
        Style.COLOR.name: "#846252", Style.EDGE_COLOR.name: "#FFFFFF", Style.WIDTH.name: 7,
        Style.EDGE_WIDTH_RATIO.name: 0.15,
        # text
        Style.TEXT_FONT_SIZE.name: 5,
        Style.TEXT_COLOR.name: "#8c7359", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF',
        Style.TEXT1_POSITIONS.name: [TextPositions.BOTTOM], Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2,
        Style.TEXT_WRAP_LEN.name: 20
    })
]

nodes_styles_default: ElementStyles = [
    ({'natural': ''}, {
    }),

    # natural must be before place - some peaks are also places
    ({'place': ''}, {
        Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2, Style.MIN_PLOT_REQ.name: MinPlot.TEXT1.name,
        Style.TEXT_COLOR.name: "#000000", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF',
        Style.TEXT1_POSITIONS.name: [
            TextPositions.TOP, TextPositions.BOTTOM, TextPositions.RIGHT]
    }),
    ([], {

        Style.ALPHA.name: 1, Style.EDGE_ALPHA.name: 1,
        Style.TEXT_FONTFAMILY.name: 'Arial',
        Style.TEXT_STYLE.name: 'normal',
        Style.TEXT_WEIGHT.name: 'normal', Style.TEXT_WRAP_LEN.name: 15
    })
]

NODES_STYLES: ElementStyles = [
    *icons_above_styles_nodes,
    *natural_styles_nodes,
    *place_styles,
    *nodes_styles_default,
]
# -------------------ways------------------
# styles that must be assigned to all way features
# scaled styles - relative to polygon (not paper)
WAYS_STYLES_SCALE = [Style.WIDTH.name]
# dashed highways z index 0-waterways, 1-14 - dashedways, 15-20 - barrier, 21-50 normal ways or areas as ways, 60-70 aeroway, 70-80 - aerialway, 90 - 100 (subway - 20) - railways

# bridges overwrite because bridge have separated styles with bridge..
highway_styles_bridges_overwrite: ElementStyles = [
    ({'highway': '', 'bridge': ''}, {Style.EDGE_COLOR.name: None,
                                     })]

# add highway bridge and tunnel styles
highway_styles_tunnels: ElementStyles = [
    ([{'highway': ['motorway', 'motorway_link'],
     'tunnel': ''},
      {'highway': ['motorway', 'motorway_link'],
      'covered': ''}
      ],
     {Style.COLOR.name: "#a9de86", Style.EDGE_COLOR.name: "#629157"}),

    ([{'highway': ['trunk', 'trunk_link'], 'tunnel': ''},
      {'highway': ['trunk', 'trunk_link'], 'covered': ''}],
     {Style.COLOR.name: "#a9de86", Style.EDGE_COLOR.name: "#629157"}),

    ([{'highway': ['primary', 'primary_link'], 'tunnel': ''},
      {'highway': ['primary', 'primary_link'], 'covered': ''}],
     {Style.COLOR.name: "#ffe6bd", Style.EDGE_COLOR.name: "#e8a542"}),

    ([{'highway': ['secondary', 'secondary_link'],
     'tunnel': ''},
      {'highway': ['secondary', 'secondary_link'],
       'covered': ''}
      ], {Style.COLOR.name: "#fbf8b0", Style.EDGE_COLOR.name: "#cdc139"}),
    
    # default color and all edge styles
    ([{'highway': '', 'tunnel': '', 'bridge': '~'}, {'highway': '', 'covered': '', 'bridge': '~'}],
     {Style.EDGE_LINESTYLE.name: (2, (3, 1)),
      Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
      Style.COLOR.name: "#FFFFFF", Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR, Style.LINESTYLE.name: "-"})]

highway_styles_main: ElementStyles = [
    ({'highway': 'motorway'}, {Style.COLOR.name: '#9bd772', Style.ZINDEX.name: 50,
                               Style.EDGE_COLOR.name: "#629157"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 42, "9": 1.3, "8": 1.5, "7": 1.8, "6": 1.9, "5": 0.8,
            "4": 1.6, "3": 1.6, "2": 1.6, "1-1": 1.4},
            Style.WIDTH.name),
        "6-8": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
        "4-5": {Style.EDGE_WIDTH_RATIO.name: 1 + 2,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 2,
                Style.PLOT_WITHOUT_CROSSING.name: True},
        "2-3": {Style.EDGE_WIDTH_RATIO.name: 1 + 2.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 2.5,
                Style.PLOT_WITHOUT_CROSSING.name: True},
        "1": {Style.EDGE_WIDTH_RATIO.name: 1 + 3,
              Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 3,
              Style.PLOT_WITHOUT_CROSSING.name: True}
    }),

    ({'highway': 'trunk'}, {Style.COLOR.name: '#9bd772', Style.ZINDEX.name: 49,
     Style.EDGE_COLOR.name: "#629157"},
     {
         **Utils.cumulative_zoom_size_multiplier({
             "10": 42, "9": 1.3, "8": 1.4, "7": 1.7, "6": 1.8, "5": 1.4,
             "4": 1.6, "3": 1.7, "2": 1.6, "1-1": 1.4},
             Style.WIDTH.name),
         "6-7": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.6,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.6},
         "3-5": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.8,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.8},
        "1-2": {Style.EDGE_WIDTH_RATIO.name: 1 + 1.3,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 1.3}
    }),

    ({'highway': 'primary'}, {Style.COLOR.name: '#ffcc78', Style.ZINDEX.name: 48,
     Style.EDGE_COLOR.name: "#e8a542"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 42, "9": 1.3, "8": 1.4, "7": 1.7, "6": 1.8, "5": 1.3,
            "4": 1.6, "3": 1.7, "2": 1.6, "1-1": 1.4},
            Style.WIDTH.name),
         "6-8": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.6,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.6},
         "2-5": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.8,
                 Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.8},
        "1": {Style.EDGE_WIDTH_RATIO.name: 1 + 1.3,
              Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 1.3},
    }),

    ({'highway': 'secondary'}, {Style.COLOR.name: '#faef75', Style.ZINDEX.name: 47,
                                Style.WIDTH.name: 20, Style.EDGE_COLOR.name: "#cdc139"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 40, "9": 1.2, "8": 1.4, "7": 1.8, "6": 1.5,
            "5": 1.5, "4": 1.6, "1-3": 1.6},
            Style.WIDTH.name),
        "7-9": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
        "1-6": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.7},
    }),

    ({'highway': 'tertiary'}, {Style.ZINDEX.name: 43, Style.COLOR.name: NORMAL_WAY_COLOR,
                               Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR}, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 40, "9": 1.2, "8": 1.4, "7": 1.8, "6": 1.5,
            "5": 1.5, "1-4": 1.2},
            Style.WIDTH.name),
        "7-9": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
        "1-6": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.7},
    }),

    ({'highway': 'motorway_link'}, {Style.COLOR.name: '#9bd772', Style.ZINDEX.name: 46,
     Style.EDGE_COLOR.name: "#629157"}),

    ({'highway': 'trunk_link'}, {Style.COLOR.name: '#9bd772', Style.ZINDEX.name: 45,
                                 Style.EDGE_COLOR.name: "#629157"}),

    ({'highway': 'primary_link'}, {Style.COLOR.name: '#ffcc78', Style.ZINDEX.name: 44,
                                   Style.EDGE_COLOR.name: "#e8a542"}),

    ({'highway': ['motorway_link', 'trunk_link', 'primary_link']}, {}, {
        **Utils.cumulative_zoom_size_multiplier({
            "9-10": 32, "8": 1.3, "7": 1.8, "6": 1.8, "5": 1.3,
            "4": 1.7, "3": 1.6, "2": 1.4, "1": 1.4},
            Style.WIDTH.name),
        "9": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
              Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
        "1-8": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.8,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.8}
    }),

    ({'highway': 'secondary_link'}, {Style.COLOR.name: '#faef75', Style.ZINDEX.name: 43,
     Style.EDGE_COLOR.name: "#cdc139"}, {
        **Utils.cumulative_zoom_size_multiplier({
            "9-10": 30, "8": 1.3, "7": 1.7, "6": 1.6, "5": 1.3,
            "1-4": 1.6},
            Style.WIDTH.name),
        "9": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
              Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
        "1-8": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.8,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.8}
    }),

    ({'highway': 'tertiary_link'}, {Style.ZINDEX.name: 42}),

    ({'highway': ['residential', 'unclassified', 'pedestrian', 'tertiary_link']},
     {Style.ZINDEX.name: 40, Style.COLOR.name: NORMAL_WAY_COLOR,
      Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR},
     {
        **Utils.cumulative_zoom_size_multiplier(
            {"9-10": 27, "8": 1.3, "7": 1.8, "6-3": 1.8, "2-1": 1.5}, Style.WIDTH.name),
        "7-8": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
        "1-6": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.8,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.8},
    }),
]

highway_styles_surface_special_and_paths: ElementStyles = [

    # to non dashed
    ({'highway': ['track', 'cycleway'],
      'surface': ['asphalt'],
      'tracktype': ('~grade3', '~grade4', '~grade5'),
      },
     {Style.ZINDEX.name: 35, Style.COLOR.name: "#d4d2cf", Style.EDGE_COLOR.name: "#a49d84",
      Style.LINESTYLE.name: "-", Style.EDGE_LINESTYLE.name: "-"},
     {
        **SPECIAL_WAYS_CUMULATIVE_SIZE,
        "1-8": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.7},

        "8-10": {Style.COLOR.name: "#ebe8e4", Style.EDGE_COLOR.name: "#9a9275"},
        "7": {Style.COLOR.name: "#e1dedb", Style.EDGE_COLOR.name: "#a2967c"}}),

    ([{'highway': ['path', 'track'],
      'surface': ['asphalt', 'concrete', 'paving_stones', 'sett', 'cobblestone',
                  'compacted', 'fine_gravel'],
       'tracktype': ('~grade3', '~grade4', '~grade5')},
      {'highway': ['path', 'track'],
        'tracktype': ['grade1', 'grade2']}],
     {Style.ZINDEX.name: 33, Style.COLOR.name: NORMAL_WAY_COLOR, Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR,
      Style.LINESTYLE.name: "-", Style.EDGE_LINESTYLE.name: "-"},
     {
        **SMALL_NONDASHED_CUMULATIVE_SIZE,
        "9": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
              Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
        # on smaller zoom, change to line without edge
        "1-8": {Style.COLOR.name: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.name: None,
                Style.PLOT_ON_BRIDGE.name: True}
    }),

    ({'highway': ['footway'],
      'surface': ['unpaved', 'gravel', 'pebblestone', 'rock', 'dirt',
                  'ground', 'grass', 'sand', 'mud', 'woodchips']},
     {Style.COLOR.name: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.name: None,
      Style.LINESTYLE.name: (3, (5, 4)), Style.ZINDEX.name: 10,
      Style.PLOT_ON_BRIDGE.name: False},
     {**DASHED_LAND_WAYS_CUMULATIVE_SIZE,
      "1-6": {Style.PLOT_ON_BRIDGE.name: True}}
     ),
]

highway_styles_special_and_paths: ElementStyles = [

    ({'highway': 'service'}, {Style.ZINDEX.name: 37, Style.COLOR.name: NORMAL_WAY_COLOR,
                              Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR}),

    ({'highway': 'raceway'}, {Style.COLOR.name: NORMAL_WAY_COLOR, Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR,
                              Style.ZINDEX.name: 35},
     {"7-10": {Style.COLOR.name: '#e1dedb',
               Style.EDGE_COLOR.name: "#a8a483"}
      }),

    ({'highway': ['raceway', 'service']}, {},
     {
        **SPECIAL_WAYS_CUMULATIVE_SIZE,
        "1-9": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.7,
                Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.7},
    }),


    ({'highway': 'cycleway'}, {Style.ZINDEX.name: 36, Style.COLOR.name: NORMAL_WAY_COLOR,
                               Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR}, {
        "1-8": {Style.COLOR.name: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.name: None, Style.LINESTYLE.name: "-",
                Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.PLOT_ON_BRIDGE.name: True}
    }),

    ({'highway': 'steps'}, {Style.COLOR.name: NORMAL_WAY_COLOR, Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR,
                            Style.LINESTYLE.name: (2, (3, 0.2)),
                            Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value,
                            Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
                            Style.PLOT_ON_BRIDGE.name: False, Style.ZINDEX.name: 31},
     {"1-8": {Style.COLOR.name: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.name: None, Style.LINESTYLE.name: "-",
              Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.PLOT_ON_BRIDGE.name: True}}),

    ({'highway': 'footway'}, {Style.ZINDEX.name: 30, Style.COLOR.name: NORMAL_WAY_COLOR,
                              Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR, },
     {"1-8": {Style.COLOR.name: UNPAVED_WAY_COLOR, Style.EDGE_COLOR.name: None, Style.LINESTYLE.name: "-",
              Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.PLOT_ON_BRIDGE.name: True}
      }),

    ({'highway': ['footway', 'steps', 'cycleway']}, {},
     {**SMALL_NONDASHED_CUMULATIVE_SIZE,
      "9": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
            Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.5},
      }),


    ({'highway': 'track'}, {Style.ZINDEX.name: 14, Style.COLOR.name: UNPAVED_WAY_COLOR, Style.LINESTYLE.name: (7, (10, 4)),
     Style.EDGE_COLOR.name: None, Style.PLOT_ON_BRIDGE.name: None},
     {"1-7": {Style.PLOT_ON_BRIDGE.name: True}}),
    ({'highway': 'path'}, {Style.ZINDEX.name: 13, Style.COLOR.name: UNPAVED_WAY_COLOR, Style.LINESTYLE.name: (3, (5, 4)),
     Style.EDGE_COLOR.name: None, Style.PLOT_ON_BRIDGE.name: None},
     {"1-7": {Style.PLOT_ON_BRIDGE.name: True}}),
    ({'highway': ['path', 'track']}, {}, {
        **DASHED_LAND_WAYS_CUMULATIVE_SIZE
    }
    ),
]


railway_styles_bridges_overwrite: ElementStyles = [
    ({'railway': ['funicular', 'subway'], 'bridge': ''}, {
        Style.BRIDGE_EDGE_COLOR.name: None, Style.BRIDGE_COLOR.name: None
    }),
    ({'railway': ['subway'], 'bridge': ''}, {
        Style.COLOR.name: '#FFFFFF',
        Style.EDGE_COLOR.name: '#939393',
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
    })
]

railway_styles_tunnels: ElementStyles = [
    ([{'railway': ['rail', 'light_rail', "monorail", 'miniature'], 'tunnel': ''},
     {'railway': ['rail', 'light_rail', "monorail", 'miniature'], 'covered': ''}], {
        Style.COLOR.name: None, Style.EDGE_LINESTYLE.name: (3, (7, 4)),
        Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value
    }),

    ([{'railway': 'tram', 'tunnel': ''},
     {'railway': 'tram', 'covered': ''}], {
        Style.LINESTYLE.name: (3, (7, 4)),
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value
    }),

    ([{'railway': 'funicular', 'tunnel': ''},
     {'railway': 'funicular', 'covered': ''}], {
        Style.COLOR.name: None,
        Style.EDGE_WIDTH_RATIO.name: 0.4,
        Style.EDGE_LINESTYLE.name: (2, (3, 2)),
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value,
    })
]

railway_styles_service: ElementStyles = [
    ({'railway': ['rail', 'disused', 'light_rail', "monorail", "subway"],
      'service': ['crossover', 'siding', 'spur', 'yard']}, {
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 8, "9": 1.2, "8": 1.8, "4-7": 1.7, "1-3": 1.5}, Style.WIDTH.name)
    })]

railway_styles: ElementStyles = [
    # for osm light_rail, monorail is just line, subway is line but with different color

    ({'railway': ['rail', 'disused', 'light_rail', "monorail", 'miniature']}, {
        Style.COLOR.name: '#FFFFFF', Style.EDGE_COLOR.name: '#707070',
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.5,
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
        Style.ZINDEX.name: 100
    }),
    # 3
    ({'railway': 'subway'}, {
        Style.COLOR.name: '#939392', Style.LINESTYLE.name: (3, (7, 4)),
        Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
        Style.EDGE_COLOR.name: None,
        Style.ZINDEX.name: 20
    }),

    ({'railway': ['rail', 'disused', 'light_rail', "monorail", 'miniature', "subway"]}, {},
     {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 11, "9": 1.2, "8": 1.6, "7": 2.1,
                "6": 2.3, "5": 2, "2-4": 1.3, "1": 1.3},
            Style.WIDTH.name)
    }),

    ({'railway': 'funicular'}, {
        Style.ZINDEX.name: 99,
        Style.COLOR.name: '#FFFFFF',
        Style.EDGE_COLOR.name: '#474747',
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_LINESTYLE.name: (0, (5, 5)),
        Style.EDGE_WIDTH_RATIO.name: 1 + 0.8, Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.name: 0.4,
        Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.ROUND.value
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "8-9": 2, "7": 2,
                "1-6": (1.8, {Style.LINESTYLE.name: (0, (4, 8))})},
            Style.WIDTH.name),
    }),

    ({'railway': 'tram'}, {
        Style.COLOR.name: '#404040'
    },
        {**Utils.cumulative_zoom_size_multiplier(
         {"10": 4, "9": 1.5, "6-8": 1.2, "1-5": 1.3},
         Style.WIDTH.name)}
    ),

]


aerialway_styles: ElementStyles = [
    ({'aerialway': ['cable_car', 'gondola', 'mixed_lift']}, {
        Style.COLOR.name: '#FFFFFF',
        Style.EDGE_LINESTYLE.name: "--",
        Style.LINESTYLE.name: (0, (4, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.6,
        Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.name: 0.3, Style.ZINDEX.name: 80
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "8-9": 2, "7": 2,
                "3-6": 1.8, "1-2": 1.5},
            Style.WIDTH.name),
        "1-6": {Style.LINESTYLE.name: (0, (4, 8))}
    }),

    ({'aerialway': ['chair_lift']}, {
        Style.LINESTYLE.name: (0, (3, 5)),
        Style.EDGE_LINESTYLE.name: '-', Style.EDGE_WIDTH_RATIO.name: 0.3,
        Style.ZINDEX.name: 79
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "9": 1.5, "8": 1.3, "7": 1.6,
                "3-6": 2.4, "1-2": 1.5},
            Style.WIDTH.name),
        "1-6": {Style.LINESTYLE.name: (0, (3, 8))}
    }),
]

aeroway_styles: ElementStyles = [
    ({'aeroway': 'runway'}, {
        Style.ZINDEX.name: 70,
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 60, "9": 2, "8": 1.3, "5-7": 1.7, "1-4": 1.5},
            Style.WIDTH.name),
        "6": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.3},
        "1-5": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.6},
    }),
    ({'aeroway': 'taxiway'}, {
        Style.WIDTH.name: 30,
        Style.ZINDEX.name: 69,
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 30, "8-9": 1.5, "7": 1.3, "5-6": 1.6, "1-4": 2},
            Style.WIDTH.name),
        "1-6": {Style.EDGE_WIDTH_RATIO.name: 1 + 0.5},
    }),
]

waterway_styles_tunnels: ElementStyles = [
    ([{'waterway': '', 'tunnel': '', 'intermittent': "yes"},
     {'waterway': '', 'covered': '', 'intermittent': "yes"}], {
     Style.LINESTYLE.name: (0, (1, 1)), Style.EDGE_COLOR.name: None}),
    ([{'waterway': '', 'tunnel': ''},
      {'waterway': '', 'covered': ''}], {Style.LINESTYLE.name: "--", Style.EDGE_COLOR.name: None})]

waterway_styles: ElementStyles = [
    ({'waterway': '', 'intermittent': "yes"}, {Style.LINESTYLE.name: (0, (1, 1)),
                                               Style.EDGE_COLOR: None}),
    ({'waterway': ['river']}, {}, {
        **Utils.cumulative_zoom_size_multiplier(
            {"8-10": 65, "7": 2, "6": 2, "5": 1.8,
                "4": 1.1, "3": 1.2, "2": 1.7, "1": 1.8},
            Style.WIDTH.name)
    }),

    ({'waterway': ['canal']}, {}, {
        **Utils.cumulative_zoom_size_multiplier(
            {"8-10": 30, "7": 1.8, "6": 1.7, "3-5": 1.7, "1-2": 1.4},
            Style.WIDTH.name)
    }),
]


ways_styles_default: ElementStyles = [
    ({'highway': ''}, {
        Style.EDGE_WIDTH_RATIO.name: 1 + 0.3,
        Style.COLOR.name: NORMAL_WAY_COLOR,
        Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR
    }),
    ({'highway': '', 'bridge': ''}, {
        Style.BRIDGE_EDGE_LINESTYLE.name: '-', Style.BRIDGE_LINESTYLE.name: '-',
        Style.BRIDGE_WIDTH_RATIO.name: 1, Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.3,
        Style.BRIDGE_EDGE_COLOR.name: "#83877e", Style.BRIDGE_COLOR.name: "#FFFFFF",
        Style.PLOT_ON_BRIDGE.name: True
    }),

    ({'railway': ''}, {
        Style.ZINDEX.name: 90
    }),
    ({'railway': '', 'bridge': ''}, {
        Style.BRIDGE_EDGE_LINESTYLE.name: '-', Style.BRIDGE_LINESTYLE.name: '-',
        Style.BRIDGE_EDGE_COLOR.name: '#707070', Style.BRIDGE_COLOR.name: "#FFFFFF",
        Style.BRIDGE_WIDTH_RATIO.name: 1 + 1.6, Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.3,
        Style.PLOT_ON_BRIDGE.name: True,
    }),

    ({'aeroway': ''}, {
        Style.COLOR.name: NORMAL_WAY_COLOR, Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR,
        Style.EDGE_WIDTH_RATIO.name: 1 + 0.2,
    }),

    ({'aerialway': ''}, {
        Style.COLOR.name: '#606060',
        Style.EDGE_COLOR.name: '#606060', Style.EDGE_LINESTYLE.name: '-',
        Style.LINESTYLE.name: (0, (0.1, 3)), Style.EDGE_WIDTH_RATIO.name: 0.3,
        Style.ZINDEX.name: 70
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 20, "9": 1.5, "8": 1.2, "7": 1.5,
                "1-6": (2.2, {Style.LINESTYLE.name: (0, (0.1, 8))})},
            Style.WIDTH.name)
    }),

    ({'barrier': ''}, {
        Style.ZINDEX.name: 15,
        Style.COLOR.name: "#909090"
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"9-10": 8, "5-8": 1.5, "1-4": 1.4},
            Style.WIDTH.name),
    }),

    ({'route': 'ferry'}, {
        Style.COLOR.name: '#7394b4', Style.LINESTYLE.name: (0, (5, 4)),
        Style.ZINDEX.name: 1, Style.EDGE_COLOR.name: None
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 8, "9": 1.5, "8": 1.8, "7": 1.7, "6": 2, "5": 2,
             "4": 2.1, "3": 2, '2': 2, '1': 1.3},
            Style.WIDTH.name),
    }),

    ({'waterway': ''}, {
        Style.COLOR.name: WATER_COLOR_ZOOM_1_7,
        Style.ZINDEX.name: 0, Style.EDGE_COLOR.name: None
    }, {
        **Utils.cumulative_zoom_size_multiplier(
            {"9-10": 10, "8": 1.7, "7": 1.8, "6": 2, "3-5": 2, "1-2": 1.4},
            Style.WIDTH.name),
        "8-10": {Style.COLOR.name: WATER_COLOR_ZOOM_8_10}}),


    ([], {
        Style.ALPHA.name: 1.0, Style.EDGE_ALPHA.name: 1.0,
        Style.LINESTYLE.name: '-', Style.EDGE_LINESTYLE.name: '-',
        Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.ROUND.value,
    }),
]


WAYS_STYLES: ElementStyles = [
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
AREAS_STYLES_SCALE = [Style.WIDTH.name]


landuse_styles_area: ElementStyles = [

    ({'landuse': 'farmland'}, {Style.COLOR.name: '#EDEDE0'}),
    ({'landuse': ['vineyard', 'orchard']}, {Style.COLOR.name: '#e1ebbe'}),

    ({'landuse': ['basin', 'salt_pond']}, {Style.COLOR.name: WATER_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.name: WATER_COLOR_ZOOM_8_10}}),
    ({'landuse': ['forest', 'recreation_ground', 'meadow', 'grass', 'cemetery']},
     {Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_1_7}, {
        "8-10": {Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_8_10}}),

    ({'landuse': 'cemetery'}, {}, {
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 5, "9": 1.6}, Style.WIDTH.name),
        "9-10": {Style.EDGE_COLOR.name: '#ada994',
                 Style.EDGE_ALPHA.name: 1, Style.EDGE_LINESTYLE.name: '-'}
    }),

    ({'landuse': ['allotments', 'retail', 'residential', 'garages', 'commercial']}, {},
     {"8-10": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_8_10},
      "7": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_7},
      "1-6": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),

    ({'landuse': ['industrial', 'farmyard', 'brownfield', 'quarry', 'landfill']},
     {},
     {"8-10": {Style.COLOR.name: INDUSTRIAL_AREA_COLOR_ZOOM_8_10},
      "7": {Style.COLOR.name: INDUSTRIAL_AREA_COLOR_ZOOM_7},
      "5-6": {Style.COLOR.name: INDUSTRIAL_AREA_COLOR_ZOOM_7},
      "1-4": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),
]

leisure_styles_area: ElementStyles = [
    ({'leisure': ['garden', 'park']}, {Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_8_10}}),
    ({'leisure': ['golf_course', 'playground', 'pitch']},
     {Style.COLOR.name: '#e3edc6',
      Style.EDGE_ALPHA.name: 1, Style.EDGE_LINESTYLE.name: '-',
      Style.EDGE_COLOR.name: '#b5c48b'}, {
          **Utils.cumulative_zoom_size_multiplier({
              "10": 4, "9": 1.4, "8": 1.4, "7": 1.4, "1-6": 1.5},
              Style.WIDTH.name)
    }),
    ({'leisure': ['sports_centre']},
     {Style.COLOR.name: '#def7d3', Style.EDGE_ALPHA.name: 1, Style.EDGE_LINESTYLE.name: '-',
      Style.EDGE_COLOR.name: '#b5c48b'}, {
          **Utils.cumulative_zoom_size_multiplier({
              "10": 4, "9": 1.4, "8": 1.4, "7": 1.4, "1-6": 1.5},
              Style.WIDTH.name)
    }),
    ({'leisure': 'swimming_pool'}, {Style.COLOR.name: WATER_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.name: WATER_COLOR_ZOOM_8_10}}),
]

# dynamic change color based on zoom level
building_styles_area: ElementStyles = [
    ({'building': ['church', 'synagogue', 'cathedral', 'temple', 'monastery']}, {}, {
        "8-10": {Style.COLOR.name: '#908b84'}}),

    ([{'building': ['university', 'hospital', 'public', 'clinic', 'supermarket']},
      {'building': '', 'historic': ''}], {}, {  # same as historic..
        "8-10": {Style.COLOR.name: '#bab09a'}}),

    ({'building': ['industrial', 'warehouse']}, {}, {
        "8-10": {Style.COLOR.name: '#d4d1cc'},
        "7": {Style.COLOR.name: INDUSTRIAL_AREA_COLOR_ZOOM_7},
        "5-6": {Style.COLOR.name: INDUSTRIAL_AREA_COLOR_ZOOM_5_6}}),
]

natural_styles_area: ElementStyles = [

    ({'natural': ['heath', 'scrub', 'grassland', 'wood']}, {Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_1_7},
     {
        "8-10": {Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_8_10}
    }),

    ({'natural': ['water', 'bay']}, {Style.COLOR.name: WATER_COLOR_ZOOM_1_7},
     {"8-10": {Style.COLOR.name: WATER_COLOR_ZOOM_8_10}}),
]

amenity_styles_area: ElementStyles = [
    ({'amenity': 'grave_yard'}, {
        Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_1_7,
    }, {
        "8-10": {Style.COLOR.name: GREEN_AREA_COLOR_ZOOM_8_10},
        **Utils.cumulative_zoom_size_multiplier(
            {"10": 5, "9": 1.6}, Style.WIDTH.name),
        "9-10": {Style.EDGE_COLOR.name: '#ada994',
                 Style.EDGE_ALPHA.name: 1, Style.EDGE_LINESTYLE.name: '-'}}),
]

boundary_styles: ElementStyles = [
    ({'boundary': 'national_park'}, {
        Style.COLOR.name: None, Style.EDGE_ALPHA.name: 1, Style.ZINDEX.name: 1
    }, {
        "6-10": {Style.EDGE_COLOR.name: '#a4c280'},
        "4-5": {Style.EDGE_COLOR.name: '#a3be85', Style.COLOR.name: '#a3be85', Style.ALPHA.name: 0.4},
        "1-3": {Style.EDGE_COLOR.name: '#779e47', Style.COLOR.name: '#779e47', Style.ALPHA.name: 0.4},
        **RESERVATION_EDGE_CUMULATIVE_SIZE
    }),
]
areas_with_ways: ElementStyles = [
    ([{'highway': ['pedestrian', 'footway']},
      {'amenity': ['parking', 'motorcycle_parking']}], {
        Style.COLOR.name: '#FFFFFF', Style.ZINDEX.name: 41,
        Style.EDGE_COLOR.name: NORMAL_WAY_EDGE_COLOR,
        Style.EDGE_ALPHA.name: 1, Style.EDGE_LINESTYLE.name: '-'
    }, {
        **Utils.cumulative_zoom_size_multiplier({
            "10": 6, "9": 1.6, "8": 1.8, "7": 1.8, "1-6": 1.6},
            Style.WIDTH.name)
    }),
]

area_styles_default: ElementStyles = [
    ({'landuse': ''},  {Style.COLOR.name: LAND_COLOR}),
    ({'leisure': ''}, {Style.COLOR.name: LAND_COLOR}),
    ({'natural': ''}, {Style.COLOR.name: LAND_COLOR}),

    ({'aeroway': ''}, {Style.COLOR.name: INDUSTRIAL_AREA_COLOR_ZOOM_5_6}),
    ({'building': ''}, {Style.COLOR.name: '#e1d4bb'},
     {"7": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_7},
      "1-6": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),
    ({'amenity': ''}, {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_8_10},
     {"7": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_7},
      "1-6": {Style.COLOR.name: RESIDENTAL_AREA_COLOR_ZOOM_1_6}}),

    # areas that will be ploted with ways

    ({'boundary': ''}, {
        Style.COLOR.name: None, Style.EDGE_COLOR.name: None,
        Style.EDGE_LINESTYLE.name: '-'
    }),

    ([], {
        Style.COLOR.name: LAND_COLOR, Style.ALPHA.name: 1.0
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


# check what to do with gpx styles
MAPYCZSTYLE: dict[str, dict[str, any]] = {
    "variables": {
        MapThemeVariable.GPXS_STYLES_SCALE: GPXS_STYLES_SCALE,
        MapThemeVariable.NODES_STYLES_SCALE: NODES_STYLES_SCALE,
        MapThemeVariable.WAYS_STYLES_SCALE: WAYS_STYLES_SCALE,
        MapThemeVariable.AREAS_STYLES_SCALE: AREAS_STYLES_SCALE,
        MapThemeVariable.WATER_COLOR: WATER_COLOR,
        MapThemeVariable.LAND_COLOR: LAND_COLOR,
        MapThemeVariable.AREAS_OVER_WAYS_FILTER: AREAS_OVER_WAYS_FILTER,
    },
    "styles": {
        'gpxs': GPXS_STYLES,
        'nodes': NODES_STYLES,
        'ways': WAYS_STYLES,
        'areas': AREAS_STYLES
    }
}
