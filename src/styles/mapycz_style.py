from common.custom_types import ElementStyles, FeatureStyles
from common.map_enums import Style, TextPositions, MinPlot, MarkerAbove, MinLoad, LineCupStyles
from config import font_awesome_prop, material_design_prop

#! edge linestyle is suported only dashed or not dashed on not solid lines
#! ploting is turned of by setting color to None
#! text and marker turn of by setting marker/textcolor to None
# if want to turn of only like only marker but text print like annotation set marker to "None"
# ------------styles--------------
OCEAN_WATER = '#8fb6db'

GENERAL_DEFAULT_STYLES: FeatureStyles = {Style.COLOR.name: '#EDEDE0',  Style.ZINDEX.name: 0,
                                         Style.WIDTH.name: 1, Style.LINESTYLE.name: '-',
                                         Style.ALPHA.name: 1, Style.EDGE_COLOR.name: None, Style.EDGE_LINESTYLE.name: '-'}


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
]

gpxs_mandatory_styles: ElementStyles = [
    ([], {Style.COLOR.name: 'Green', Style.WIDTH.name: 1, Style.ALPHA.name: 1.0, Style.LINESTYLE.name: "-",
          Style.START_MARKER.name: "o",
          Style.START_MARKER_WIDHT.name: 2, Style.START_MARKER_EDGE_RATIO.name: 0.1,
          Style.START_MARKER_COLOR.name: "#18ac0d", Style.START_MARKER_EDGE_COLOR.name: "#FFFFFF", Style.START_MARKER_ALPHA.name: 1.0,
          Style.FINISH_MARKER.name: "\uf11e",
          Style.FINISH_MARKER_HORIZONTAL_ALIGN.name: "left", Style.FINISH_MARKER_VERTICAL_ALIGN.name: "bottom",
          Style.FINISH_MARKER_WIDHT.name: 5, Style.FINISH_MARKER_EDGE_RATIO.name: 0.1,
          Style.FINISH_MARKER_COLOR.name: "#000000", Style.FINISH_MARKER_EDGE_COLOR.name: "#FFFFFF", Style.FINISH_MARKER_ALPHA.name: 1.0,
          Style.FINISH_MARKER_FONT_PROPERTIES.name: font_awesome_prop
          })
]

GPXS_STYLES: ElementStyles = [
    *folders_styles,  # folder must be first - folder have only some byt file name have all
    *root_files_styles,
    *gpxs_styles_default,
    *gpxs_mandatory_styles
]


# -------------------nodes-------------------
# styles that must be assigned to all node features

place_styles: ElementStyles = [
    ({'place': 'city'}, {
        Style.TEXT_FONT_SIZE.name: 25, Style.ZINDEX.name: 30
    },
        {
        "10-10": {Style.TEXT_FONT_SIZE.name: 15}
    }),
    ({'place': 'town'}, {
        Style.TEXT_FONT_SIZE.name: 10, Style.ZINDEX.name: 29
    },
        {
        "10-10": {Style.TEXT_FONT_SIZE.name: 5, Style.MARKER.name: "o", Style.COLOR.name: "#decda8", Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                  Style.TEXT1_POSITIONS.name: [TextPositions.TOP.name, TextPositions.BOTTOM.name, TextPositions.RIGHT.name], Style.EDGE_WIDTH_RATIO.name: 0.1, Style.WIDTH.name: 2.8,
                  Style.EDGE_COLOR.name: "#a59b7a"}
    }),

    ({'place': 'village'}, {
        Style.TEXT_FONT_SIZE.name: 10, Style.ZINDEX.name: 28
    },
        {
        "10-10": {Style.TEXT_FONT_SIZE.name: 5},
        "11-14": {Style.TEXT_FONT_SIZE.name: 8, Style.MARKER.name: "o", Style.COLOR.name: "#decda8", Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                  Style.TEXT1_POSITIONS.name: [TextPositions.TOP.name, TextPositions.BOTTOM.name, TextPositions.RIGHT.name], Style.EDGE_WIDTH_RATIO.name: 0.2,
                  Style.WIDTH.name: 5, Style.EDGE_COLOR.name: "#a59b7a", Style.MARKER_ABOVE_OTHERS.name: MarkerAbove.NONE}
    }),
]


# text color or MARKER color turn of by string "None" instead of None
natural_styles_nodes: ElementStyles = [
    ({'natural': 'peak'}, {
        Style.MARKER.name: "^",
        Style.MARKER_HORIZONTAL_ALIGN.name: "center", Style.MARKER_VERTICAL_ALIGN.name: None,
        # Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT2.name,
        Style.COLOR.name: "#7f3016",
        Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT2.name,
        Style.TEXT_FONT_SIZE.name: 3, Style.WIDTH.name: 3.6,  Style.TEXT1_POSITIONS.name: [TextPositions.TOP.name],
        Style.TEXT2_POSITIONS.name: [TextPositions.BOTTOM.name], Style.EDGE_WIDTH_RATIO.name: 0,

    })  # rozlišení - dict vs dict s 2 dict uvnitř
]


