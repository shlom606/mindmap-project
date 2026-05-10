# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import AIEngine
from graph_build import GraphBuilder
from database import MindMapStorage
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
        # 1. AI Processing: Classification & Embedding[cite: 3, 4]
        embeddings, groups = engine.get_predictions(request.concepts)
        
        # 2. Graph Construction: KNN and Force-Directed Layout
        graph_data = builder.create_structure(request.concepts, embeddings, groups)
        
        # 3. Data Persistence: Save to SQLite
        map_id = db.save_user_map(request.username, request.map_title, graph_data)
        
        return {
            "status": "success",
            "map_id": map_id,
            "data": graph_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-maps/{username}")
async def get_user_maps(username: str):
    maps = db.load_user_maps(username)
    return {"maps": maps}