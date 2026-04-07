import torch
import torch.nn as nn
import networkx as nx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

# Create this dictionary at the top of main.py
CATEGORY_MAP = {
    0: "Technology & Science",
    1: "History & Society",
    2: "Nature & Biology",
    3: "Arts & Culture",
    4: "Daily Life"
}

app = FastAPI()

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_mindmap_data(user_concepts):
    if not user_concepts:
        return {"nodes": [], "links": []}

    # A. Generate Embeddings
    embeddings = sbert_model.encode(user_concepts)
    inputs = torch.tensor(embeddings).float()

    # B. FFNN Prediction (Classification)
    with torch.no_grad():
        outputs = nn_model(inputs)
        _, predicted_classes = torch.max(outputs, 1)
        # Convert tensor to list of integers
        groups = predicted_classes.tolist()

    # C. Build Graph for Positions and Links
    G = nx.Graph()
    for concept in user_concepts:
        G.add_node(concept)

    # Connect neighbors (KNN)
    k = min(len(user_concepts) - 1, 2)
    knn = NearestNeighbors(n_neighbors=k+1, metric='cosine')
    knn.fit(embeddings)
    distances, indices = knn.kneighbors(embeddings)

    for i, neighbors in enumerate(indices):
        for neighbor_idx in neighbors[1:]:
            G.add_edge(user_concepts[i], user_concepts[neighbor_idx])

    # Calculate Layout (Spring Layout)
    pos = nx.spring_layout(G, k=0.5)

    # D. Format Final JSON
    nodes = []
    for i, concept in enumerate(user_concepts):
        category_id = groups[i]
        nodes.append({
            "id": concept,
            "group": category_id,
            "category_name": CATEGORY_MAP.get(category_id, "Unknown"), # Check this line!
            "x": float(pos[concept][0] * 1000),
            "y": float(pos[concept][1] * 1000)
        })

    links = [{"source": edge[0], "target": edge[1]} for edge in G.edges()]

    return {"nodes": nodes, "links": links}

@app.post("/generate")
async def create_map(data: ConceptList):
    return generate_mindmap_data(data.concepts)