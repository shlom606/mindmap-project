#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define DIMENSION 384     // מתאים ל-SBERT (שנה ל-8 עבור miniBERT)
#define M 16              // מקסימום חיבורים לצומת בשכבות עליונות
#define M0 32             // מקסימום חיבורים לצומת בשכבה 0
#define MAX_LEVELS 5      // מקסימום שכבות בגרף

typedef struct HNSWNode {
    int id;
    float vector[DIMENSION];
    int level;
    struct HNSWNode** neighbors[MAX_LEVELS];
    int neighbor_counts[MAX_LEVELS];
} HNSWNode;

typedef struct {
    HNSWNode* enter_node;
    int max_level;
} HNSWIndex;

// 1. חישוב מרחק קוסינוס (White Box)
float calculate_distance(float* v1, float* v2) {
    float dot = 0.0f, norm_a = 0.0f, norm_b = 0.0f;
    for (int i = 0; i < DIMENSION; i++) {
        dot += v1[i] * v2[i];
        norm_a += v1[i] * v1[i];
        norm_b += v2[i] * v2[i];
    }
    if (norm_a == 0.0f || norm_b == 0.0f) return 1.0f;
    return 1.0f - (dot / (sqrtf(norm_a) * sqrtf(norm_b)));
}

// 2. הגרלת שכבה לצומת חדש (הסתברות דמוית Skip-List)
int get_random_level() {
    int level = 0;
    while (rand() % 2 == 0 && level < MAX_LEVELS - 1) {
        level++;
    }
    return level;
}

// 3. חיפוש חמדן בשכבה בודדת
HNSWNode* search_layer(float* query, HNSWNode* enter_node, int layer) {
    HNSWNode* curr_node = enter_node;
    float curr_dist = calculate_distance(query, curr_node->vector);
    int changed = 1;

    while (changed) {
        changed = 0;
        int count = curr_node->neighbor_counts[layer];
        for (int i = 0; i < count; i++) {
            HNSWNode* neighbor = curr_node->neighbors[layer][i];
            float dist = calculate_distance(query, neighbor->vector);
            if (dist < curr_dist) {
                curr_dist = dist;
                curr_node = neighbor;
                changed = 1;
            }
        }
    }
    return curr_node;
}

// 4. חיפוש KNN קלאסי חוצה שכבות
HNSWNode* hnsw_search(HNSWIndex* index, float* query) {
    if (!index->enter_node) return NULL;
    HNSWNode* curr_node = index->enter_node;
    for (int l = index->max_level; l > 0; l--) {
        curr_node = search_layer(query, curr_node, l);
    }
    return search_layer(query, curr_node, 0);
}

// 5. הכנסת צומת חדש לגרף וקישור לשכנים
void hnsw_insert(HNSWIndex* index, int id, float* vector) {
    HNSWNode* new_node = (HNSWNode*)malloc(sizeof(HNSWNode));
    new_node->id = id;
    new_node->level = get_random_level();
    for (int i = 0; i < DIMENSION; i++) new_node->vector[i] = vector[i];

    for (int l = 0; l < MAX_LEVELS; l++) {
        int max_links = (l == 0) ? M0 : M;
        new_node->neighbors[l] = (HNSWNode**)malloc(sizeof(HNSWNode*) * max_links);
        new_node->neighbor_counts[l] = 0;
    }

    if (!index->enter_node) {
        index->enter_node = new_node;
        index->max_level = new_node->level;
        return;
    }

    HNSWNode* curr_node = index->enter_node;
    // שלב א': ניווט מהיר למטה עד לשכבה העליונה של הצומת החדש
    for (int l = index->max_level; l > new_node->level; l--) {
        curr_node = search_layer(vector, curr_node, l);
    }

    // שלב ב': חיבור שכנים מהשכבה של הצומת החדש ומטה
    for (int l = (new_node->level < index->max_level ? new_node->level : index->max_level); l >= 0; l--) {
        curr_node = search_layer(vector, curr_node, l);
        
        int max_links = (l == 0) ? M0 : M;
        if (curr_node->neighbor_counts[l] < max_links) {
            curr_node->neighbors[l][curr_node->neighbor_counts[l]++] = new_node;
            new_node->neighbors[l][new_node->neighbor_counts[l]++] = curr_node;
        }
    }

    if (new_node->level > index->max_level) {
        index->max_level = new_node->level;
        index->enter_node = new_node;
    }
}