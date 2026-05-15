# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai_engine import AIEngine
from graph_build import GraphBuilder
from database import MindMapStorage
from typing import Literal
from pydantic import BaseModel
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
class UserAuth(BaseModel):
    username: str
    password: str
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
        selected_engine = engines.get(request.model_type, engines['minibert'])
        embeddings, groups = selected_engine.get_predictions(request.concepts)
        graph_data = builder.create_structure(request.concepts, embeddings, groups)
        
        # This call now handles the missing user check
        map_id = db.save_user_map(request.username, request.map_title, graph_data)
        
        return {
            "status": "success",
            "data": graph_data,
            "map_id": map_id
        }
    except ValueError as ve:
        # Catch the "User not found" error specifically
        raise HTTPException(status_code=401, detail=str(ve))
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
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