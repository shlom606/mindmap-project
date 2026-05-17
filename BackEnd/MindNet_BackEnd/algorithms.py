# algorithms.py
import numpy as np
import networkx as nx

def manual_knn(embeddings, k):
    """White box KNN logic using Cosine Distance."""
    embeddings = np.array(embeddings)
    n_samples = embeddings.shape[0]
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9 
    norm_embeddings = embeddings / norms
    all_distances, all_indices = [], []

    for i in range(n_samples):
        similarities = np.dot(norm_embeddings, norm_embeddings[i])
        distances = 1 - similarities
        nearest_idx = np.argsort(distances)[:k+1]
        all_indices.append(nearest_idx)
        all_distances.append(distances[nearest_idx])
    return np.array(all_distances), np.array(all_indices)



def white_box_density_cluster(embeddings, eps=0.6, min_samples=2):
    """
    White box density-based clustering.
    Replaces HDBSCAN. Uses a DBSCAN-style neighborhood expansion.
    """
    # ADD THIS LINE: Convert Python list to a Numpy array first!
    embeddings = np.array(embeddings) 
    
    n = len(embeddings)
    labels = -1 * np.ones(n) # -1 indicates noise
    cluster_id = 0
    
    # Calculate Euclidean distance matrix (This is what was crashing)
    diff = embeddings[:, np.newaxis, :] - embeddings[np.newaxis, :, :]
    dist_matrix = np.linalg.norm(diff, axis=2)
    
    for i in range(n):
        if labels[i] != -1: continue 
        
        neighbors = np.where(dist_matrix[i] < eps)[0]
        if len(neighbors) < min_samples: continue
        
        # Expand cluster
        labels[i] = cluster_id
        queue = list(neighbors)
        while queue:
            neighbor_idx = queue.pop(0)
            if labels[neighbor_idx] == -1: 
                labels[neighbor_idx] = cluster_id
                new_neighbors = np.where(dist_matrix[neighbor_idx] < eps)[0]
                if len(new_neighbors) >= min_samples:
                    queue.extend([nn for nn in new_neighbors if labels[nn] == -1])
        cluster_id += 1
        
    return labels.astype(int)


def white_box_modularity_community(G):
    """
    White box Greedy Modularity Community Detection.
    Replaces python-louvain. Iteratively merges nodes to maximize graph modularity.
    """
    if G.number_of_nodes() == 0: return {}
    
    # Start with each node in its own community
    partition = {node: i for i, node in enumerate(G.nodes())}
    m = G.size(weight='weight')
    if m == 0: return {node: 0 for node in G.nodes()}

    def get_modularity(curr_partition):
        """Calculates the modularity score Q of the current partition."""
        q = 0
        for community in set(curr_partition.values()):
            nodes_in_comm = [n for n, c in curr_partition.items() if c == community]
            subgraph = G.subgraph(nodes_in_comm)
            lc = subgraph.size(weight='weight') # Internal edges
            dc = sum(dict(G.degree(nodes_in_comm, weight='weight')).values()) # Total edges
            q += (lc / m) - (dc / (2 * m))**2
        return q

    improved = True
    while improved:
        improved = False
        for node in G.nodes():
            old_comm = partition[node]
            best_q = get_modularity(partition)
            
            # Test moving node to neighbor's communities
            for neighbor in G.neighbors(node):
                new_comm = partition[neighbor]
                if new_comm == old_comm: continue
                
                partition[node] = new_comm
                new_q = get_modularity(partition)
                
                if new_q > best_q:
                    best_q = new_q
                    improved = True
                else:
                    partition[node] = old_comm # Revert change if it didn't improve Q
                    
    return partition