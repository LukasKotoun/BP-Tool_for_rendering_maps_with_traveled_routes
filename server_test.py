from fastapi import FastAPI, File, UploadFile, Form, Depends
from pydantic import BaseModel
import json

from typing import Dict, Any, List, Optional
import geopandas as gpd
from fastapi.middleware.cors import CORSMiddleware

# Pydantic model for 'WANTED_CATEGORIES' and 'UNWANTED_CATEGORIES'
class CategoryFilter(BaseModel):
    nodes: List[str]
    nodes_from_area: List[str]
    ways: List[str]
    areas: List[str]

# Main configuration model
class MapGeneratorConfig(BaseModel):
    styles_size_changes: Optional[Any] = None  # Optional field
    gpxs_styles: Optional[Any] = None  # Optional list of styles

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/generate_map/")
async def generate_map(
    gpxs: Optional[List[UploadFile]] = File(None),
    config: str = Form(...),
    # Handle multiple GPX files in the request
):
    try:
        config_obj = MapGeneratorConfig(**json.loads(config))
    except Exception as e:
        return {"message": "Invalid configuration data"}
    print(config_obj.dict())
    print(config_obj.gpxs_styles)
    # Assuming you want to handle the uploaded GPX files (gpxs)
    # if gpxs:
    #     gpx_files = [file.filename for file in gpxs]  # Get filenames of the uploaded files
    #     # You can process these files as needed
    # else:
    #     gpx_files = []
    print("asd")
    return {"message": "Map generated successfully"}
