# graph_builder.py
import numpy as np
import networkx as nx
from sklearn.neighbors import NearestNeighbors #try to implement knn myself
from config import CATEGORY_MAP 
#This is taking the CATEGORY_MAP parameter from the config.py file

class GraphBuilder:
    @staticmethod
    def manual_knn(embeddings, k):
        """
        Custom K-Nearest Neighbors implementation using Cosine Distance.
        Replaces sklearn's NearestNeighbors to demonstrate algorithmic understanding.
        """
        # Ensure embeddings is a numpy array for vector operations
        embeddings = np.array(embeddings)
        n_samples = embeddings.shape[0]
        
        # 1. Normalize vectors to unit length (L2 Norm)
        # This allows us to calculate Cosine Similarity via Dot Product
        #This limit every vector from 384D into 1D keeping his direction
        #The direction is the only thing that matters cause we use Cosine Similarity which only utilise angel
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Prevent division by zero if an embedding is all zeros
        norms[norms == 0] = 1e-9 
        # Divide each vector by its length to get a unit vector (length = 1) 
        norm_embeddings = embeddings / norms

        all_distances = []
        all_indices = []

        for i in range(n_samples):
            # 2. Calculate Dot Product between current vector and all others
            # Since vectors are normalized, dot product equals cosine similarity
            similarities = np.dot(norm_embeddings, norm_embeddings[i])
            
            # 3. Convert Similarity to Distance (0.0 means identical, 1.0 means orthogonal)
            distances = 1 - similarities
            
            # 4. Get indices of the K+1 smallest distances 
            # We use K+1 because the smallest distance is always the node itself (dist=0)
            #It takes the K+1 distances from small to big values the smaller the
            nearest_idx = np.argsort(distances)[:k+1]
            
            all_indices.append(nearest_idx)
            all_distances.append(distances[nearest_idx])

        return np.array(all_distances), np.array(all_indices)




    @staticmethod
    #This is a static method cause it does not need to save data only to create the graph

    def create_structure(concepts, embeddings, group_ids):
        G = nx.Graph()
        #This is a function from the networkx library which creates an empty container that understands graph theory

        n_concepts = len(concepts)
        #This is the amount of concepts the user has


        # Dynamic K: Don't look for more neighbors than exist!
        k_neighbors = min(3, n_concepts - 1)
        #The algorithem looks between 3 neighbours and n_concepts-1 neighbours the -1 is to not include itself

        if k_neighbors > 0:# If there is more then one concept
            distances, indices = GraphBuilder.manual_knn(embeddings, k_neighbors)
            #This line executes the KNN and searches for the k_neighbors + 1  
            #The metric is for the algorithem to measure the angle between vectors 
            #If two words point in the same direction in the 384D space, they are semantically related.

            #knn.fit(embeddings)
            #Placing all the embeddings from the SBERT model into a 384D space

            #distances, indices = knn.kneighbors(embeddings)
            #For every word, the algorithm looks around and finds the K closest words.
            #Then stores the indices and distances of the 384D vectors into the according lists

            # Use a threshold (Cosine distance is 0.0 to 1.0)
            # 0.7 means "if they are more than 70% different, don't draw a line"
            THRESHOLD = 0.7 

            for i in range(n_concepts):
            #A for loop going over all the concepts which i is an index to
                for j, neighbor_idx in enumerate(indices[i][1:]):
                    #This line helps find the current value and index of the array
                    #It stores the current Index in the j parameter and its value at neighbor_idx
                    #indices[i]: The list of IDs for its closest friends.
                    dist = distances[i][j+1]
                    #This line gets the amount of distance between concept number i and j+1
                    if dist < THRESHOLD: # Only add edge if they are actually 'close'
                        #This line checks if the distance is diffrent by the THRESHOLD amount 
                        #If its less then it adds the edge between the word in index i and the word in index neighbor_idx
                        G.add_edge(concepts[i], concepts[neighbor_idx])
        
        # Calculate X, Y positions (The Spring Physics)
        pos = nx.spring_layout(G, k=0.15, iterations=50)
        #NetworkX uses the Fruchterman-Reingold force-directed algorithm
        #Repulsion: It treats every node like a magnet. They all want to push each other away so they don't overlap.
        #Attraction: It treats every edge (link) like a rubber band. It pulls connected words closer together.

        nodes = []
        for i, concept in enumerate(concepts):
            #For each of the concepts it stores a value in cocept and index in i
            nodes.append({
                "id": concept, 
                #The id of the concept will be his name

                "group": group_ids[i], 
                #The group is the value of the predicted category in the predicted category list with i as its index

                "category": CATEGORY_MAP.get(group_ids[i], "Unknown"),
                "x": float(pos.get(concept, [0,0])[0] * 1000),
                "y": float(pos.get(concept, [0,0])[1] * 1000)
                #The spring layout gives coordinents by the value -1 to 1 
                #We need to multiply by 1000 to fit a regular computer monitor
            })
            
        links = [{"source": u, "target": v} for u, v in G.edges()]
        
        return {"nodes": nodes, "links": links}