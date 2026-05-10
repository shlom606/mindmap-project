import numpy as np
import networkx as nx
import hdbscan
import community as community_louvain # The Louvain library
from config import CATEGORY_MAP 

class GraphBuilder:
    @staticmethod
    def manual_knn(embeddings, k):
        """
        Custom K-Nearest Neighbors implementation using Cosine Distance.
        Demonstrates the math behind semantic similarity.
        """
        embeddings = np.array(embeddings)
        n_samples = embeddings.shape[0]
        
        # 1. Normalize vectors to unit length
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9 
        norm_embeddings = embeddings / norms

        all_distances = []
        all_indices = []

        for i in range(n_samples):
            # 2. Calculate Dot Product (Cosine Similarity)
            similarities = np.dot(norm_embeddings, norm_embeddings[i])
            
            # 3. Convert Similarity to Distance
            distances = 1 - similarities
            
            # 4. Get indices of the K+1 smallest distances 
            nearest_idx = np.argsort(distances)[:k+1]
            
            all_indices.append(nearest_idx)
            all_distances.append(distances[nearest_idx])

        return np.array(all_distances), np.array(all_indices)

    @staticmethod
    def create_structure(concepts, embeddings, group_ids):
        """
        Builds the mind map structure using KNN for edges, 
        HDBSCAN for spatial clusters, and Louvain for graph communities.
        """
        G = nx.Graph()
        n_concepts = len(concepts)

        # --- STEP 1: HDBSCAN (Density-Based Clustering) ---
        # Clusters concepts based on their 384D positions
        # min_cluster_size=2 allows for very small groups in small maps
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
        hdbscan_labels = clusterer.fit_predict(embeddings)

        # --- STEP 2: Graph Building with KNN ---
        k_neighbors = min(3, n_concepts - 1)
        if k_neighbors > 0:
            distances, indices = GraphBuilder.manual_knn(embeddings, k_neighbors)
            THRESHOLD = 0.7 

            for i in range(n_concepts):
                for j, neighbor_idx in enumerate(indices[i][1:]):
                    dist = distances[i][j+1]
                    if dist < THRESHOLD:
                        # Add edge with weight for Louvain (higher weight = closer)
                        G.add_edge(concepts[i], concepts[neighbor_idx], weight=1.0 - dist)
        
        # --- STEP 3: Louvain (Community Detection) ---
        # Identifies communities based on the topology of the links
        louvain_partition = {}
        if G.number_of_edges() > 0:
            louvain_partition = community_louvain.best_partition(G)
        else:
            # Fallback if no links were formed
            louvain_partition = {concept: 0 for concept in concepts}

        # --- STEP 4: Positioning and Node Metadata ---
        pos = nx.spring_layout(G, k=0.15, iterations=50)
        nodes = []
        for i, concept in enumerate(concepts):
            nodes.append({
                "id": concept, 
                "ffnn_group": group_ids[i], # Prediction from your Neural Network[cite: 4]
                "hdbscan_group": int(hdbscan_labels[i]), # Grouping by spatial density
                "louvain_group": louvain_partition.get(concept, 0), # Grouping by graph connectivity[cite: 1]
                "category": CATEGORY_MAP.get(group_ids[i], "Unknown"),
                "x": float(pos.get(concept, [0,0])[0] * 1000),
                "y": float(pos.get(concept, [0,0])[1] * 1000)
            })
            
        links = [{"source": u, "target": v} for u, v in G.edges()]
        
        return {"nodes": nodes, "links": links}