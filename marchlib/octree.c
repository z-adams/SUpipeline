#include "octree.h"
#include "vec3.h"

/*  Octant naming standards are as follows:
    index   signature (x,y,z)
    0       (+ + +)
    1       (- + +)
    2       (- - +)
    3       (+ - +)
    4       (+ + -)
    5       (- + -)
    6       (- - -)
    7       (+ - -)
*/

struct List
{
    int *data;
    int capacity;
    int size;
};

typedef struct List* list_t;

struct OctNode
{
    struct *OctNode children[8];    /*64 bytes*/
    struct Vec3 center;             /*12 bytes*/
    int *data;                      /*8  bytes*/
    float x_width;                  /*4  bytes*/
    float y_width;                  /*4  bytes*/
    float z_width;                  /*4  bytes*/
};

typedef struct OctNode* node_t;

struct Octree
{
    node_t *HEAD;
};

list_t list_create(void)
{
    list_t list = malloc(sizeof(struct List));
    list->data = NULL;
    list
}

octree_t octree_create(void)
{
    octree_t oct = malloc(sizeof(struct Octree));
    if (!oct)
        return NULL;
    oct->HEAD = NULL;
    return oct;
}

node_t node_create(struct Vec3 center, float x_w, float y_w, float z_w)
{
    node_t node = malloc(sizeof(struct OctNode));
    if (!node)
        return NULL;
    for (int i = 0; i < 8; i++)
        node->children[i] = NULL;
    node->data = NULL;
    node->center = center;
    node->x_width = x_w;
    node->y_width = y_w;
    node->z_width = z_w;
    return node;
}

void node_insert_data(node_t node, int data)
{
    if (!node->data)
    {
        node->data = malloc(DATA_CAP*sizeof(int));
        for (int i = 0; i < DATA_CAP; i++)
            node->data[i] = -1;
    }
    for (int i = 0; i < 
}

void octree_destroy(octree_t o)
{
    free(o);
}

int get_octant(node_t node, struct Vec3 test)
{
    if (test.x > node->center.x)
        if (test.y > node->center.y)
            if (test.z > node->center.z)
                return 0;
            else
                return 4;
        else
            if (test.z > node->center.z)
                return 3;
            else
                return 7;
    else
        if (test.y > node->center.y)
            if (test.z > node->center.z)
                return 1;
            else
                return 5;
        else
            if (test.z > node->center.z)
                return 2;
            else
                return 6;
}

void octree_insert(octree_t oct, struct Vec3 pos, int index)
{
    int octant = get_octant(oct->HEAD, pos);

}

void octree_search(octree_t oct, struct Vec3 pos, int **indices, int n_results)
{
    
}
