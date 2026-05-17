package main

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

const (
	Dimension = 384 // מתאים לוקטורים של SBERT
	M         = 16  // מקסימום חיבורים בשכבות עליונות
	M0        = 32  // מקסימום חיבורים בשכבה התחתונה (שכבה 0)
	MaxLevels = 5
)

type HNSWNode struct {
	ID             int                `json:"id"`
	Concept        string             `json:"concept"`
	Vector         [Dimension]float32 `json:"vector"`
	Level          int                `json:"level"`
	Neighbors      [][] *HNSWNode     `json:"-"`
	NeighborCounts []int              `json:"-"`
}

type HNSWIndex struct {
	EnterNode *HNSWNode
	MaxLevel  int
	mu        sync.RWMutex
}

var index = &HNSWIndex{EnterNode: nil, MaxLevel: 0}

// חישוב מרחק קוסינוס
func calculateDistance(v1, v2 [Dimension]float32) float32 {
	var dot, normA, normB float32
	for i := 0; i < Dimension; i++ {
		dot += v1[i] * v2[i]
		normA += v1[i] * v1[i]
		normB += v2[i] * v2[i]
	}
	if normA == 0 || normB == 0 {
		return 1.0
	}
	return 1.0 - (dot / (float32(math.Sqrt(float64(normA))) * float32(math.Sqrt(float64(normB)))))
}

func getRandomLevel() int {
	level := 0
	for rand.Intn(2) == 0 && level < MaxLevels-1 {
		level++
	}
	return level
}

func searchLayer(query [Dimension]float32, enterNode *HNSWNode, layer int) *HNSWNode {
	currNode := enterNode
	currDist := calculateDistance(query, currNode.Vector)
	changed := true

	for changed {
		changed = false
		for i := 0; i < currNode.NeighborCounts[layer]; i++ {
			neighbor := currNode.Neighbors[layer][i]
			dist := calculateDistance(query, neighbor.Vector)
			if dist < currDist {
				currDist = dist
				currNode = neighbor
				changed = true
			}
		}
	}
	return currNode
}

func hnswSearch(query [Dimension]float32) *HNSWNode {
	index.mu.RLock()
	defer index.mu.RUnlock()

	if index.EnterNode == nil {
		return nil
	}
	currNode := index.EnterNode
	for l := index.MaxLevel; l > 0; l-- {
		currNode = searchLayer(query, currNode, l)
	}
	return searchLayer(query, currNode, 0)
}

func hnswInsert(id int, concept string, vector [Dimension]float32) {
	index.mu.Lock()
	defer index.mu.Unlock()

	newNode := &HNSWNode{
		ID:             id,
		Concept:        concept,
		Vector:         vector,
		Level:          getRandomLevel(),
		Neighbors:      make([][]*HNSWNode, MaxLevels),
		NeighborCounts: make([]int, MaxLevels),
	}

	for i := 0; i < MaxLevels; i++ {
		maxLinks := M
		if i == 0 {
			maxLinks = M0
		}
		newNode.Neighbors[i] = make([]*HNSWNode, maxLinks)
	}

	if index.EnterNode == nil {
		index.EnterNode = newNode
		index.MaxLevel = newNode.Level
		return
	}

	currNode := index.EnterNode
	for l := index.MaxLevel; l > newNode.Level; l-- {
		currNode = searchLayer(vector, currNode, l)
	}

	startLevel := newNode.Level
	if newNode.Level > index.MaxLevel {
		startLevel = index.MaxLevel
	}

	for l := startLevel; l >= 0; l-- {
		currNode = searchLayer(vector, currNode, l)
		maxLinks := M
		if l == 0 {
			maxLinks = M0
		}

		if currNode.NeighborCounts[l] < maxLinks {
			currNode.Neighbors[l][currNode.NeighborCounts[l]] = newNode
			currNode.NeighborCounts[l]++

			newNode.Neighbors[l][newNode.NeighborCounts[l]] = currNode
			newNode.NeighborCounts[l]++
		}
	}

	if newNode.Level > index.MaxLevel {
		index.MaxLevel = newNode.Level
		index.EnterNode = newNode
	}
}

// מנגנוני ה-API לחיבור חיצוני
type InsertPayload struct {
	ID      int                `json:"id"`
	Concept string             `json:"concept"`
	Vector  [Dimension]float32 `json:"vector"`
}

type SearchPayload struct {
	Vector [Dimension]float32 `json:"vector"`
}

func insertHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		return
	}
	var p InsertPayload
	json.NewDecoder(r.Body).Decode(&p)
	hnswInsert(p.ID, p.Concept, p.Vector)
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "inserted"})
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		return
	}
	var p SearchPayload
	json.NewDecoder(r.Body).Decode(&p)
	match := hnswSearch(p.Vector)
	if match == nil {
		json.NewEncoder(w).Encode(map[string]interface{}{"status": "empty", "matched_id": -1})
		return
	}
	json.NewEncoder(w).Encode(map[string]interface{}{"status": "success", "matched_id": match.ID, "concept": match.Concept})
}

func main() {
	rand.Seed(time.Now().UnixNano())
	http.HandleFunc("/insert", insertHandler)
	http.HandleFunc("/search", searchHandler)
	fmt.Println("🚀 Go HNSW Indexer running on port 8080...")
	http.ListenAndServe(":8080", nil)
}