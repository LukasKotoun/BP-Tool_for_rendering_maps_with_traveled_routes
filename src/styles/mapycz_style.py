from common.custom_types import ElementStyles, FeatureStyles
from common.map_enums import Style, TextPositions, MinPlot, MarkerAbove, MarkersCodes, LineCupStyles, MapThemeVariable
from config import font_awesome_prop, material_design_prop

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
                                      [{'highway': ['pedestrian', 'footway'], 'area': 'yes'}, {'amenity': ['parking', 'motorcycle_parking']}])
WAYS_WITHOUT_CROSSING = {"1-4": {'highway': 'motorway'}, "5-10": None}

WATER_COLOR = '#8FB6DB'
LAND_COLOR = '#EDEDE0'


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
# marker minimum: 
# text minimum:
# styles that must be assigned to all node features
# zorder: castle: 28, towers: 29 peaks: 30, place names 40-50, 

NODES_STYLES_SCALE = []
place_styles: ElementStyles = [
    ({'place': 'city'}, {
        Style.TEXT_FONT_SIZE.name: 25, Style.ZINDEX.name: 50
    },
        {
        "10-10": {Style.TEXT_FONT_SIZE.name: 15}
    }),
    ({'place': 'town'}, {
        Style.TEXT_FONT_SIZE.name: 10, Style.ZINDEX.name: 49
    },
        {
        "10-10": {Style.TEXT_FONT_SIZE.name: 5, Style.MARKER.name: "o", Style.COLOR.name: "#decda8", Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                  Style.TEXT1_POSITIONS.name: [TextPositions.TOP, TextPositions.BOTTOM, TextPositions.RIGHT], Style.EDGE_WIDTH_RATIO.name: 0.1, Style.WIDTH.name: 2.8,
                  Style.EDGE_COLOR.name: "#a59b7a"}
    }),

    ({'place': 'village'}, {
        Style.TEXT_FONT_SIZE.name: 10, Style.ZINDEX.name: 48
    },
        {
        "10-10": {Style.TEXT_FONT_SIZE.name: 5},
        "11-14": {Style.TEXT_FONT_SIZE.name: 8, Style.MARKER.name: "o", Style.COLOR.name: "#decda8", Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT1.name,
                  Style.TEXT1_POSITIONS.name: [TextPositions.TOP, TextPositions.BOTTOM, TextPositions.RIGHT], Style.EDGE_WIDTH_RATIO.name: 0.2,
                  Style.WIDTH.name: 5, Style.EDGE_COLOR.name: "#a59b7a", Style.MARKER_ABOVE_OTHERS.name: MarkerAbove.NONE}
    }),
]


# text color or MARKER color turn of by string "None" instead of None
natural_styles_nodes: ElementStyles = [
    ({'natural': 'peak'}, {
        Style.ZINDEX.name: 30, Style.MIN_PLOT_REQ.name: MinPlot.MARKER_TEXT2.name,
        # marker
        Style.MARKER.name: "^", Style.MARKER_HORIZONTAL_ALIGN.name: "center", 
        Style.COLOR.name: "#42281a", Style.EDGE_COLOR.name: "None",
        # text
        Style.TEXT_FONT_SIZE.name: 6, Style.WIDTH.name: 3,  Style.TEXT1_POSITIONS.name: [TextPositions.TOP],
        Style.TEXT2_POSITIONS.name: [TextPositions.BOTTOM], Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2,

    }) 
]
icons_above_styles_nodes: ElementStyles = [
    # todo size
    ({'man_made': 'tower', 'tower:type': ['observation', 'watchtower']}, {
        Style.MIN_PLOT_REQ.name: MinPlot.MARKER.name, 
        # marker
        Style.MARKER.name: MarkersCodes.FA_TOWER_OBSERVATION.value, Style.MARKER_FONT_PROPERTIES.name: font_awesome_prop,
        Style.COLOR.name: "#863417", Style.EDGE_COLOR.name: "#FFFFFF", Style.WIDTH.name: 7, 
        Style.EDGE_WIDTH_RATIO.name: 0.1,
        Style.MARKER_HORIZONTAL_ALIGN.name: "center", Style.MARKER_ABOVE_OTHERS.name: MarkerAbove.NORMAL,
        # text
        Style.TEXT_COLOR.name: "#000000", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF',
        Style.TEXT1_POSITIONS.name: [TextPositions.BOTTOM],
        Style.TEXT_FONT_SIZE.name: 6, Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2,
    }),

    ({'historic': ['castle']}, {
        Style.MIN_PLOT_REQ.name: MinPlot.MARKER.name, 
        # marker
        Style.MARKER.name: MarkersCodes.MU_CASTLE.value, Style.MARKER_FONT_PROPERTIES.name: material_design_prop,
        Style.COLOR.name: "#714f41", Style.EDGE_COLOR.name: "#FFFFFF", Style.WIDTH.name: 7, 
        Style.EDGE_WIDTH_RATIO.name: 0.1,
        Style.MARKER_HORIZONTAL_ALIGN.name: "center", Style.MARKER_ABOVE_OTHERS.name: MarkerAbove.NORMAL,
        # text
        Style.TEXT_COLOR.name: "#000000", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF',
        Style.TEXT1_POSITIONS.name: [TextPositions.BOTTOM],
        Style.TEXT_FONT_SIZE.name: 6, Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2,
    })
]

