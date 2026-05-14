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

MINIBERT_PATH = 'minibert_weights.pth'


# Model Dimensions
#These define the topology of the FFNN neural network.
INPUT_SIZE = 8 if EMBEDDING_MODE == 'minibert' else 384
#The exact length of a vector produced by the all-MiniLM-L6-v2 SBERT model each numerical value has a neuron represnting it

HIDDEN_SIZE = 128 
#The "bottleneck" layer where the AI compresses the 384 dimensions to find the most important patterns.

NUM_CLASSES = 5
#The number of classes that the FFNN can output from 384 dimentions vector we get a 5 dimention vector
MODEL_PATH = 'mindmap_FFNN.pth' #the path which has the trained FFNN model. the model was trained in google colab.


DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
#Checks if the device has a gpu then works with that if it doesn't then it works with the cpu. this makes the code portable
