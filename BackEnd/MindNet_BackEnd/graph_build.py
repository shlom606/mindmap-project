# graph_builder.py
import networkx as nx
from sklearn.neighbors import NearestNeighbors
from config import CATEGORY_MAP 
#This is taking the CATEGORY_MAP parameter from the config.py file

class GraphBuilder:
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
            knn = NearestNeighbors(n_neighbors=k_neighbors + 1, metric='cosine')
            #This line executes the KNN and searches for the k_neighbors + 1  
            #The metric is for the algorithem to measure the angle between vectors 
            #If two words point in the same direction in the 384D space, they are semantically related.

            knn.fit(embeddings)
            #Placing all the embeddings from the SBERT model into a 384D space

            distances, indices = knn.kneighbors(embeddings)
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