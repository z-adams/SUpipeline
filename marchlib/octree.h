#pragma once

#ifndef OCTREE_H
#define OCTREE_H

#define DATA_CAP 10  // Maximum elements allowed per "leaf"

typedef struct Octree* octree_t;

octree_t octree_create(void);

void octree_destroy(octree_t o);

void octree_insert(octree_t oct, struct Vec3 pos, int index);

void octree_search(octree_t oct, struct Vec3 pos, int **indices, int n_results);

#endif
