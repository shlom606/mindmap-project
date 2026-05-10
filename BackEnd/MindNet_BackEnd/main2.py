# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from ai_engine import AIEngine
from graph_build import GraphBuilder
from database import DatabaseManager

app = FastAPI()
engine = AIEngine()
builder = GraphBuilder()
db = DatabaseManager()

class ConceptRequest(BaseModel):
    title: str
    concepts: list[str]

class SearchRequest(BaseModel):
    query: str

@app.post("/generate")
async def generate(data: ConceptRequest):
    # 1. AI processing (Embeddings and FFNN classification)
    embeddings, groups = engine.get_predictions(data.concepts)
    
    # 2. Build HNSW Index for the search bar functionality
    engine.build_search_index(embeddings)
    
    # 3. Create Graph Structure (KNN and Spring Layout)
    graph_data = builder.create_structure(data.concepts, embeddings, groups)
    
    # 4. Save to SQLite for persistence
    map_id = db.save_map(data.title, graph_data["nodes"], graph_data["links"])
    
    return {"id": map_id, "graph": graph_data}

@app.post("/search")
async def search(data: SearchRequest):
    # Perform semantic search using HNSW
    indices = engine.search_similar_concepts(data.query)
    return {"related_indices": indices}

@app.get("/history")
async def get_history():
    # Return list of previous maps from SQLite
    return db.get_all_maps()