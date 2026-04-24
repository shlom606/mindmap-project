# config.py
import torch

CATEGORY_MAP = {
    0: "Technology & Science",
    1: "History & Society",
    2: "Nature & Biology",
    3: "Arts & Culture",
    4: "Daily Life"
}

# Model Dimensions
INPUT_SIZE = 384
HIDDEN_SIZE = 128
NUM_CLASSES = 5
MODEL_PATH = 'mindmap_model3.pth'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'