
// paper and areas
export const paperSizes = [
  { label: "Vlastní", value: JSON.stringify({ width: null, height: null }) },
  { label: "A0 (1189 × 841 mm)", value: JSON.stringify({ height: 841, width: 1189 }) },
  { label: "A1 (841 × 594 mm)", value: JSON.stringify({ height: 594, width: 841 }) },
  { label: "A2 (594 × 420 mm)", value: JSON.stringify({ height: 420, width: 594 }) },
  { label: "A3 (420 × 297 mm)", value: JSON.stringify({ height: 297, width: 420 }) },
  { label: "A4 (297 × 210 mm)", value: JSON.stringify({ height: 210, width: 297 }) },
  { label: "A5 (297 × 148 mm)", value: JSON.stringify({ height: 148, width: 210 }) },
  { label: "A6 (148 × 105 mm)", value: JSON.stringify({ height: 105, width: 148 }) }
]

export const mapGeneratingStatusMappingCZ = {
  "failed": "Zpracování selhalo",
  "in_queue": "Čekání ve frontě na zpracování",
  "starting": "Začíná se zpracovávat 1/12",
  "extracting": "Extrahování dat ze souboru 2/12",
  "loading": "Načítání mapových dat ze souboru 3/12",
  "filtering": "Filtrování mapových dat 4/12",
  "styling": "Nastavování vzhledu mapových dat 5/12",
  "preparing_for_plotting": "Příprava mapových dat k vykreslení 6/12",
  "areas_plotting": "Vykreslování oblastí 7/12",
  "ways_plotting": "Vykreslování cest 8/12",
  "nodes_plotting": "Vykreslování bodů 9/12",
  "gpxs_plotting": "Vykreslování GPX tras 10/12",
  "file_saving": "Ukládání mapy do souboru 11/12",
  "completed": "Generování mapy bylo úspěšně dokončeno, probíhá její stahování! 12/12",
  "sending_data": "Odesílání dat na server"
}

export const mapDataNamesMappingCZ = {
  "cz": "Česká republika",
  "sk": "Slovensko",
  "at": "Rakousko",
  "de": "Německo",
  "pl": "Polsko",
  "hu": "Maďarsko",
  "si": "Slovinsko",
  "hr": "Chorvatsko",
  "it": "Itálie",
  "fr": "Francie",
  "be": "Belgie",
  "nl": "Nizozemsko",
  "lu": "Lucembursko",
  "gb": "Velká Británie",
  "ie": "Irsko",
  "dk": "Dánsko",
  "se": "Švédsko",
  "no": "Norsko",
  "fi": "Finsko",
  "ee": "Estonsko",
}



export const numberOfZoomLevels = 10
// gpx styles
export const gpxDefaultStyles: GpxStyleAttributes = {
  color: '#FF0000',
  width: 0.5,
  alpha: 0.7,
  zindex: 0,
  linestyle: '-',
  line_capstyle: 'round',
  edge_color: null,
  edge_alpha: 0,
  edge_width_ratio: 0,
  edge_linestyle: '-',
  edge_capstyle: 'round',
  gpx_above_text: false,
  start_marker: null,
  start_marker_width: 1.7,
  start_marker_edge_ratio: 0.1,
  start_marker_color: '#18ac0d',
  start_marker_alpha: 1,
  start_marker_edge_color: '#FFFFFF',
  finish_marker: null,
  finish_marker_width: 1.7,
  finish_marker_edge_ratio: 0.1,
  finish_marker_color: '#000000',
  finish_marker_alpha: 1,
  finish_marker_edge_color: '#FFFFFF',
  marker_layer_position: 'under_text'
};

export const LINESTYLES = ['-', '--', '- -'];
export const CAPSTYLES = ['round', 'butt', 'projecting'];
export const CAPSTYLE_MAPPING_CZ = {
  round: 'Zaoblený ()',
  butt: 'Useknutý []',
  projecting: 'Prodloužený useknutý [ ]'
};

export const MARKER_LAYER_POSITIONS = ['above_text', 'under_text'];
export const MARKER_LAYER_POSITION_MAPPING_CZ = {
  above_text: 'Nad textem',
  under_text: 'Pod textem'
};
export const MARKERS = ['finish', 'start', null];
export const MARKER_MAPPING_CZ= {
  null: 'Žádná',
  start: 'Start - kolečko/bod', 
  finish: 'Cíl - vlajka'
};

