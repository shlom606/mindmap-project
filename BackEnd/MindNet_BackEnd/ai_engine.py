# ai_engine.py
import torch
import torch.nn as nn
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from config import INPUT_SIZE, HIDDEN_SIZE, NUM_CLASSES,FFNN_PATH, DEVICE,EMBEDDING_MODE, MINIBERT_EMBEDDING_PATH
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
            # Always load the final classifier
            self.classifier = ConceptClassifier().to(DEVICE)
            self.classifier.load_state_dict(torch.load(FFNN_PATH, map_location=DEVICE))
            self.classifier.eval()
        # Inside AIEngine.__init__
        if self.mode == 'minibert':
            # 1. Load Vocab 
            # The tokenizer needs vocabulary to turn words to IDs
            with open('vocab_4categories.json', 'r') as f:
                vocab = json.load(f)
            self.tokenizer = SimpleTokenizer(vocab)
            
            # 2. Load the BERT model (The "Embedder")
            self.minibert = BERT(vocab_size=len(vocab), d_model=8, num_heads=2).to(DEVICE)
            # Load BERT weights here
            self.minibert.load_state_dict(torch.load(MINIBERT_EMBEDDING_PATH, map_location=DEVICE))
            self.minibert.eval()

            # 3. Load the Classifier (The "Logic")
            self.classifier = ConceptClassifier().to(DEVICE)
            # Load CLASSIFIER weights here (the 8-dim version you just downloaded)
            self.classifier.load_state_dict(torch.load(FFNN_PATH, map_location=DEVICE))
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