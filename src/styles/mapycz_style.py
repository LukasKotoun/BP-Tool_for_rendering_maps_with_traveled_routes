from common.custom_types import *
from common.map_enums import *

#! edge linestyle is suported only dashed or not dashed on not solid lines,
#! ploting is turned of by setting color to None text color or icon color turn of by string "None" instead of None
# ------------styles--------------
OCEAN_WATER = '#8fb6db'

GENERAL_DEFAULT_STYLES: FeatureStyles = {StyleKey.COLOR: '#EDEDE0',  StyleKey.ZINDEX: 0,
                                         StyleKey.WIDTH: 1, StyleKey.LINESTYLE: '-',
                                         StyleKey.ALPHA: 1, StyleKey.EDGE_COLOR: None, StyleKey.EDGE_LINESTYLE: '-'}

# !!! icon from svg
from svgpath2mpl import parse_path
def center_path(p):
    p.vertices -= p.vertices.mean(axis=0)
    return p

asd = center_path(parse_path("""
  M 5,25 A 20,20 0 1,1 45,25 A 20,20 0 1,1 5,25 Z
  M 15,7 L 7,15 L 15,15 Z
  M 25,5 L 35,5 L 35,15 L 25,15 Z
  M 35,15 L 45,15 L 45,25 L 35,25 Z
  M 15,6 L 6,15 L 15,15 Z
  M 15,15 L 25,15 L 25,25 L 15,25 Z
  M 25,25 L 35,25 L 35,35 L 25,35 Z
  M 5,25 L 15,25 L 15,35 L 5,35 Z
  M 45,35 L 35,45 L 35,35 Z
  M 15,35 L 25,35 L 25,45 L 15,45 Z
  M 25,25 A 21,21 0 1,1 25,25 Z
"""))

test = {
    "marker": center_path(parse_path("M 100,10 L 40,198 L 190,78 L 10,78 L 160,198 z"))
}

# -------------------gpx-------------------
root_files_styles: ElementStyles = [
    ({'fileName': 'Grilovačka.gpx'}, {StyleKey.COLOR: "Red"}),
]

folders_styles: ElementStyles = [
    ({'folder': 'pěšky'}, {StyleKey.COLOR: "Blue"}),
    ({'folder': 'Kolo testování'}, {StyleKey.WIDTH: 1, StyleKey.ALPHA: 0.7}),
    ({'folder': 'Kolo'}, {StyleKey.COLOR: "Purple"}),
]

gpxs_styles_default: ElementStyles = [
    ({'fileName': ''}, {StyleKey.COLOR: 'Red', StyleKey.WIDTH: 1,
     StyleKey.ALPHA: 0.7,  StyleKey.ZINDEX: 0}),
    ({'folder': ''}, {StyleKey.COLOR: 'Orange', StyleKey.WIDTH: 1,
     StyleKey.ALPHA: 0.7,  StyleKey.ZINDEX: 0}),
]

