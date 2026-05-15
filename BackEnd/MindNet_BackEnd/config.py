# config.py
import torch


#This is a dictionary that maps the numerical output of the categories which it marks
#The FFNN doesn't know "Daily Life" it only knows "Class 4"
CATEGORY_MAP = {
    0: "Technology & Science",
    1: "History & Society",
    2: "Nature & Biology",
    3: "Arts & Culture",
    4: "Daily Life"
}

EMBEDDING_MODE = 'sbert'

MINIBERT_EMBEDDING_PATH = 'minibert_emb_4categories.pth'

VOCAB_PATH='vocab_4categories.json'

# Model Dimensions
#These define the topology of the FFNN neural network.
if EMBEDDING_MODE == 'minibert':
    INPUT_SIZE = 8
    NUM_CLASSES = 4
    FFNN_PATH = 'miniBERT_FFNN_classifier_4categories.pth' # The classifier trained on 8-dim vectors
else:
    INPUT_SIZE = 384
    NUM_CLASSES = 5
    FFNN_PATH = 'SBERT_FFNN_Clasifier.pth' # The original classifier trained on SBERT
#the path which has the trained FFNN model. the model was trained in google colab.
#The exact length of a vector produced by the all-MiniLM-L6-v2 SBERT model each numerical value has a neuron represnting it

HIDDEN_SIZE = 128 
#The "bottleneck" layer where the AI compresses the 384 dimensions to find the most important patterns.

# NUM_CLASSES = 5
#The number of classes that the FFNN can output from 384 dimentions vector we get a 5 dimention vector



DEVICE ='cpu'
#Checks if the device has a gpu then works with that if it doesn't then it works with the cpu. this makes the code portable