nodes_styles_default: ElementStyles = [
    ({'natural': ''}, {
        Style.TEXT_COLOR.name: "#000000", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF'
    }),
    
    # natural must be before place - some peaks are also places
    ({'place': ['city', 'town', 'village']}, {
        Style.TEXT_OUTLINE_WIDTH_RATIO.name: 0.2, Style.MIN_PLOT_REQ.name: MinPlot.TEXT1.name,
        Style.TEXT_COLOR.name: "#000000", Style.TEXT_OUTLINE_COLOR.name: '#FFFFFF',
        Style.TEXT1_POSITIONS.name: [
            TextPositions.TOP, TextPositions.BOTTOM, TextPositions.RIGHT]
    }),
]

nodes_mandatory_styles: ElementStyles = [
    ([], {
        Style.ALPHA.name: 1, Style.EDGE_ALPHA.name: 1,
        Style.TEXT_FONTFAMILY.name: 'DejaVu Sans',
        Style.TEXT_STYLE.name: 'normal',
        Style.TEXT_WEIGHT.name: 'normal', Style.TEXT_WRAP_LEN.name: 15
    })
]

NODES_STYLES: ElementStyles = [
    *icons_above_styles_nodes,
    *natural_styles_nodes,
    *place_styles,
    *nodes_styles_default,
    *nodes_mandatory_styles
]
# todo maybe is needed to change dashed linstyles by zoom level - cahnged with width :]
# -------------------ways------------------
# styles that must be assigned to all way features
# scaled styles - relative to polygon (not paper)
WAYS_STYLES_SCALE = [Style.WIDTH.name]
# dashed highways z index 0-waterways, 1-14 - dashedways, 15-20 - barrier, 21-50 normal ways, 60-70 aeroway, 70-80 - aerialway, 90 - 100 (subway - 20) - railways

# bridges overwrite because bridge have separated styles with bridge..
highway_styles_bridges_overwrite: ElementStyles = [
    ({'highway': '', 'bridge': ''}, {Style.EDGE_COLOR.name: None,
                                     })]

# add highway bridge and tunnel styles
highway_styles_tunnels: ElementStyles = [
    ({'highway': ['motorway', 'motorway_link'],
     'tunnel': ''}, {Style.COLOR.name: "#a0e078"}),
    ({'highway': ['trunk', 'primary', 'trunk_link', 'primary_link'], 'tunnel': ''},
     {Style.COLOR.name: "#fee0b0"}),
    ({'highway': ['secondary', 'secondary_link'],
     'tunnel': ''}, {Style.COLOR.name: "#e4e791"}),
    # default color and all edge styles
    ({'highway': '', 'tunnel': ''}, {Style.EDGE_LINESTYLE.name: (2, (3, 1)),
                                     Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
                                     Style.COLOR.name: "#f6f9f5", Style.EDGE_COLOR.name: "#B0A78D", Style.LINESTYLE.name: "-"})]

