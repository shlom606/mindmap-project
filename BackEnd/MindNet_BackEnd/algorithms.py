import hdbscan
import community.community_louvain as community_louvain
import networkx as nx
import hnswlib
import numpy as np

class MindMapAlgorithms:
    def __init__(self, dim=384): # 384 הוא הגודל הסטנדרטי של SBERT
        self.dim = dim
        self.index = None

    def cluster_hdbscan(self, embeddings):
        #Cluster identification based on geometric density
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
        cluster_labels = clusterer.fit_predict(embeddings)
        return cluster_labels

    def detect_communities_louvain(self, nodes, edges):
        #Identifying communities based on graph structure (Modularity)
        G = nx.Graph()
        for edge in edges:
            G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        
        partition = community_louvain.best_partition(G)
        return partition

    def build_hnsw_index(self, embeddings):
        #Building an index for fast, real-time semantic
        num_elements = len(embeddings)
        self.index = hnswlib.Index(space='cosine', dim=self.dim)
        self.index.init_index(max_elements=num_elements, ef_construction=200, M=16)
        self.index.add_items(embeddings, np.arange(num_elements))
        return self.index