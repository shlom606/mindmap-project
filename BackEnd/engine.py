import json
import networkx as nx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import community as community_louvain

# --- 1. אתחול האפליקציה והמודל (מחוץ לפונקציות כדי שירוץ פעם אחת) ---
app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')

# הגדרת מבנה הנתונים שה-API מצפה לקבל מה-React
class ConceptList(BaseModel):
    concepts: list[str]

# הגדרת CORS (כדי שהפרונטאנד יוכל לדבר עם הבקאנד)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. הפונקציה הלוגית (המנוע של המפה) ---
def generate_mindmap_data(user_concepts):
    if not user_concepts or len(user_concepts) < 2:
        return {"nodes": [], "links": []}

    # א. יצירת Embeddings
    embeddings = model.encode(user_concepts)

    # ב. בניית הגרף
    G = nx.Graph()
    for concept in user_concepts:
        G.add_node(concept)

    # ג. חיבור שכנים קרובים (KNN)
    k = min(len(user_concepts) - 1, 2)
    knn = NearestNeighbors(n_neighbors=k+1, metric='cosine')
    knn.fit(embeddings)
    distances, indices = knn.kneighbors(embeddings)

    for i, neighbors in enumerate(indices):
        for neighbor_idx in neighbors[1:]:
            G.add_edge(user_concepts[i], user_concepts[neighbor_idx])

    # ד. זיהוי קהילות (צבעים)
    partition = community_louvain.best_partition(G)

    # ה. חישוב מיקומים (X, Y)
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # ו. בניית ה-JSON הסופי
    nodes = []
    for concept in user_concepts:
        nodes.append({
            "id": concept,
            "group": partition.get(concept, 0),
            "x": float(pos[concept][0] * 1000),
            "y": float(pos[concept][1] * 1000)
        })

    links = []
    for edge in G.edges():
        links.append({
            "source": edge[0],
            "target": edge[1]
        })

    return {"nodes": nodes, "links": links}

# --- 3. ה-Routes (הנתיבים של ה-API) ---

# נתיב לקבלת רשימה חדשה ויצירת מפה בזמן אמת
@app.post("/generate")
async def create_map(data: ConceptList):
    print(f"Generating map for: {data.concepts}")
    result = generate_mindmap_data(data.concepts)
    return result

# נתיב "ברירת מחדל" למקרה שאתה עדיין רוצה לטעון את הקובץ הישן
@app.get("/graph")
async def get_static_graph():
    try:
        with open('mindmap_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"nodes": [], "links": []}

# להרצה בטרמינל: uvicorn main:app --reload