highway_styles_main: ElementStyles = [
    # todo size
    ({'highway': 'motorway'}, {Style.COLOR.name: '#8cd25f', Style.ZINDEX.name: 50,
     Style.WIDTH.name: 32, Style.EDGE_COLOR.name: "#5E9346"}),
    # todo size
    ({'highway': 'motorway_link'}, {Style.COLOR.name: '#8cd25f', Style.ZINDEX.name: 49,
     Style.WIDTH.name: 32, Style.EDGE_COLOR.name: "#5E9346"}),

    # todo size
    ({'highway': 'trunk'}, {Style.COLOR.name: '#FDC364', Style.ZINDEX.name: 48,
     Style.WIDTH.name: 26, Style.EDGE_COLOR.name: "#E19532"}),
    # todo size
    ({'highway': 'trunk_link'}, {Style.COLOR.name: '#FDC364', Style.ZINDEX.name: 47,
     Style.WIDTH.name: 26, Style.EDGE_COLOR.name: "#E19532"}),

    # todo size
    ({'highway': 'primary'}, {Style.COLOR.name: '#FDC364', Style.ZINDEX.name: 46,
     Style.WIDTH.name: 22, Style.EDGE_COLOR.name: "#E19532"}),
    # todo size
    ({'highway': 'primary_link'}, {Style.COLOR.name: '#FDC364', Style.ZINDEX.name: 45,
                                   Style.WIDTH.name: 22, Style.EDGE_COLOR.name: "#E19532"}),

    # todo size
    ({'highway': 'secondary'}, {Style.COLOR.name: '#F7ED60', Style.ZINDEX.name: 45,
                                Style.WIDTH.name: 20, Style.EDGE_COLOR.name: "#c1b42a"}),
    # todo size
    ({'highway': 'secondary_link'}, {Style.COLOR.name: '#F7ED60', Style.ZINDEX.name: 44,
     Style.WIDTH.name: 20, Style.EDGE_COLOR.name: "#c1b42a"}),

    # todo size
    ({'highway': 'tertiary'}, {Style.ZINDEX.name: 43, Style.COLOR.name: '#FFFFFF',
                               Style.EDGE_COLOR.name: "#B0A78D", Style.WIDTH.name: 16}),
    # todo size
    ({'highway': 'tertiary_link'}, {Style.COLOR.name: '#FFFFFF', Style.ZINDEX.name: 42,
     Style.WIDTH.name: 16, Style.EDGE_COLOR.name: "#B0A78D"}),



    # o trochu menší než tertiary
    # todo size
    ({'highway': 'residential'}, {Style.ZINDEX.name: 40, Style.COLOR.name: '#FFFFFF',
                                  Style.EDGE_COLOR.name: "#B0A78D", }),
    # todo size
    ({'highway': 'unclassified'}, {Style.ZINDEX.name: 39, Style.COLOR.name: '#FFFFFF',
                                   Style.EDGE_COLOR.name: "#B0A78D"}),
]

highway_styles_surface_special_and_paths: ElementStyles = [

    # to non dashed
    # todo size bigger than normal track - solid bigger than dashed - big
    ({'highway': ['track', 'cycleway'],
      'surface': ['asphalt'],
      'tracktype': ('~grade3', '~grade4', '~grade5'),
      },
     {Style.ZINDEX.name: 35, Style.COLOR.name: "#e6e3dd", Style.EDGE_COLOR.name: "#857e5f",
      Style.LINESTYLE.name: "-", Style.EDGE_LINESTYLE.name: "-"}),
    
 # todo size - white slightly bigger than normal track, 
 # other(non white) same size as normal track - so set size only for zoom where is white
    ([{'highway': ['path', 'track'],
      'surface': ['asphalt', 'concrete', 'paving_stones', 'sett', 'cobblestone',
                  'compacted', 'fine_gravel'],
       'tracktype': ('~grade3', '~grade4', '~grade5')},
      {'highway': ['path', 'track'],
        'tracktype': ['grade1', 'grade2']}],
     {Style.ZINDEX.name: 33, Style.COLOR.name:  '#FFFFFF', Style.EDGE_COLOR.name: "#B0A78D",
      Style.LINESTYLE.name: "-", Style.EDGE_LINESTYLE.name: "-"},
     {"1-8":  # on smaller zoom, change to line without edge
        {Style.COLOR.name: '#8f8364', Style.EDGE_COLOR.name: None,
         Style.PLOT_ON_BRIDGE.name: True}}),


    #todo size dashed footway size - same as dashed path or track
    ({'highway': ['footway'],
      'surface': ['unpaved', 'gravel', 'pebblestone', 'rock', 'dirt',
                  'ground', 'grass', 'sand', 'mud', 'woodchips']},
     {Style.COLOR.name: "#8f8364", Style.EDGE_COLOR.name: None,
      Style.LINESTYLE.name: (3, (5, 4)), Style.ZINDEX.name: 10,
      Style.PLOT_ON_BRIDGE.name: False},
     {"1-7": {Style.PLOT_ON_BRIDGE.name: True}}
     ),
]

