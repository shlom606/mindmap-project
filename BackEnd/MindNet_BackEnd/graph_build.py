# graph_build.py
import networkx as nx

# Import our custom white-box algorithms
from algorithms import manual_knn, white_box_density_cluster, white_box_modularity_community

class GraphBuilder:
    SBERT_MAP = {
        0: "Technology & Science",
        1: "History & Society",
        2: "Nature & Biology",
        3: "Arts & Culture",
        4: "Daily Life"
    }

    MINIBERT_MAP = {
        0: "Fruit",
        1: "Machine Learning",
        2: "History",
        3: "Daily Life"
    }

    @classmethod
    def create_structure(cls, concepts, embeddings, group_ids, mode='minibert'):
        """Orchestrates the graph building process and formats output."""
        G = nx.Graph()
        n_concepts = len(concepts)

        # 1. Density Clustering (HDBSCAN Replacement)
        density_labels = white_box_density_cluster(embeddings)

        # 2. Add Edges via KNN
        k_neighbors = min(3, n_concepts - 1)
        if k_neighbors > 0:
            distances, indices = manual_knn(embeddings, k_neighbors)
            for i in range(n_concepts):
                for j, neighbor_idx in enumerate(indices[i][1:]):
                    if distances[i][j+1] < 0.7:
                        G.add_edge(concepts[i], concepts[neighbor_idx], weight=1.0 - distances[i][j+1])
        
        # 3. Community Detection (Louvain Replacement)
        community_partition = white_box_modularity_community(G)

        # 4. Determine Active Category Map
        current_map = cls.SBERT_MAP if mode == 'sbert' else cls.MINIBERT_MAP

        # 5. Metadata Assembly & Coordinates
        pos = nx.spring_layout(G, k=0.15, iterations=50)
        nodes = []
        for i, concept in enumerate(concepts):
            nodes.append({
                "id": concept, 
                "ffnn_group": group_ids[i],
                "hdbscan_group": int(density_labels[i]), 
                "louvain_group": community_partition.get(concept, 0),
                "category": current_map.get(group_ids[i], "Unknown"),
                "x": float(pos.get(concept, [0,0])[0] * 1000),
                "y": float(pos.get(concept, [0,0])[1] * 1000)
            })
            
        links = [{"source": u, "target": v} for u, v in G.edges()]
        return {"nodes": nodes, "links": links}