nodes_styles_default: ElementStyles = [
    # natural must be before place - some peaks are also places
    ({'natural': ''}, {

    }),
    ({'place': ['city', 'town', 'village']}, {
       Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2, Style.MIN_PLOT_REQ.name: MinPlot.TEXT1.name,
        Style.TEXT1_POSITIONS.name: [
            TextPositions.TOP.name, TextPositions.BOTTOM.name, TextPositions.RIGHT.name]
    }),
]

nodes_mandatory_styles: ElementStyles = [
    ([], {
        Style.MIN_LOAD_REQ.name: MinLoad.NONE.name,
        Style.COLOR.name: '#000000', Style.ZINDEX.name: 1, Style.ALPHA.name: 1, Style.EDGE_ALPHA.name: 1,
        Style.TEXT_COLOR.name: '#000000', Style.TEXT_FONT_SIZE.name: 5, Style.TEXT_FONTFAMILY.name: 'DejaVu Sans',
        Style.TEXT_STYLE.name: 'normal', Style.EDGE_COLOR.name: '#FFFFFF', Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2,
        Style.TEXT_WEIGHT.name: 'normal', Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF', Style.TEXT_WRAP_LEN.name: 15
    })
]

NODES_STYLES: ElementStyles = [
    *natural_styles_nodes,
    *place_styles,
    *nodes_styles_default,
    *nodes_mandatory_styles
]


# -------------------ways-------------------
# styles that must be assigned to all way features


# add highway bridge and tunnel styles
# highway_styles_tunnels: FeaturesCategoryStyle = {
#     'motorway': {Style.COLOR.name: '#8cd25f', Style.ZINDEX.name: 7, Style.WIDTH.name: 32, Style.EDGE_COLOR.name: "#5E9346"..},
# }


highway_styles: ElementStyles = [
    ({'highway': '', 'bridge': ''}, {Style.EDGE_COLOR.name: None}),
    ({'highway': 'motorway'}, {Style.COLOR.name: '#8cd25f', Style.ZINDEX.name: 7,
     Style.WIDTH.name: 32, Style.EDGE_COLOR.name: "#5E9346"}),
    ({'highway': 'trunk'}, {Style.COLOR.name: '#FDC364', Style.ZINDEX.name: 6,
     Style.WIDTH.name: 26, Style.EDGE_COLOR.name: "#E19532"}),
    ({'highway': 'primary'}, {Style.COLOR.name: '#FDC364', Style.ZINDEX.name: 5,
     Style.WIDTH.name: 22, Style.EDGE_COLOR.name: "#E19532"}),
    ({'highway': 'secondary'}, {Style.COLOR.name: '#F7ED60',
     Style.ZINDEX.name: 4, Style.WIDTH.name: 20, Style.EDGE_COLOR.name: "#c1b42a"}),
    ({'highway': 'tertiary'}, {Style.COLOR.name: '#FFFFFF',
     Style.ZINDEX.name: 3, Style.WIDTH.name: 16}),
    ({'highway': 'unclassified'}, {Style.COLOR.name: '#FFFFFF', Style.WIDTH.name: 10}),
    ({'highway': 'road'}, {Style.COLOR.name: '#FFFFFF'}),
    ({'highway': 'footway'}, {Style.COLOR.name: '#FFFFFF',
     Style.BRIDGE_COLOR.name: "#FFFFFF"}),
    ({'highway': 'steps'}, {Style.COLOR.name: '#8f8364', Style.LINESTYLE.name: "--",
     Style.EDGE_COLOR.name: None, Style.PLOT_ON_BRIDGE.name: None}),
    ({'highway': 'path'}, {Style.COLOR.name: '#8f8364', Style.LINESTYLE.name: "--",
     Style.EDGE_COLOR.name: None, Style.BRIDGE_COLOR.name: "#FFFFFF", Style.PLOT_ON_BRIDGE.name: None}),
    ({'highway': 'track'}, {Style.COLOR.name: '#8f8364', Style.LINESTYLE.name: "--",
     Style.EDGE_COLOR.name: None, Style.BRIDGE_COLOR.name: "#FFFFFF", Style.PLOT_ON_BRIDGE.name: None}),
    ({'highway': 'residential'}, {Style.COLOR.name: '#FFFFFF'})
]


railway_styles: ElementStyles = [
    ({'railway': 'rail'}, {
        Style.COLOR.name: '#FFFFFF', Style.WIDTH.name: 10,
        Style.BRIDGE_EDGE_COLOR.name: '#5D5D5D', Style.BRIDGE_COLOR.name: "#FFFFFF",
        Style.EDGE_COLOR.name: '#5D5D5D', Style.BRIDGE_WIDTH_RATIO.name: 1 + 1.7,
        Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.4, 
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.4,
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value
    }),


    ({'railway': 'tram'}, {
        Style.COLOR.name: '#404040',  Style.WIDTH.name: 4
    })
]