highway_styles_special_and_paths: ElementStyles = [

    # o trochu menší než residental
    # todo size
    ({'highway': 'service'}, {Style.ZINDEX.name: 38, Style.COLOR.name: '#FFFFFF',
                              Style.EDGE_COLOR.name: "#B0A78D"}),
    # todo size
    ({'highway': 'pedestrian'}, {Style.ZINDEX.name: 37, Style.COLOR.name: '#FFFFFF',
                                 Style.EDGE_COLOR.name: "#B0A78D"}),
    # todo size
    ({'highway': 'cycleway'}, {Style.ZINDEX.name: 36, Style.COLOR.name: '#FFFFFF',
                               Style.EDGE_COLOR.name: "#B0A78D"}),

    # todo size
    ({'highway': 'raceway'}, {Style.COLOR.name: '#FFFFFF', Style.EDGE_COLOR.name: "#B0A78D",
                              Style.ZINDEX.name: 35},
     {"7-10": {Style.COLOR.name: '#e6e3dd',
               Style.EDGE_COLOR.name: "#857e5f"}
      }),


    # todo size - same as footway - test
    ({'highway': 'steps'}, {Style.COLOR.name: '#FFFFFF', Style.EDGE_COLOR.name: "#B0A78D",
                            Style.LINESTYLE.name: (2, (3, 0.2)),
                            Style.LINE_CAPSTYLE: LineCupStyles.BUTT.value,
                            Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
                            Style.PLOT_ON_BRIDGE.name: False, Style.ZINDEX.name: 31},
     {"1-8": {Style.COLOR.name: '#8f8364', Style.EDGE_COLOR.name: None, Style.LINESTYLE.name: "-",
              Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.PLOT_ON_BRIDGE.name: True}}),
    
     ({'highway': 'footway'}, {Style.ZINDEX.name: 30, Style.BRIDGE_COLOR.name: "#FFFFFF"},
     {"1-8": {Style.COLOR.name: '#8f8364', Style.EDGE_COLOR.name: None, Style.LINESTYLE.name: "-",
              Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.PLOT_ON_BRIDGE.name: True}
      }),
    # steps and footway - same size
    ({'highway': ['footway', 'steps']}, {},
     {"1-8": {}
      }),


    # todo size track and path same
    ({'highway': 'track'}, {Style.ZINDEX.name: 14, Style.COLOR.name: '#8f8364', Style.LINESTYLE.name: (7, (10, 4)),
     Style.EDGE_COLOR.name: None, Style.BRIDGE_COLOR.name: "#FFFFFF", Style.PLOT_ON_BRIDGE.name: None},
     {"1-7": {Style.PLOT_ON_BRIDGE.name: True}}),
    ({'highway': 'path'}, {Style.ZINDEX.name: 13, Style.COLOR.name: '#8f8364', Style.LINESTYLE.name: (3, (5, 4)),
     Style.EDGE_COLOR.name: None, Style.BRIDGE_COLOR.name: "#FFFFFF", Style.PLOT_ON_BRIDGE.name: None},
     {"1-7": {Style.PLOT_ON_BRIDGE.name: True}}),
    # dashed path and track size
     ({'highway': ['path', 'track']}, {Style.WIDTH.name: 20},
    ),
    
]


# railways
# bridges overwrite because bridge have separated styles with bridge..
railway_styles_bridges_overwrite: ElementStyles = [
    ({'railway': ['funicular', 'subway'], 'bridge': ''}, {
        Style.BRIDGE_EDGE_COLOR.name: None, Style.BRIDGE_COLOR.name: None
    }),
    ({'railway': ['subway'], 'bridge': ''}, {
        Style.COLOR.name: '#FFFFFF',
        Style.EDGE_COLOR.name: '#818181',
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.4,
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
    })
]

