import torch
import torch.nn as nn
import networkx as nx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import HDBSCAN

# Create this dictionary at the top of main.py
CATEGORY_MAP = {
    0: "Technology & Science",
    1: "History & Society",
    2: "Nature & Biology",
    3: "Arts & Culture",
    4: "Daily Life"
}

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, "*" is fine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Load SBERT Model ---
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# --- 2. Define the FFNN Architecture (Must match Colab) ---
class ConceptClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(ConceptClassifier, self).__init__()
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

# --- 3. Initialize and Load the Trained Weights ---
INPUT_SIZE = 384
HIDDEN_SIZE = 128
NUM_CLASSES = 5

nn_model = ConceptClassifier(INPUT_SIZE, HIDDEN_SIZE, NUM_CLASSES)
# Load the saved weights from Colab
nn_model.load_state_dict(torch.load('concept_model_v2.pth'))
nn_model.eval() # Set to evaluation mode

class ConceptList(BaseModel):
    concepts: list[str]


def generate_mindmap_data(user_concepts):
    if len(user_concepts) < 3: # HDBSCAN needs a minimum number of points
        return {"nodes": [], "links": []}

    # A. Generate Embeddings & FFNN Classes
    embeddings = sbert_model.encode(user_concepts)
    inputs = torch.tensor(embeddings).float()
    
    with torch.no_grad():
        outputs = nn_model(inputs)
        _, predicted_classes = torch.max(outputs, 1)
        groups = predicted_classes.tolist()

    # B. Run HDBSCAN
    # min_cluster_size: smallest group you want to find
    # min_samples: provides a measure of how conservative the clustering is
    # Standard sklearn HDBSCAN parameters
    clusterer = HDBSCAN(min_cluster_size=2, min_samples=1) 
    cluster_labels = clusterer.fit_predict(embeddings)
    #cluster_labels = clusterer.fit_predict(embeddings)

    # C. Build Graph
    G = nx.Graph()
    nodes = []
    for i, concept in enumerate(user_concepts):
        # We still use the FFNN 'group' for colors, 
        # but we can save the HDBSCAN label too
        nodes.append({
            "id": concept,
            "group": groups[i], 
            "hdbscan_cluster": int(cluster_labels[i]),
            "category_name": CATEGORY_MAP.get(groups[i], "Unknown")
        })
        G.add_node(concept)

    # D. Create Links based on HDBSCAN Clusters
    # Connect words if they belong to the same HDBSCAN cluster (and aren't noise: -1)
    for i in range(len(user_concepts)):
        for j in range(i + 1, len(user_concepts)):
            if cluster_labels[i] == cluster_labels[j] and cluster_labels[i] != -1:
                G.add_edge(user_concepts[i], user_concepts[j])

    # Calculate Layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    for node in nodes:
        node["x"] = float(pos[node["id"]][0] * 1000)
        node["y"] = float(pos[node["id"]][1] * 1000)

    links = [{"source": edge[0], "target": edge[1]} for edge in G.edges()]

    return {"nodes": nodes, "links": links}

@app.post("/generate")
async def create_map(data: ConceptList):
    return generate_mindmap_data(data.concepts)