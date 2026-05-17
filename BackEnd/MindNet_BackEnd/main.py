# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import AIEngine
from graph_build import GraphBuilder
from database import MindMapStorage
from typing import Literal
from pydantic import BaseModel
import requests
#The FastAPI settings to initilise the web server
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize our specialized modules
#engine = AIEngine() #this from ai_engine.py
builder = GraphBuilder() #this is from graph_build.py
db = MindMapStorage()
GO_HNSW_URL = "http://127.0.0.1:8080"

class HNSWSearchRequest(BaseModel):
    query_text: str
class ConceptRequest(BaseModel):
    concepts: list[str]

class MapGenerationRequest(BaseModel):
    username: str
    map_title: str
    concepts: list[str]
    model_type: str # Add this field

class UserAuth(BaseModel):
    username: str
    password: str
# Pre-load both engines for fast switching
engines = {
    'sbert': AIEngine(mode='sbert'),
    'minibert': AIEngine(mode='minibert')
}
# @app.post("/generate")
# async def generate(data: ConceptRequest):
#     # Step 1: AI processes the text
#     embeddings, groups = engine.get_predictions(data.concepts)
    
#     # Step 2: Architect builds the graph
#     graph_data = builder.create_structure(data.concepts, embeddings, groups)
    
#     return graph_data
@app.post("/generate-and-save")
async def generate_and_save(request: MapGenerationRequest):
    # 1. THE TRACKER: Watch your Python terminal when you click generate!
    print("\n--- NEW GENERATION REQUEST ---")
    print(f"Words: {request.concepts}")
    print(f"Model Requested by React: '{request.model_type}'")
    
    try:
        # 2. Strict selection
        selected_engine = engines.get(request.model_type)
        if not selected_engine:
            print(f"CRITICAL: '{request.model_type}' not found! Using fallback.")
            selected_engine = engines.get('minibert')
            
        embeddings, groups = selected_engine.get_predictions(request.concepts)
        index_concepts_in_hnsw(request.concepts, embeddings)
        graph_data = builder.create_structure(
            request.concepts, 
            embeddings, 
            groups, 
            mode=request.model_type
        )
        
        map_id = db.save_user_map(request.username, request.map_title, graph_data)
        print("--- SUCCESS ---")
        return {
            "status": "success",
            "data": graph_data,
            "map_id": map_id
        }
    except Exception as e:
        print(f"--- CRASH: {str(e)} ---") # This prints the exact error!
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/my-maps/{username}")
async def get_user_maps(username: str):
    # This calls the load_user_maps method we added to database.py earlier
    maps = db.load_user_maps(username)
    if maps is None:
        return {"maps": []}
    return {"maps": maps}

# 2. Add the SIGNUP route
@app.post("/signup")
async def signup(user: UserAuth):
    # This calls the database logic 
    success = db.signup_user(user.username, user.password)
    if not success:
        # If the username is already in the DB, return 400
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"status": "success"} 

@app.post("/login")
async def login(user: UserAuth):
    # This calls the authentication method in database.py
    if db.authenticate_user(user.username, user.password):
        return {"status": "success", "username": user.username}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.delete("/delete-map/{username}/{map_id}")
async def delete_map(username: str, map_id: int):
    # This calls the delete method in database.py
    if db.delete_user_map(username, map_id):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Map not found or unauthorized")


# 1. פונקציית עזר לאינדוקס מילים ב-Go (נקרא לה מתוך generate_and_save)
def index_concepts_in_hnsw(concepts, embeddings):
    try:
        for i, concept in enumerate(concepts):
            payload = {
                "id": i,  # מזהה זמני או מזהה מה-DB שלך
                "concept": concept,
                "vector": embeddings[i].tolist()  # הפיכת מערך numpy לרשימת floats
            }
            requests.post(f"{GO_HNSW_URL}/insert", json=payload)
    except Exception as e:
        print(f"Failed to index in HNSW Go Service: {e}")

# 2. נתיב חדש עבור ה-Search Bar ב-Frontend
@app.post("/api/semantic-search")
async def semantic_search(request: HNSWSearchRequest):
    try:
        # שימוש במודל SBERT הקיים שלך ב-FastAPI כדי להפוך את מילת החיפוש לוקטור
        sbert_engine = engines.get('sbert')
        if not sbert_engine:
            raise HTTPException(status_code=500, detail="SBERT engine not loaded")
            
        embeddings, _ = sbert_engine.get_predictions([request.query_text])
        query_vector = embeddings[0].tolist()

        # שליחת הוקטור לשרת ה-Go לחיפוש מהיר חוצה שכבות
        go_response = requests.post(f"{GO_HNSW_URL}/search", json={"vector": query_vector})
        result = go_response.json()

        return result  # יחזיר את ה-status, matched_id, וה-concept
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")