railway_styles_tunnels: ElementStyles = [
    ({'railway': ['rail', 'light_rail', "monorail", 'miniature'], 'tunnel': ''}, {
        Style.COLOR.name: None, Style.EDGE_LINESTYLE.name: (3, (7, 4)),
        Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value
    }),

    ({'railway': 'tram', 'tunnel': ''}, {
        Style.EDGE_LINESTYLE.name: (3, (7, 4)),
        Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value
    }),
    
    # todo size - same as normal tram
    ({'railway': 'funicular', 'tunnel': ''}, {
        Style.COLOR.name: None,
        Style.EDGE_WIDTH_RATIO.name: 0.4,
        Style.EDGE_LINESTYLE.name: (2, (3, 2)),
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value,
    })
]

railway_styles_service: ElementStyles = [
    # # todo size - smaller than normal rail
    ({'railway': ['rail', 'light_rail', "monorail", "subway"],
      'service': ['crossover', 'siding', 'spur', 'yard']}, {
        Style.WIDTH.name: 15,  # smaller width, in osm alpha and width
    })]

railway_styles: ElementStyles = [
    # for osm light_rail, monorail is just line, subway is line but with different color
    ({'railway': ['rail', 'light_rail', "monorail", 'miniature']}, {
        Style.COLOR.name: '#FFFFFF', Style.EDGE_COLOR.name: '#5D5D5D',
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.4,
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
        Style.ZINDEX.name: 100
    }),

    ({'railway': 'subway'}, {
        Style.COLOR.name: '#818181', Style.LINESTYLE.name: (3, (7, 4)),
        Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
        Style.EDGE_COLOR.name: None, Style.WIDTH.name: 10,
        Style.ZINDEX.name: 20
    }),
    # # todo size - test subway size
    ({'railway': ['rail', 'light_rail', "monorail", 'miniature', "subway"]}, {
        Style.WIDTH.name: 15,
    }),


    # # todo size
    ({'railway': 'funicular'}, {
        Style.ZINDEX.name: 99,
        Style.COLOR.name: '#FFFFFF', Style.WIDTH.name: 10,
        Style.EDGE_COLOR.name: '#5D5D5D',
        Style.EDGE_LINESTYLE.name: (0, (5, 5)),
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.8,
        Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.name: 0.4,
        Style.LINE_CAPSTYLE.name: LineCupStyles.ROUND.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.ROUND.value
    }),

    # # todo size
    ({'railway': 'tram'}, {
        Style.COLOR.name: '#404040', Style.WIDTH.name: 4
    }),

]

waterway_styles_tunnels: ElementStyles = [
    ({'waterway': '', 'tunnel': '', 'intermittent': "yes"}, {
     Style.LINESTYLE.name: (0, (1, 1)), Style.EDGE_COLOR: None}),
    ({'waterway': '', 'tunnel': ''}, {Style.LINESTYLE.name: "--", Style.EDGE_COLOR: None})]

waterway_styles: ElementStyles = [
    ({'waterway': '', 'intermittent': "yes"}, {Style.LINESTYLE.name: (0, (1, 1)),
                                               Style.EDGE_COLOR: None}),
    # todo size
    ({'waterway': ['river']}, {Style.WIDTH.name: 15}),
    # todo size - smaller than river bigger than default
    ({'waterway': ['canal']}, {Style.WIDTH.name: 15}),
]

aerialway_styles: ElementStyles = [
    # todo size
    ({'aerialway': ['cable_car', 'gondola', 'mixed_lift']}, {
        Style.COLOR.name: '#FFFFFF', Style.WIDTH.name: 50,
        Style.EDGE_COLOR.name: '#5D5D5D', Style.EDGE_LINESTYLE.name: (0, (5, 5)),
        Style.LINESTYLE.name: (0, (5, 5)), Style.EDGE_WIDTH_RATIO.name: 1 + 0.8,
        Style.EDGE_WIDTH_DASHED_CONNECT_RATIO.name: 0.4, Style.ZINDEX.name: 80
    }),
    # todo size
    ({'aerialway': ['chair_lift']}, {
        Style.COLOR.name: '#5D5D5D', Style.WIDTH.name: 50,
        Style.EDGE_COLOR.name: '#5D5D5D', Style.LINESTYLE.name: (0, (3, 5)),
        Style.EDGE_LINESTYLE.name: '-', Style.EDGE_WIDTH_RATIO.name: 0.4,
        Style.ZINDEX.name: 79
    }),
]

