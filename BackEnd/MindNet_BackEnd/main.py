# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import AIEngine
from graph_build import GraphBuilder

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize our specialized modules
engine = AIEngine()
builder = GraphBuilder()

class ConceptRequest(BaseModel):
    concepts: list[str]

@app.post("/generate")
async def generate(data: ConceptRequest):
    # Step 1: AI processes the text
    embeddings, groups = engine.get_predictions(data.concepts)
    
    # Step 2: Architect builds the graph
    graph_data = builder.create_structure(data.concepts, embeddings, groups)
    
    return graph_data