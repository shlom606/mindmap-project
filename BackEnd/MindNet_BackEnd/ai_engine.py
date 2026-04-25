# ai_engine.py
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer #import in order to load the SBERT model
from config import INPUT_SIZE, HIDDEN_SIZE, NUM_CLASSES, MODEL_PATH, DEVICE
#Gets the parameters data from the parameter file also known as config.py
class ConceptClassifier(nn.Module): #this is a class for the architecture of the FFNN

    def __init__(self):
        super(ConceptClassifier, self).__init__() 
        #This "wakes up" the parent nn.Module so PyTorch can track your gradients and layers.

        self.fc1 = nn.Linear(INPUT_SIZE, HIDDEN_SIZE) 
        #This is a fully connected layer which perform the matrix multiplication y=x*A^T+b, where A are the weights the model learned during training.
        # Takes INPUT_SIZE (384) features of the embedded vector and expands/filters them into the HIDDEN_SIZE(128) amount patterns

        self.relu = nn.ReLU() 
        #The "Rectified Linear Unit." It’s an activation function that turns off "dead" neurons (negative values), allowing the model to learn complex, non-linear relationships.

        self.dropout = nn.Dropout(0.2)
        #A regularization technique. During training, it randomly "turns off" 20% of neurons to prevent Overfitting.

        self.fc2 = nn.Linear(HIDDEN_SIZE, NUM_CLASSES)
        # Condenses the HIDDEN_SIZE(128) patterns into NUM_CLASSES(5) final category scores

    def forward(self, x):
        # This is the "Forward Pass" - how data flows through the network
        out = self.fc1(x)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return out

class AIEngine:
    def __init__(self):
        
        self.sbert = SentenceTransformer('all-MiniLM-L6-v2')
        # Load the SBERT model 

        self.model = ConceptClassifier().to(DEVICE)
        # Loads the FFNN model saved on the current directory

        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device(DEVICE)))
        #This line loads the weights saved in the MODEL_PATH file into the class blueprint

        self.model.eval()
        #This tells PyTorch to turn off Dropout and BatchNormalization because we are now using the model, not training it.

    def get_predictions(self, concepts):
        # This line generates embeddings for each of the concepts the user has given
        embeddings = self.sbert.encode(concepts)
        
        #This line is putting all of the user concept embeddings into a tensor
        inputs = torch.tensor(embeddings).float().to(DEVICE)

        with torch.no_grad():
            #This is turning off gradient calculation

            outputs = self.model(inputs)
            #This line is getting the output  (prediction vector) of the model set up previously. it will have a 5 dimention vector for each concept

            _, predicted = torch.max(outputs, 1)
            #This line is getting a single prediction from the category with the highest probability from the prediction vector

        return embeddings, predicted.tolist()
        #this returns the embeddings and the predictions for each concept