aeroway_styles: ElementStyles = [
    # todo size
    ({'aeroway': 'runway'}, {
        Style.WIDTH.name: 50,
        Style.ZINDEX.name: 70,
        Style.LINE_CAPSTYLE.name: LineCupStyles.BUTT.value, Style.EDGE_CAPSTYLE.name: LineCupStyles.BUTT.value,
    }),
    # todo size
    ({'aeroway': 'taxiway'}, {
        Style.WIDTH.name: 20, 
        Style.ZINDEX.name: 69,
    }),
]

# barrier_styles: ElementStyles = [
#     ({'barrier': 'hedge'}, {
#         Style.COLOR.name: '#B7DEA6',
#         Style.ZINDEX.name: 14
#     })
# ]


ways_styles_default: ElementStyles = [
    ({'highway': ''}, {
        Style.WIDTH.name: 20,  # todo remove width
        Style.EDGE_WIDTH_RATIO.name: 1 + 0.3,
        Style.COLOR.name: '#FFFFFF',
        Style.EDGE_COLOR.name: "#B0A78D"
    }),
    ({'highway': '', 'bridge': ''}, {
        Style.BRIDGE_EDGE_LINESTYLE.name: '-', Style.BRIDGE_LINESTYLE.name: '-',
        Style.BRIDGE_WIDTH_RATIO.name: 1, Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.3,
        Style.BRIDGE_EDGE_COLOR.name: "#7D7D7D", Style.BRIDGE_COLOR.name: "#FFFFFF",
        Style.PLOT_ON_BRIDGE.name: True
    }),

    ({'railway': ''}, {
        Style.ZINDEX.name: 90
    }),
    ({'railway': '', 'bridge': ''}, {
        Style.BRIDGE_EDGE_COLOR.name: '#5D5D5D', Style.BRIDGE_COLOR.name: "#FFFFFF",
        Style.BRIDGE_WIDTH_RATIO.name: 1 + 1.7, Style.BRIDGE_EDGE_WIDTH_RATIO.name: 1 + 0.4,
        Style.PLOT_ON_BRIDGE.name: True
    }),

    ({'aeroway': ''}, {
        Style.COLOR.name: "#FFFFFF", Style.EDGE_COLOR.name: "#B0A78D",
        Style.EDGE_WIDTH_RATIO.name: 1 + 0.3,
    }),

     # todo size
    ({'aerialway': ''}, {
        Style.COLOR.name: '#5D5D5D', Style.WIDTH.name: 50,
        Style.EDGE_COLOR.name: '#5D5D5D', Style.EDGE_LINESTYLE.name: '-',
        Style.LINESTYLE.name: (0, (0.1, 3)), Style.EDGE_WIDTH_RATIO.name: 0.4,
        Style.ZINDEX.name: 70
    }),

     # todo size
    ({'barrier': ''}, {
        Style.WIDTH.name: 8, Style.ZINDEX.name: 15,
        Style.COLOR.name: "#7e7f7c"
    }),

     # todo size - #
    ({'waterway': ''}, {
        Style.COLOR.name: '#8FB8DB', Style.WIDTH.name: 8,
        Style.ZINDEX.name: 0, Style.EDGE_COLOR.name: None
    }),
]

