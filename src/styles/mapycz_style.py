from common.custom_types import *
from common.map_enums import *
from config import font_awesome_prop, material_desigh_prop

#! edge linestyle is suported only dashed or not dashed on not solid lines,
#! ploting is turned of by setting color to None text color or icon color turn of by string "None" instead of None
# ------------styles--------------
OCEAN_WATER = '#8fb6db'

GENERAL_DEFAULT_STYLES: FeatureStyles = {StyleKey.COLOR: '#EDEDE0',  StyleKey.ZINDEX: 0,
                                         StyleKey.WIDTH: 1, StyleKey.LINESTYLE: '-',
                                         StyleKey.ALPHA: 1, StyleKey.EDGE_COLOR: None, StyleKey.EDGE_LINESTYLE: '-'}



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
        StyleKey.START_ICON: "o",
        StyleKey.START_ICON_WIDHT: 2, StyleKey.START_ICON_EDGE_RATIO: 0.1,
        StyleKey.START_ICON_COLOR: "#18ac0d", StyleKey.START_ICON_EDGE_COLOR: "#FFFFFF", StyleKey.START_ICON_ALPHA: 1.0,
        StyleKey.FINISH_ICON: "\uf11e",
        StyleKey.FINISH_ICON_WIDHT: 5, StyleKey.FINISH_ICON_EDGE_RATIO: 0.1,
        StyleKey.FINISH_ICON_COLOR: "#000000", StyleKey.FINISH_ICON_EDGE_COLOR: "#FFFFFF", StyleKey.FINISH_ICON_ALPHA: 1.0,
        StyleKey.FINISH_MARKER_FONT_PROPERTIES: font_awesome_prop
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
print(font_awesome_prop)
natural_styles_nodes: ElementStyles = [
    ({'natural': 'peak'}, {
        # StyleKey.ICON: "^", 
        StyleKey.ICON: "\uf11e", 
        StyleKey.MARKER_HORIZONTAL_ALIGN: "center", StyleKey.MARKER_VERTICAL_ALIGN: "center",
        StyleKey.MARKER_FONT_PROPERTIES: material_desigh_prop,
        StyleKey.COLOR: "#7f3016", StyleKey.MIN_REQ_POINT: MinParts.MARKER_TEXT2, #StyleKey.MIN_REQ_POINT: MinParts.MARKER_TEXT2,
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
        StyleKey.TEXT_WEIGHT: 'normal', StyleKey.TEXT_OUTLINE_COLOR: '#FFFFFF', StyleKey.TEXT_WRAP_LEN: 15
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