gpxs_mandatory_styles: ElementStyles = [
    ([], {StyleKey.COLOR: 'Green', StyleKey.WIDTH: 1, StyleKey.ALPHA: 1.0, StyleKey.LINESTYLE: "-",
        # StyleKey.START_ICON:  center_path(parse_path("M 100,10 L 40,198 L 190,78 L 10,78 L 160,198 z")),
        StyleKey.START_ICON: parse_path("M384 192c0 87.4-117 243-168.3 307.2c-12.3 15.3-35.1 15.3-47.4 0C117 435 0 279.4 0 192C0 86 86 0 192 0S384 86 384 192z"),
        # StyleKey.START_ICON: asd,
        StyleKey.FINISH_ICON: "o",
        StyleKey.START_ICON_WIDHT: 2, StyleKey.START_ICON_EDGE_RATIO: 0.1,
        StyleKey.START_ICON_COLOR: "#18ac0d", StyleKey.START_ICON_EDGE_COLOR: "#FFFFFF", StyleKey.START_ICON_ALPHA: 1.0,
        StyleKey.FINISH_ICON_WIDHT: 2, StyleKey.FINISH_ICON_EDGE_RATIO: 0.1,
        StyleKey.FINISH_ICON_COLOR: "white", StyleKey.FINISH_ICON_EDGE_COLOR: "#FFFFFF", StyleKey.FINISH_ICON_ALPHA: 1.0,
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
        StyleKey.TEXT_FONT_SIZE: 25, StyleKey.ZINDEX: 30
    },
        {
        "10-10": {StyleKey.TEXT_FONT_SIZE: 15}
    }),
    ({'place': 'town'}, {
        StyleKey.TEXT_FONT_SIZE: 15, StyleKey.ZINDEX: 29
    },
        {
        "10-10": {StyleKey.TEXT_FONT_SIZE: 6, StyleKey.ICON: "o", StyleKey.COLOR: "#decda8", StyleKey.MIN_REQ_POINT: MinParts.MARKER_TEXT1,
        StyleKey.TEXT1_POSITIONS: [TextPositions.TOP, TextPositions.BOTTOM, TextPositions.RIGHT], StyleKey.EDGE_WIDTH_RATIO:0.1, StyleKey.WIDTH: 2.8, 
        StyleKey.EDGE_COLOR: "#a59b7a"}
    }),

    ({'place': 'village'}, {
        StyleKey.TEXT_FONT_SIZE: 10, StyleKey.ZINDEX: 28
    },
        {
        "10-10": {StyleKey.TEXT_FONT_SIZE: 5},
        "11-14": {StyleKey.TEXT_FONT_SIZE: 10, StyleKey.ICON: "o", StyleKey.COLOR: "#decda8", StyleKey.MIN_REQ_POINT: MinParts.MARKER_TEXT1,
        StyleKey.TEXT1_POSITIONS: [TextPositions.TOP, TextPositions.BOTTOM, TextPositions.RIGHT], StyleKey.EDGE_WIDTH_RATIO:0.2, StyleKey.WIDTH: 4.5, 
        StyleKey.EDGE_COLOR: "#a59b7a"}
    }),
]


# text color or icon color turn of by string "None" instead of None
natural_styles_nodes: ElementStyles = [
    ({'natural': 'peak'}, {
        StyleKey.ICON: "^", StyleKey.COLOR: "#7f3016", StyleKey.MIN_REQ_POINT: MinParts.MARKER_TEXT2, #StyleKey.MIN_REQ_POINT: MinParts.MARKER_TEXT2,
        StyleKey.TEXT_FONT_SIZE: 3, StyleKey.WIDTH: 3.6,  StyleKey.TEXT1_POSITIONS: [TextPositions.TOP], 
        StyleKey.TEXT2_POSITIONS: [TextPositions.BOTTOM], StyleKey.EDGE_WIDTH_RATIO: 0, StyleKey.MARKER_CHECK_OVERLAP: True
    })  # rozlišení - dict vs dict s 2 dict uvnitř
]


nodes_styles_default: ElementStyles = [
    # natural must be before place - some peaks are also places
    ({'natural': ''}, {
       
    }),
    ({'place': ['city', 'town', 'village']}, {
        StyleKey.TEXT_FONT_SIZE: 5, StyleKey.TEXT_OUTLINE_WIDTH_RATIO: 0.2, StyleKey.MIN_REQ_POINT: MinParts.TEXT1,
        StyleKey.TEXT1_POSITIONS: [TextPositions.TOP, TextPositions.BOTTOM, TextPositions.RIGHT]
    }),
]

