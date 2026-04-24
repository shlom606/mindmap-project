import torch
import torch.nn as nn
import networkx as nx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import HDBSCAN
import numpy as np

# --- CONFIGURATION & CATEGORY MAPPING ---
CATEGORY_MAP = {
    0: "Technology & Science",
    1: "History & Society",
    2: "Nature & Biology",
    3: "Arts & Culture",
    4: "Daily Life"
}



# --- STAGE 1: THE BRAIN (AI MODELS) ---
class ConceptClassifier(nn.Module):
    def __init__(self, input_size=384, hidden_size=128, num_classes=5):
        super(ConceptClassifier, self).__init__()
        # Use 'fc1' and 'fc2' to match your Colab names exactly
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return out

class MindMapBrain:
    """Encapsulates all AI processing: Embeddings, Classification, and Clustering"""
    def __init__(self, model_path='concept_model_v2.pth'):
        self.sbert = SentenceTransformer('all-MiniLM-L6-v2')
        self.classifier = ConceptClassifier()
        # Load weights and set to evaluation mode
        try:
            self.classifier.load_state_dict(torch.load('mindmap_model.pth', map_location=torch.device('cpu')))
            self.classifier.eval()
        except FileNotFoundError:
            print(f"Warning: {model_path} not found. FFNN will use random weights.")

    def process_concepts(self, text_list):
        # 1. Embeddings (SBERT)
        embeddings = self.sbert.encode(text_list)
        
        # 2. Classification (FFNN)
        with torch.no_grad():
            inputs = torch.tensor(embeddings).float()
            logits = self.classifier(inputs)
            group_ids = torch.argmax(logits, dim=1).tolist()
        
        # 3. Density Clustering (HDBSCAN)
        # Identifies 'Islands' of thought
        clusterer = HDBSCAN(min_cluster_size=2, min_samples=1, metric='euclidean')
        cluster_labels = clusterer.fit_predict(embeddings).tolist()
        
        return embeddings, group_ids, cluster_labels

# --- STAGE 2: THE GRAPH PROCESSOR (LOGIC) ---
class GraphProcessor:
    """Turns AI data into a visual map using KNN and NetworkX"""
    @staticmethod
    def build_web(concepts, embeddings, groups, clusters):
        G = nx.Graph()
        
        # A. Neighborhood Search (KNN) - This creates the 'Lines'
        # We find the 3 closest neighbors for every word to create a 'web'
        knn = NearestNeighbors(n_neighbors=4, metric='cosine')
        knn.fit(embeddings)
        distances, indices = knn.kneighbors(embeddings)

        nodes = []
        for i, concept in enumerate(concepts):
            nodes.append({
                "id": concept,
                "group": groups[i],
                "cluster": clusters[i],
                "category": CATEGORY_MAP.get(groups[i], "General")
            })
            
            # Create Links based on KNN (The core Mind Map web)
            for neighbor_idx in indices[i][1:]: # Skip itself
                G.add_edge(concept, concepts[neighbor_idx])

        # B. Force-Directed Layout (NetworkX)
        # Calculates X,Y positions based on physics
        pos = nx.spring_layout(G, k=0.15, iterations=50)
        
        for node in nodes:
            node["x"] = float(pos[node["id"]][0] * 1000)
            node["y"] = float(pos[node["id"]][1] * 1000)


        nodes_output = []
        for node in nodes:
            nodes_output.append({
                "id": str(node["id"]),
                "group": int(node["group"]),
                "cluster": int(node["cluster"]),
                "category": str(node["category"]),
                "x": float(node["x"]),
                "y": float(node["y"])
            })

        links_output = []
        for edge in G.edges():
            links_output.append({
                "source": str(edge[0]),
                "target": str(edge[1])
            })

        # Return only the cleaned dictionaries
        return {"nodes": nodes_output, "links": links_output}

# --- STAGE 3: THE API (FASTAPI) ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For your school project, "*" allows any frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

brain = MindMapBrain()

class ConceptRequest(BaseModel):
    concepts: list[str]

@app.post("/generate")
async def generate_map(request: ConceptRequest):
    if len(request.concepts) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 concepts")
    
    # Run the pipeline
    embeddings, groups, clusters = brain.process_concepts(request.concepts)
    data = GraphProcessor.build_web(request.concepts, embeddings, groups, clusters)
    
    return data