// map elements
export const wantedNodesUpdatesZooms = {
  1: { place: ["city"] },
  2: { place: ["town"], natural: ["peak"] },
  3: {},
  4: { place: ["village"] },
  5: {},
  6: {},
  7: {},
  8: { man_made: ["tower"], historic: ["castle"], place: ["suburb", "neighbourhood", "locality"] },
  9: {},
  10: {}
}

export const wantedWaysUpdatesZooms = {
  1: { highway: ["motorway", "trunk", "primary", "motorway_link", "trunk_link", "primary_link"], route: ["ferry"], waterway: ["river"] },
  2: {},
  3: { highway: ["secondary"] },
  4: { highway: ["secondary_link", "tertiary", "raceway"], railway: ["rail", "light_rail", "monorail"], aeroway: ["runway", "taxiway"] },
  5: { railway: ["funicular"], waterway: ["canal", "stream"], aerialway: ["cable_car", "gondola", "chair_lift", "mixed_lift"] },
  6: {
    highway: ["tertiary_link", "residential", "unclassified", "pedestrian", "track", "path"],
    aerialway: ["t-bar", "j-bar", "platter", "rope_tow", "magic_carpet", "zip_line", "goods"]
  },
  7: { highway: ["service", "cycleway", "footway", "steps"], railway: ["subway"], waterway: ["drain", "ditch"] },
  8: { railway: ["miniature"] },
  9: { railway: ["tram"], barrier: ["city_wall", "wall", "cable_barrier"] },
  10: {}
}

export const wantedAreasUpdatesZooms = {
  1: {landuse: true, leisure: ["park", "garden"],
        natural: true,
        
  },
  2: {boundary:["national_park"]},
  3: {amenity: ["grave_yard", "school", "university", "college", "kindergarten", "bus_station", "hospital", "clinic", "place_of_worship"],
    leisure: ["swimming_pool"],
  },
  4: {building: true},
  5: {},
  6: {aeroway: ["aerodrome"]},
  7: {amenity: ["motorcycle_parking", "parking"],
    highway: ["pedestrian", "footway"],
    leisure: ["pitch", "playground", "sports_centre", "golf_course"],
  },
  8: {},
  9: {},
  10: {}
}

export const nodesKeysNamesMappingCZ = {
  place: "Místa",
  natural: "Přírodní objekty",
  man_made: "Umělé objekt",
  historic: "Historické objekt"
}

export const nodesNamesMappingCZ = {
  place: {
    city: "Velkoměsto",
    town: "Město",
    village: "Vesnice",
    suburb: "Městská část",
    neighbourhood: "Menší městská část",
    locality: "Lokalita"
  },
  natural: {
    peak: "Vrchol (Hora, Kopec)"
  },
  man_made: {
    tower: "Rozhledna"
  },
  historic: {
    castle: "Hrad"
  }
}

export const waysKeysNamesMappingCZ = {
  highway: "Silnice",
  railway: "Železnice",
  aeroway: "Letiště",
  aerialway: "Lanovky",
  barrier: "Bariéry",
  waterway: "Vodní toky",
  route: "Vodní trasy"
}
export const waysNamesMappingCZ = {
  highway: {
    motorway: "Dálnice",
    trunk: "Silnice pro motorová vozidla",
    primary: "Silnice I. třídy",
    secondary: "Silnice II. třídy",
    tertiary: "Silnice III. třídy",
    motorway_link: "Nájezd na dálnici",
    trunk_link: "Nájezd na silnici pro motorová vozidla",
    primary_link: "Nájezd na silnici I. třídy",
    secondary_link: "Nájezd na silnici II. třídy",
    tertiary_link: "Nájezd na silnici III. třídy",
    residential: "Místní komunikace",
    unclassified: "Neklasifikovaná silnice",
    service: "Přístupová cesta",
    pedestrian: "Pěší zóna",
    cycleway: "Cyklostezka",
    raceway: "Závodní dráha",
    steps: "Schodiště",
    footway: "Chodník",
    track: "Pěšina (track)",
    path: "Pěšinka (path)"
  },
  railway: {
    rail: "Železnice",
    light_rail: "Lehká železnice",
    monorail: "Jednokolejná železnice",
    miniature: "Modelová železnice",
    subway: "Metro",
    funicular: "Lanovka"
  },
  aeroway: {
    runway: "Vzletová dráha",
    taxiway: "Přijezdová dráha"
  },
  aerialway: {
    cable_car: "Velká kabinová",
    gondola: "Kabinková",
    chair_lift: "Sedačková",
    mixed_lift: "Smíšená",
    "t-bar": "Kotva",
    "j-bar": "J-kotva",
    platter: "Puma",
    rope_tow: "Lanovka",
    magic_carpet: "Kobercová lanovka",
    zip_line: "zipline",
    goods: "Nákladní lanovka"
  },
  barrier: {
    city_wall: "Městská hradba",
    wall: "Zeď",
    cable_barrier: "Ochranná bariéra"
  },
  waterway: {
    river: "Řeka",
    canal: "Kanál",
    stream: "Potok",
    drain: "Odtok",
    ditch: "Příkop"
  },
  route: {
    ferry: "Trajekt"
  }
}