nodes_mandatory_styles: ElementStyles = [
    ([], {
        StyleKey.COLOR: '#000000', StyleKey.ZINDEX: 1, StyleKey.ALPHA: 1, StyleKey.EDGE_ALPHA: 1,
        StyleKey.TEXT_COLOR: '#000000', StyleKey.TEXT_FONT_SIZE: 5, StyleKey.TEXT_FONTFAMILY: 'DejaVu Sans',
        StyleKey.TEXT_STYLE: 'normal', StyleKey.EDGE_COLOR: '#FFFFFF', StyleKey.TEXT_OUTLINE_WIDTH_RATIO: 0.2,
        StyleKey.TEXT_WEIGHT: 'normal', StyleKey.TEXT_OUTLINE_COLOR: '#FFFFFF', StyleKey.TEXT1_WRAP_LEN: 15, StyleKey.TEXT2_WRAP_LEN: 15
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
ways_mandatory_styles: ElementStyles = [
    ([], {
        StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0, StyleKey.WIDTH: 1, StyleKey.LINESTYLE: '-',
        StyleKey.EDGE_WIDTH_RATIO: 1 + 0.3, StyleKey.EDGE_ALPHA: 1,
        StyleKey.EDGE_COLOR: None, StyleKey.EDGE_LINESTYLE: '-', StyleKey.WIDTH_SCALE: 1, StyleKey.FE_WIDTH_SCALE: 1,
    }),
    ({'bridge': ''}, {
        StyleKey.BRIDGE_WIDTH_RATIO: 1, StyleKey.BRIDGE_EDGE_WIDTH_RATIO: 1 + 0.3,
        # on bridge (will be bridge edge)
        StyleKey.BRIDGE_COLOR: "#FFFFFF", StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D", StyleKey.PLOT_ON_BRIDGE: True
    }),
]

# add highway bridge and tunnel styles
# highway_styles_tunnels: FeaturesCategoryStyle = {
#     'motorway': {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7, StyleKey.WIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"..},
# }


highway_styles: ElementStyles = [
    ({'highway': '', 'bridge': ''}, {StyleKey.EDGE_COLOR: None}),
    ({'highway': 'motorway'}, {StyleKey.COLOR: '#8cd25f', StyleKey.ZINDEX: 7,
     StyleKey.WIDTH: 32, StyleKey.EDGE_COLOR: "#5E9346"}),
    ({'highway': 'trunk'}, {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 6,
     StyleKey.WIDTH: 26, StyleKey.EDGE_COLOR: "#E19532"}),
    ({'highway': 'primary'}, {StyleKey.COLOR: '#FDC364', StyleKey.ZINDEX: 5,
     StyleKey.WIDTH: 22, StyleKey.EDGE_COLOR: "#E19532"}),
    ({'highway': 'secondary'}, {StyleKey.COLOR: '#F7ED60',
     StyleKey.ZINDEX: 4, StyleKey.WIDTH: 20, StyleKey.EDGE_COLOR: "#c1b42a"}),
    ({'highway': 'tertiary'}, {StyleKey.COLOR: '#FFFFFF',
     StyleKey.ZINDEX: 3, StyleKey.WIDTH: 16}),
    ({'highway': 'unclassified'}, {StyleKey.COLOR: '#FFFFFF'}),
    ({'highway': 'road'}, {StyleKey.COLOR: '#FFFFFF'}),
    ({'highway': 'footway'}, {StyleKey.COLOR: '#FFFFFF',
     StyleKey.BRIDGE_COLOR: "#FFFFFF"}),
    ({'highway': 'steps'}, {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--",
     StyleKey.EDGE_COLOR: None, StyleKey.PLOT_ON_BRIDGE: None}),
    ({'highway': 'path'}, {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--",
     StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF", StyleKey.PLOT_ON_BRIDGE: None}),
    ({'highway': 'track'}, {StyleKey.COLOR: '#8f8364', StyleKey.LINESTYLE: "--",
     StyleKey.EDGE_COLOR: None, StyleKey.BRIDGE_COLOR: "#FFFFFF", StyleKey.PLOT_ON_BRIDGE: None}),
    ({'highway': 'residential'}, {StyleKey.COLOR: '#FFFFFF'})
]


railway_styles: ElementStyles = [
    ({'railway': 'rail'}, {
        StyleKey.COLOR: '#FFFFFF', StyleKey.WIDTH: 10,
        StyleKey.BRIDGE_EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_COLOR: "#FFFFFF",
        StyleKey.EDGE_COLOR: '#5D5D5D', StyleKey.BRIDGE_WIDTH_RATIO: 1 + 1.7,
        # todo control after function to calculating width
        StyleKey.BRIDGE_EDGE_WIDTH_RATIO: 1 + 0.4,
        StyleKey.LINESTYLE: (0, (5, 5)), StyleKey.EDGE_WIDTH_RATIO: 1 + 0.4
    }),

    ({'railway': 'tram'}, {
        StyleKey.COLOR: '#404040',  StyleKey.WIDTH: 4
    })
]


ways_styles_default: ElementStyles = [
    ({'highway': ''}, {
        StyleKey.COLOR: '#FFFFFF', StyleKey.BRIDGE_EDGE_COLOR: "#7D7D7D",
        StyleKey.ZINDEX: 1, StyleKey.WIDTH: 8, StyleKey.EDGE_COLOR: "#B0A78D"
    }),
    ({'railway': ''}, {
        StyleKey.COLOR: '#FFFFFF', StyleKey.ZINDEX: 100, StyleKey.WIDTH: 8
    }),
    ({'waterway': ''}, {
        StyleKey.COLOR: '#8FB8DB', StyleKey.WIDTH: 8,
        StyleKey.ZINDEX: 0, StyleKey.EDGE_COLOR: None
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
        StyleKey.COLOR: '#EDEDE0', StyleKey.ALPHA: 1.0
    })
]

landuse_styles: ElementStyles = [
    ({'landuse': 'farmland'}, {StyleKey.COLOR: '#EDEDE0'}),
    ({'landuse': 'forest'}, {StyleKey.COLOR: '#9FC98D'}),
    ({'landuse': 'meadow'}, {StyleKey.COLOR: '#B7DEA6'}),
    ({'landuse': 'grass'}, {StyleKey.COLOR: '#B7DEA6', StyleKey.ZINDEX: 1}),
    ({'landuse': 'residential'}, {StyleKey.COLOR: '#E2D4AF'}),
    ({'landuse': 'industrial'}, {StyleKey.COLOR: '#DFDBD1'}),
    ({'landuse': 'basin'}, {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
    ({'landuse': 'salt_pond'}, {StyleKey.COLOR: '#8FB8DB', StyleKey.ZINDEX: 1}),
]

leisure_styles: ElementStyles = [
    ({'leisure': 'swimming_pool'}, {StyleKey.COLOR: '#8FB8DB'}),
    ({'leisure': 'golf_course'}, {StyleKey.COLOR: '#DCE9B9'}),
    ({'leisure': 'playground'}, {StyleKey.COLOR: '#DCE9B9'}),
    ({'leisure': 'pitch'}, {StyleKey.COLOR: '#DCE9B9'}),
    ({'leisure': 'sports_centre'}, {StyleKey.COLOR: '#9FC98D'}),
    ({'leisure': 'nature_reserve'}, {StyleKey.COLOR: None, StyleKey.EDGE_COLOR: '#97BB72',
                                     StyleKey.WIDTH: 80, StyleKey.ZINDEX: 1,
                                     StyleKey.EDGE_ALPHA: 0.85, StyleKey.EDGE_LINESTYLE: '-'})
]

building_styles: ElementStyles = [
    ({'building': 'house'}, {StyleKey.COLOR: 'grey'}),
    ({'building': 'residential'}, {StyleKey.COLOR: 'grey'}),
]

natural_styles: ElementStyles = [
    ({'natural': 'wood'}, {StyleKey.COLOR: '#9FC98D'}),
    ({'natural': 'water'}, {StyleKey.COLOR: '#8FB8DB'}),
    ({'natural': 'scrub'}, {StyleKey.COLOR: '#B7DEA6'}),
    ({'natural': 'heath'}, {StyleKey.COLOR: '#B7DEA6'}),
]

area_styles_default: ElementStyles = [
    ({'building': ''}, {StyleKey.COLOR: '#B7DEA6'}),
    ({'landuse': ''},  {StyleKey.COLOR: '#EDEDE0'}),
    ({'water': ''}, {StyleKey.COLOR: '#8FB8DB'}),
    ({'leisure': ''}, {StyleKey.COLOR: '#EDEDE0'}),
    ({'natural': ''}, {StyleKey.COLOR: '#B7DEA6'}),
    ({'boundary': ''}, {
        StyleKey.COLOR: None, StyleKey.EDGE_COLOR: '#97BB72',
        StyleKey.WIDTH: 80, StyleKey.EDGE_LINESTYLE: '-',
        StyleKey.ZINDEX: 1, StyleKey.EDGE_ALPHA: 0.85
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
