# ai_engine.py
import torch
import torch.nn as nn
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from config import INPUT_SIZE, HIDDEN_SIZE, NUM_CLASSES,FFNN_PATH, DEVICE,EMBEDDING_MODE, MINIBERT_EMBEDDING_PATH, VOCAB_PATH
# Import your custom architecture
from miniBERT import BERT, SimpleTokenizer

class ConceptClassifier(nn.Module):
    # Pass input_size and num_classes directly to the constructor
    def __init__(self, input_size, num_classes):
        super(ConceptClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, HIDDEN_SIZE)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(HIDDEN_SIZE, num_classes)

    def forward(self, x):
        return self.fc2(self.dropout(self.relu(self.fc1(x))))
class AIEngine:
    def __init__(self, mode='minibert'):
        self.mode = mode
        
        if self.mode == 'sbert':
            # Hardcoded values for SBERT to avoid config.py conflicts
            input_size = 384
            num_classes = 5
            model_path = 'SBERT_FFNN_Clasifier.pth'
            
            self.embedder_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.classifier = ConceptClassifier(input_size, num_classes).to(DEVICE)
            self.classifier.load_state_dict(torch.load(model_path, map_location=DEVICE))
            
        elif self.mode == 'minibert':
            # Hardcoded values for miniBERT
            input_size = 8
            num_classes = 4
            model_path = 'miniBERT_FFNN_classifier_4categories.pth'
            
            with open(VOCAB_PATH, 'r') as f:
                vocab = json.load(f)
            self.tokenizer = SimpleTokenizer(vocab)
            
            self.minibert = BERT(vocab_size=len(vocab), d_model=8, num_heads=2).to(DEVICE)
            self.minibert.load_state_dict(torch.load(MINIBERT_EMBEDDING_PATH, map_location=DEVICE))
            
            self.classifier = ConceptClassifier(input_size, num_classes).to(DEVICE)
            self.classifier.load_state_dict(torch.load(model_path, map_location=DEVICE))
            
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