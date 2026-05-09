import hdbscan
import community.community_louvain as community_louvain
import networkx as nx
import hnswlib
import numpy as np

class MindMapAlgorithms:
    @staticmethod
    def get_hdbscan_clusters(embeddings):
        # זיהוי צבירים על בסיס צפיפות (Density-based)
        # זה מוצא קבוצות "טבעיות" במרחב הוקטורי בלי קשר לקטגוריות של ה-FFNN
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
        return clusterer.fit_predict(embeddings)

    @staticmethod
    def get_louvain_communities(nodes, edges):
        # זיהוי קהילות על בסיס מבנה הגרף (Modularity)
        if not edges:
            return {node['id']: 0 for node in nodes}
            
        G = nx.Graph()
        for edge in edges:
            G.add_edge(edge['source'], edge['target'])
        
        # מחזיר דירוג קהילה לכל צומת
        return community_louvain.best_partition(G)

    @staticmethod
    def build_fast_search(embeddings):
        # אינדוקס HNSW לחיפוש סמנטי מהיר (O(log n))
        dim = embeddings.shape[1]
        num_elements = embeddings.shape[0]
        p = hnswlib.Index(space='cosine', dim=dim)
        p.init_index(max_elements=num_elements, ef_construction=200, M=16)
        p.add_items(embeddings)
        return p