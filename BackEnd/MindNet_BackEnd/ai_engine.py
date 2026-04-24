# ai_engine.py
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from config import INPUT_SIZE, HIDDEN_SIZE, NUM_CLASSES, MODEL_PATH, DEVICE

class ConceptClassifier(nn.Module):
    def __init__(self):
        super(ConceptClassifier, self).__init__()
        self.fc1 = nn.Linear(INPUT_SIZE, HIDDEN_SIZE)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(HIDDEN_SIZE, NUM_CLASSES)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return out

class AIEngine:
    def __init__(self):
        # Load SBERT
        self.sbert = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load FFNN
        self.model = ConceptClassifier().to(DEVICE)
        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device(DEVICE)))
        self.model.eval()

    def get_predictions(self, concepts):
        # 1. Generate Embeddings
        embeddings = self.sbert.encode(concepts)
        
        # 2. Predict Categories
        inputs = torch.tensor(embeddings).float().to(DEVICE)
        with torch.no_grad():
            outputs = self.model(inputs)
            _, predicted = torch.max(outputs, 1)
        
        return embeddings, predicted.tolist()