ways_styles_default: ElementStyles = [
    ({'highway': ''}, {
        Style.COLOR.name: '#FFFFFF', Style.BRIDGE_EDGE_COLOR.name: "#7D7D7D",
        Style.EDGE_COLOR.name: "#B0A78D", Style.WIDTH.name: 10
    }),
    ({'railway': ''}, {
        Style.COLOR.name: '#FFFFFF', Style.ZINDEX.name: 100
    }),
    ({'waterway': ''}, {
        Style.COLOR.name: '#8FB8DB', Style.WIDTH.name: 8,
        Style.ZINDEX.name: 0, Style.EDGE_COLOR.name: None
    }),
]

# default values for all ways
ways_mandatory_styles: ElementStyles = [
    ([], {
        Style.ALPHA.name: 1.0, Style.EDGE_ALPHA.name: 1,
        Style.LINESTYLE.name: '-', Style.EDGE_WIDTH_RATIO.name: 1 + 0.3, 
        Style.EDGE_LINESTYLE.name: '-'
    }),
    ({'bridge': ''}, {
        Style.BRIDGE_EDGE_LINESTYLE.name: '-', Style.BRIDGE_LINESTYLE.name: '-',
        Style.BRIDGE_WIDTH_RATIO.name: 1, Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.3,
        Style.BRIDGE_COLOR.name: "#FFFFFF", Style.BRIDGE_EDGE_COLOR.name: "#7D7D7D", Style.PLOT_ON_BRIDGE.name: True
    }),
]

WAYS_STYLES: ElementStyles = [
    *highway_styles,
    *railway_styles,
    *ways_styles_default,
    *ways_mandatory_styles
]

# -------------------areas-------------------
area_mandatory_styles: ElementStyles = [
    ([], {
        Style.COLOR.name: '#EDEDE0', Style.ALPHA.name: 1.0
    })
]

landuse_styles: ElementStyles = [
    ({'landuse': 'farmland'}, {Style.COLOR.name: '#EDEDE0'}),
    ({'landuse': 'forest'}, {Style.COLOR.name: '#9FC98D',}),
    ({'landuse': 'meadow'}, {Style.COLOR.name: '#B7DEA6'}),
    ({'landuse': 'grass'}, {Style.COLOR.name: '#B7DEA6'}),
    ({'landuse': 'residential'}, {Style.COLOR.name: '#E2D4AF'}),
    ({'landuse': 'industrial'}, {Style.COLOR.name: '#DFDBD1'}),
    ({'landuse': 'basin'}, {Style.COLOR.name: '#8FB8DB'}),
    ({'landuse': 'salt_pond'}, {Style.COLOR.name: '#8FB8DB'}),
]

leisure_styles: ElementStyles = [
    ({'leisure': 'swimming_pool'}, {Style.COLOR.name: '#8FB8DB'}),
    ({'leisure': 'golf_course'}, {Style.COLOR.name: '#DCE9B9'}),
    ({'leisure': 'playground'}, {Style.COLOR.name: '#DCE9B9'}),
    ({'leisure': 'pitch'}, {Style.COLOR.name: '#DCE9B9'}),
    ({'leisure': 'sports_centre'}, {Style.COLOR.name: '#9FC98D'}),
    ({'leisure': 'nature_reserve'}, {Style.COLOR.name: None, Style.EDGE_COLOR.name: '#97BB72',
                                     Style.WIDTH.name: 80, 
                                     Style.EDGE_ALPHA.name: 0.85, Style.EDGE_LINESTYLE.name: '-'})
]

building_styles: ElementStyles = [
    ({'building': 'house'}, {Style.COLOR.name: 'grey'}),
    ({'building': 'residential'}, {Style.COLOR.name: 'grey'}),
]

natural_styles: ElementStyles = [
    ({'natural': 'wood'}, {Style.COLOR.name: '#9FC98D'}),
    ({'natural': 'water'}, {Style.COLOR.name: '#8FB8DB'}),
    ({'natural': 'scrub'}, {Style.COLOR.name: '#B7DEA6'}),
    ({'natural': 'heath'}, {Style.COLOR.name: '#B7DEA6'}),
]

area_styles_default: ElementStyles = [
    ({'building': ''}, {Style.COLOR.name: '#B7DEA6'}),
    ({'landuse': ''},  {Style.COLOR.name: '#EDEDE0'}),
    ({'water': ''}, {Style.COLOR.name: '#8FB8DB'}),
    ({'leisure': ''}, {Style.COLOR.name: '#EDEDE0'}),
    ({'natural': ''}, {Style.COLOR.name: '#B7DEA6'}),
    ({'boundary': ''}, {
        Style.COLOR.name: None, Style.EDGE_COLOR.name: '#97BB72',
        Style.WIDTH.name: 80, Style.EDGE_LINESTYLE.name: '-',
        Style.EDGE_ALPHA.name: 0.85
    })
]

AREAS_STYLES: ElementStyles = [
    *natural_styles,
    *building_styles,
    *landuse_styles,
    *leisure_styles,
    *area_styles_default,
    *area_mandatory_styles
]

STYLES: dict[str, ElementStyles] = {
    'nodes': NODES_STYLES,
    'ways': WAYS_STYLES,
    'areas': AREAS_STYLES
}