export const areasKeysNamesMappingCZ = {
  landuse: "Užitné pozemky",
  leisure: "Volný čas",
  natural: "Příroda",
  amenity: "Vybavení",
  boundary: "Ohraničení oblastí",
  building: "Budovy",
  aeroway: "Letiště",
  highway: "Silnice (parkoviště a pěší zóny)"
}

export const areasNamesMappingCZ = {
  landuse: {
    farmland: "Zemědělská půda",
    forest: "Les",
    residential: "Obytná zóna",
    commercial: "Komerční zóna",
    retail: "Obchodní zóna",
    industrial: "Průmyslová zóna",
    allotments: "Zahrádkářská kolonie",
    meadow: "Louka",
    grass: "Tráva",
    landfill: "Skládka",
    cemetery: "Hřbitov",
    vineyard: "Vinice",
    orchard: "Sad",
    garages: "Garáže",
    quarry: "Lom",
    recreation_ground: "Rekreační plocha"
  },
  leisure: {
    park: "Park",
    garden: "Zahrada",
    pitch: "Hřiště",
    golf_course: "Golfové hřiště",
    playground: "Dětské hřiště",
    sports_centre: "Sportovní centrum",
    swimming_pool: "Bazén"
  },
  natural: {
    wood: "Neudržovaný les",
    water: "Vodní plocha",
    scrub: "Keře",
    heath: "Vřesoviště",
    grassland: "Travnatá plocha",
    beach: "Pláž",
    sand: "Písek"
  },
  amenity: {
    motorcycle_parking: "Parkoviště pro motocykly",
    parking: "Parkoviště",
    grave_yard: "Hřbitov",
    school: "Škola",
    university: "Univerzita",
    college: "Kolej",
    kindergarten: "Mateřská škola",
    bus_station: "Autobusové nádraží",
    hospital: "Nemocnice",
    clinic: "Klinika",
    place_of_worship: "Místo k modlitbě"
  },
  boundary: {
    national_park: "Národní park"
  },
  building: "Budovy",
  aeroway: {
    aerodrome: "Letiště"
  },
  highway: {
    pedestrian: "Pěší zóna",
    footway: "Chodník"
  }
}

export const nodesMapElements = {
  place: {
    city: { plot: false, width_scale: 1, text_scale: 1 },
    town: { plot: false, width_scale: 1, text_scale: 1 },
    village: { plot: false, width_scale: 1, text_scale: 1 },
    suburb: { plot: false, text_scale: 1 },
    neighbourhood: { plot: false, text_scale: 1 },
    locality: { plot: false, text_scale: 1 }
  },
  natural: {
    peak: { plot: false, width_scale: 1, text_scale: 1 }
  },
  man_made: {
    tower: { plot: false, width_scale: 1, text_scale: 1 }
  },
  historic: {
    castle: { plot: false, width_scale: 1, text_scale: 1 }
  }
}