# default values for all ways
ways_mandatory_styles: ElementStyles = [
    ([], {
        Style.ALPHA.name: 1.0, Style.EDGE_ALPHA.name: 1,
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

    *waterway_styles,
    *waterway_styles_tunnels,

    *ways_styles_default,
    *ways_mandatory_styles
]


# -------------------areas-------------------
AREAS_STYLES_SCALE = [Style.WIDTH.name]
area_mandatory_styles_area: ElementStyles = [
    ([], {
        Style.COLOR.name: '#EDEDE0', Style.ALPHA.name: 1.0
    })
]

landuse_styles_area: ElementStyles = [
    #todo zeptat se 
    # ({'landuse': 'landfill'}, {Style.COLOR.name: '#dedcd1'}),
    # ({'landuse': ['forest', 'recreation_ground']},
    #  {Style.COLOR.name: '#9FC98D'}),
    # ({'landuse': 'vineyard'}, {Style.COLOR.name: '#d2e2a9'}),
    # ({'landuse': 'orchard'}, {Style.COLOR.name: '#ddeab4'}),
    # # ({'landuse': 'quarry'}, {Style.COLOR.name: '#DFDBD1'}),

    # ({'landuse': ['basin', 'salt_pond']}, {Style.COLOR.name: '#8FB8DB'}),

    # ({'landuse': ['meadow', 'grass', 'cemetery']},
    #  {Style.COLOR.name: '#B7DEA6'}),

    # ({'landuse': 'military'}, {
    #     Style.ZINDEX.name: 1, Style.EDGE_ALPHA.name: 0.7,
    #     Style.EDGE_COLOR.name: "#a4a4a4", Style.WIDTH.name: 70,
    #     Style.EDGE_LINESTYLE.name: "-"},
    #  {"3-6": {Style.COLOR.name: '#a4a4a4', Style.ALPHA.name: 0.2}}),

    # ({'landuse': ['allotments', 'retail', 'residential', 'garages', 'commercial']}, {},
    #  {"8-10": {Style.COLOR.name: '#ece1cb'}}),

    # ({'landuse': ['industrial', 'farmyard', 'brownfield', 'quarry']},
    #  {Style.COLOR.name: '#DFDBD1'},
    #  {"7-8": {Style.COLOR.name: '#DFDBD1'}}
    #  ),

    ({'landuse': 'farmland'}, {Style.COLOR.name: '#EDEDE0'}),
    ({'landuse': 'landfill'}, {Style.COLOR.name: '#dedcd1'}),

    ({'landuse': 'vineyard'}, {Style.COLOR.name: '#d2e2a9'}),
    ({'landuse': 'orchard'}, {Style.COLOR.name: '#ddeab4'}),

    ({'landuse': ['basin', 'salt_pond']}, {Style.COLOR.name: '#8FB8DB'}),
    ({'landuse': ['forest', 'recreation_ground', 'meadow', 'grass', 'cemetery']},
     {Style.COLOR.name: '#c5e1a3'}, {
        "8-10": {Style.COLOR.name: '#cbe8aa'}}),
    # todo test or remove - dont need on big map----
    ({'landuse': 'military'}, {
        Style.EDGE_ALPHA.name: 0.7,
        Style.EDGE_COLOR.name: "#a4a4a4", Style.WIDTH.name: 70,
        Style.EDGE_LINESTYLE.name: "-"},
     {"3-6": {Style.COLOR.name: '#a4a4a4', Style.ALPHA.name: 0.2, Style.ZINDEX.name: 1}}),

    ({'landuse': ['allotments', 'retail', 'residential', 'garages', 'commercial']}, {},
     {"8-10": {Style.COLOR.name: '#ece1cb'},
      "7": {Style.COLOR.name: '#e2d3b0'},
      "1-6": {Style.COLOR.name: '#dbcca8'}}),
    
    # todo test - jizni cast bratislavy
    ({'landuse': ['industrial', 'farmyard', 'brownfield', 'quarry']},
     {},
     {"8-10": {Style.COLOR.name: '#cac7c1'},
      "7": {Style.COLOR.name: '#d4d2ca'},
      "5-6": {Style.COLOR.name: '#cccac3'},
      "1-4": {Style.COLOR.name: '#dbcca8'}}),
]

leisure_styles_area: ElementStyles = [
    ({'leisure': ['garden', 'park']}, {Style.COLOR.name: '#B7DEA6'}),
    ({'leisure': ['golf_course', 'playground', 'pitch']},
     {Style.COLOR.name: '#DCE9B9'}),
    ({'leisure': 'sports_centre'}, {Style.COLOR.name: '#9FC98D'}),
    ({'leisure': 'swimming_pool'}, {Style.COLOR.name: '#8FB8DB'}),
    ({'leisure': 'nature_reserve'}, {Style.COLOR.name: None, Style.EDGE_COLOR.name: '#97BB72',
                                     Style.WIDTH.name: 80,
                                     Style.EDGE_ALPHA.name: 0.85, Style.EDGE_LINESTYLE.name: '-'})
]

# dynamic change color based on zoom level
building_styles_area: ElementStyles = [
    ({'building': ['church', 'synagogue', 'cathedral', 'temple', 'monastery']}, {}, {
        "8-10": {Style.COLOR.name: '#908b84'}}),

    ([{'building': ['university', 'hospital', 'public', 'clinic', 'supermarket']}, {'building': '', 'historic': ''}], {  # same as historic..
        "8-10": {Style.COLOR.name: '#bab09a'}}),

    ({'building': ['industrial', 'warehouse']}, {}, {
        "8-10": {Style.COLOR.name: '#cac7c1'},
        "7": {Style.COLOR.name: '#d4d2ca'},
        "5-6": {Style.COLOR.name: '#cccac3'}}),
]



natural_styles_area: ElementStyles = [
    ({'natural': 'wood'}, {Style.COLOR.name: '#9FC98D'}),
    ({'natural': 'beach'}, {Style.COLOR.name: '#9FC98D'}),
    ({'natural': ['water', 'bay']}, {Style.COLOR.name: '#8FB8DB'}),
    ({'natural': ['heath', 'scrub', 'grassland']},
     {Style.COLOR.name: '#B7DEA6'}),
]

amenity_styles_area: ElementStyles = [
    ({'amenity': ['parking', 'motorcycle_parking']}, {Style.COLOR.name: '#FFFFFF'}),
    ({'amenity': 'grave_yard'}, {Style.COLOR.name: '#B7DEA6'}),
    # other tags default
]

area_styles_default: ElementStyles = [
    # under buildings
    # default styles based on zoom
    # amenity as parking and aditional tags to buildings - maybe load only parking and leave aditional tag for building but not in loading


    ({'landuse': ''},  {Style.COLOR.name: '#EDEDE0'}),
    ({'leisure': ''}, {Style.COLOR.name: '#EDEDE0'}),
    ({'natural': ''}, {Style.COLOR.name: '#EDEDE0'}),

    ({'aeroway': ''}, {Style.COLOR.name: '#cccac3'}),
    ({'building': ''}, {Style.COLOR.name: '#dacbae'},
     {"7": {Style.COLOR.name: '#e2d3b0'},
      "1-6": {Style.COLOR.name: '#dbcca8'}}),
    # mostly aditional tags
    ({'amenity': ''}, {Style.COLOR.name: '#ece1cb'},
     {"7": {Style.COLOR.name: '#e2d3b0'},
      "1-6": {Style.COLOR.name: '#dbcca8'}}),

    ({'highway': ['pedestrian', 'footway']}, {Style.COLOR.name: '#FFFFFF'}),
    # ({'boundary': ''}, {
    #     Style.COLOR.name: None, Style.EDGE_COLOR.name: '#97BB72',
    #     Style.WIDTH.name: 80, Style.EDGE_LINESTYLE.name: '-',
    #     Style.EDGE_ALPHA.name: 0.85
    # })
]

AREAS_STYLES: ElementStyles = [
    *natural_styles_area,
    *landuse_styles_area,
    *leisure_styles_area,
    *building_styles_area,
    *amenity_styles_area,
    *area_styles_default,
    *area_mandatory_styles_area
]


# check what to do with gpx styles
MAPYCZSTYLE: dict[str, dict[str, any]] = {
    "variables":{
        MapThemeVariable.GPXS_STYLES_SCALE: GPXS_STYLES_SCALE,
        MapThemeVariable.NODES_STYLES_SCALE: NODES_STYLES_SCALE,
        MapThemeVariable.WAYS_STYLES_SCALE: WAYS_STYLES_SCALE,
        MapThemeVariable.AREAS_STYLES_SCALE: AREAS_STYLES_SCALE,
        MapThemeVariable.WATER_COLOR: WATER_COLOR,
        MapThemeVariable.LAND_COLOR: LAND_COLOR,
        MapThemeVariable.AREAS_OVER_WAYS_FILTER: AREAS_OVER_WAYS_FILTER,
        MapThemeVariable.WAYS_WITHOUT_CROSSING_FILTER: WAYS_WITHOUT_CROSSING,
    },
    "styles":{
        'gpxs': GPXS_STYLES,
        'nodes': NODES_STYLES,
        'ways': WAYS_STYLES,
        'areas': AREAS_STYLES
    }
}
