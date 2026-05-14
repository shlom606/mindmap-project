# ai_engine.py
import torch
import torch.nn as nn
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from config import INPUT_SIZE, HIDDEN_SIZE, NUM_CLASSES, MODEL_PATH, DEVICE,EMBEDDING_MODE
# Import your custom architecture
from miniBERT import BERT, SimpleTokenizer

class ConceptClassifier(nn.Module):
    """FFNN to classify the embeddings into 5 categories."""
    def __init__(self):
        super(ConceptClassifier, self).__init__()
        self.fc1 = nn.Linear(INPUT_SIZE, HIDDEN_SIZE)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(HIDDEN_SIZE, NUM_CLASSES)

    def forward(self, x):
        return self.fc2(self.dropout(self.relu(self.fc1(x))))

class AIEngine:
    def __init__(self, mode=EMBEDDING_MODE):
        self.mode = mode
        
        if self.mode == 'sbert':
            self.embedder_model = SentenceTransformer('all-MiniLM-L6-v2')
        # Inside AIEngine.__init__
        if self.mode == 'minibert':
            # Load vocabulary from the json file
            with open('vocab.json', 'r') as f:
                vocab = json.load(f)
            
            self.tokenizer = SimpleTokenizer(vocab, max_len=15)
            
            # IMPORTANT: Use the exact parameters from your training!
            self.minibert = BERT(
                vocab_size=len(vocab), 
                d_model=8,      # Matches your training d_model
                num_heads=2,    # Matches your training num_heads
                max_len=15      # Matches your training max_len
            ).to(DEVICE)
            
            # Load the weights you saved
            self.minibert.load_state_dict(torch.load('minibert_weights.pth', map_location=DEVICE))
            self.minibert.eval()

        # Always load the final classifier
        self.classifier = ConceptClassifier().to(DEVICE)
        self.classifier.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        self.classifier.eval()

    def get_predictions(self, concepts):
        """Processes words and returns both coordinates (embeddings) and groups."""
        if self.mode == 'sbert':
            embeddings = self.embedder_model.encode(concepts)
        else:
            embeddings = []
            for text in concepts:
                ids = torch.tensor([self.tokenizer.encode(text)]).to(DEVICE)
                with torch.no_grad():
                    # Extract the [CLS] token vector as the concept's embedding
                    states = self.minibert(ids)
                    embeddings.append(states[0, 0, :].cpu().numpy())
            embeddings = np.array(embeddings)
        
        inputs = torch.tensor(embeddings).float().to(DEVICE)
        with torch.no_grad():
            outputs = self.classifier(inputs)
            _, predicted = torch.max(outputs, 1)

        return embeddings, predicted.tolist()