export const waysMapElements = {
  highway: {
    motorway: { plot: false, width_scale: 1 },
    trunk: { plot: false, width_scale: 1 },
    primary: { plot: false, width_scale: 1 },
    secondary: { plot: false, width_scale: 1 },
    tertiary: { plot: false, width_scale: 1 },
    motorway_link: { plot: false, width_scale: 1 },
    trunk_link: { plot: false, width_scale: 1 },
    primary_link: { plot: false, width_scale: 1 },
    secondary_link: { plot: false, width_scale: 1 },
    tertiary_link: { plot: false, width_scale: 1 },
    residential: { plot: false, width_scale: 1 },
    unclassified: { plot: false, width_scale: 1 },
    service: { plot: false, width_scale: 1 },
    pedestrian: { plot: false, width_scale: 1 },
    cycleway: { plot: false, width_scale: 1 },
    raceway: { plot: false, width_scale: 1 },
    steps: { plot: false, width_scale: 1 },
    footway: { plot: false, width_scale: 1 },
    track: { plot: false, width_scale: 1 },
    path: { plot: false, width_scale: 1 }
  },
  railway: {
    rail: { plot: false, width_scale: 1 },
    light_rail: { plot: false, width_scale: 1 },
    monorail: { plot: false, width_scale: 1 },
    miniature: { plot: false, width_scale: 1 },
    subway: { plot: false, width_scale: 1 },
    funicular: { plot: false, width_scale: 1 }
  },
  aeroway: {
    runway: { plot: false, width_scale: 1 },
    taxiway: { plot: false, width_scale: 1 }
  },
  aerialway: {
    cable_car: { plot: false, width_scale: 1 },
    gondola: { plot: false, width_scale: 1 },
    chair_lift: { plot: false, width_scale: 1 },
    mixed_lift: { plot: false, width_scale: 1 },
    "t-bar": { plot: false, width_scale: 1 },
    "j-bar": { plot: false, width_scale: 1 },
    platter: { plot: false, width_scale: 1 },
    rope_tow: { plot: false, width_scale: 1 },
    magic_carpet: { plot: false, width_scale: 1 },
    zip_line: { plot: false, width_scale: 1 },
    goods: { plot: false, width_scale: 1 }
  },
  barrier: {
    city_wall: { plot: false, width_scale: 1 },
    wall: { plot: false, width_scale: 1 },
    cable_barrier: { plot: false, width_scale: 1 }
  },
  waterway: {
    river: { plot: false, width_scale: 1 },
    canal: { plot: false, width_scale: 1 },
    stream: { plot: false, width_scale: 1 },
    drain: { plot: false, width_scale: 1 },
    ditch: { plot: false, width_scale: 1 }
  },
  route: {
    ferry: { plot: false, width_scale: 1 }
  }
}

export const areasMapElements = {
  landuse: {
    farmland: { plot: false },
    forest: { plot: false },
    residential: { plot: false },
    commercial: { plot: false },
    retail: { plot: false },
    industrial: { plot: false },
    allotments: { plot: false },
    meadow: { plot: false },
    grass: { plot: false },
    landfill: { plot: false },
    cemetery: { plot: false, width_scale: 1 },
    vineyard: { plot: false },
    orchard: { plot: false },
    garages: { plot: false },
    quarry: { plot: false },
    recreation_ground: { plot: false }
  },
  leisure: {
    park: { plot: false },
    garden: { plot: false },
    pitch: { plot: false, width_scale: 1 },
    golf_course: { plot: false, width_scale: 1 },
    playground: { plot: false, width_scale: 1 },
    sports_centre: { plot: false, width_scale: 1 },
    swimming_pool: { plot: false }
  },
  natural: {
    wood: { plot: false },
    water: { plot: false },
    scrub: { plot: false },
    heath: { plot: false },
    grassland: { plot: false },
    beach: { plot: false },
    sand: { plot: false }
  },
  amenity: {
    motorcycle_parking: { plot: false },
    parking: { plot: false },
    grave_yard: { plot: false, width_scale: 1 },
    school: { plot: false },
    university: { plot: false },
    college: { plot: false },
    kindergarten: { plot: false },
    bus_station: { plot: false },
    hospital: { plot: false },
    clinic: { plot: false },
    place_of_worship: { plot: false }
  },
  boundary: {
    national_park: { plot: false, width_scale: 1 }
  },
  building: { plot: false, width_scale: 1 },
  aeroway: {
    aerodrome: { plot: false }
  },
  highway: {
    pedestrian: { plot: false, width_scale: 1 },
    footway: { plot: false, width_scale: 1 }
  }
}
