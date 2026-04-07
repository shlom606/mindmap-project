from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# --- זה החלק הקריטי לפתרון השגיאה ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # מאפשר לכל כתובת (כולל localhost של React) לגשת
    allow_credentials=True,
    allow_methods=["*"],      # מאפשר את כל סוגי הבקשות (GET, POST וכו')
    allow_headers=["*"],      # מאפשר את כל ה-Headers
)
# ------------------------------------



@app.get("/graph")
async def get_graph():
    try:
        with open('mindmap_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        return {"error": str(e)}

# הרצה בטרמינל: uvicorn main:app --reload