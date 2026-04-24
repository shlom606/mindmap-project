# graph_builder.py
import networkx as nx
from sklearn.neighbors import NearestNeighbors
from config import CATEGORY_MAP

class GraphBuilder:
    @staticmethod
    def create_structure(concepts, embeddings, group_ids):
        G = nx.Graph()
        n_concepts = len(concepts)
        
        # Dynamic K: Don't look for more neighbors than exist!
        k_neighbors = min(3, n_concepts - 1)
        
        if k_neighbors > 0:
            knn = NearestNeighbors(n_neighbors=k_neighbors + 1, metric='cosine')
            knn.fit(embeddings)
            distances, indices = knn.kneighbors(embeddings)
            
            for i in range(n_concepts):
                for neighbor_idx in indices[i][1:]: # Skip self
                    G.add_edge(concepts[i], concepts[neighbor_idx])
        
        # Calculate X, Y positions (The Spring Physics)
        pos = nx.spring_layout(G, k=0.15, iterations=50)
        
        nodes = []
        for i, concept in enumerate(concepts):
            nodes.append({
                "id": concept,
                "group": group_ids[i],
                "category": CATEGORY_MAP.get(group_ids[i], "Unknown"),
                "x": float(pos.get(concept, [0,0])[0] * 1000),
                "y": float(pos.get(concept, [0,0])[1] * 1000)
            })
            
        links = [{"source": u, "target": v} for u, v in G.edges()]
        
        return {"nodes": nodes, "links": links}