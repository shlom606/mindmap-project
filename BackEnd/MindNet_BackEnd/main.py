# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import AIEngine
from graph_build import GraphBuilder
from database import MindMapStorage
from typing import Literal
#The FastAPI settings to initilise the web server
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize our specialized modules
engine = AIEngine() #this from ai_engine.py
builder = GraphBuilder() #this is from graph_build.py
db = MindMapStorage()

class ConceptRequest(BaseModel):
    concepts: list[str]
class MapGenerationRequest(BaseModel):
    username: str
    map_title: str
    concepts: list[str]
    model_type: Literal['sbert', 'minibert'] = 'minibert' # Add this field

# Pre-load both engines for fast switching
engines = {
    'sbert': AIEngine(mode='sbert'),
    'minibert': AIEngine(mode='minibert')
}
@app.post("/generate")
async def generate(data: ConceptRequest):
    # Step 1: AI processes the text
    embeddings, groups = engine.get_predictions(data.concepts)
    
    # Step 2: Architect builds the graph
    graph_data = builder.create_structure(data.concepts, embeddings, groups)
    
    return graph_data
@app.post("/generate-and-save")
async def generate_and_save(request: MapGenerationRequest):
    try:
        # Select the engine based on user choice
        selected_engine = engines.get(request.model_type, engines['minibert'])
        
        # 1. AI Processing using the selected engine
        embeddings, groups = selected_engine.get_predictions(request.concepts)
        
        # 2. Graph Construction
        graph_data = builder.create_structure(request.concepts, embeddings, groups)
        
        # 3. Data Persistence
        map_id = db.save_user_map(request.username, request.map_title, graph_data)
        
        return {
            "status": "success",
            "model_used": request.model_type,
            "map_id": map_id,
            "data": graph_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-maps/{username}")
async def get_user_maps(username: str):
    maps = db.load_user_maps(username)
    return {"maps": maps}