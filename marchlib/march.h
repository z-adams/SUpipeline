#include <stdlib.h>

// PROJECTIONS

#define XY 0
#define YZ 1
#define ZX 2

#define USE_THREADING 1
#define NUM_THREADS 4

struct Vec3  /* total: 12 bytes */
{
    float x;    /* 4 bytes */
    float y;    /* 4 bytes */
    float z;    /* 4 bytes */
};

struct Sphere  /* total: 16 bytes */
{
    struct Vec3 origin;     /* 12 bytes */
    float r;                /* 4  bytes */
};

struct Cloud  /* total: 20 bytes */
{
    struct Sphere volume;   /* 16 bytes */
    float density;          /* 4  bytes */
};

struct Ray  /* total: 24 bytes */
{
    struct Vec3 origin;     /* 12 bytes */
    struct Vec3 direction;  /* 12 bytes */
};

struct __attribute__ ((__packed__)) MarchVolume  /* total: 84 bytes */
{
    struct Vec3 proj_direction;     /* 12 bytes */ /*12*/
    int n_vols;                     /* 4  bytes */
    struct Cloud *volumes;          /* 8  bytes */ /*12*/
    float *matrix;                  /* 8  bytes */
    float resolution;               /* 4  bytes */ /*12*/

    float x_min;                    /* 4  bytes */
    float x_max;                    /* 4  bytes */
    float y_min;                    /* 4  bytes */ /*12*/
    float y_max;                    /* 4  bytes */
    float z_min;                    /* 4  bytes */
    float z_max;                    /* 4  bytes */ /*12*/

    int matrix_u;                   /* 4  bytes */
    int matrix_v;                   /* 4  bytes */
    float u_cell_width;             /* 4  bytes */ /*12*/
    float v_cell_height;            /* 4  bytes */

    float w_img_plane;              /* 4  bytes */
    float w_depth_bound;            /* 4  bytes */ /*12*/
};

struct Subregion  /* 24 bytes */
{
    struct MarchVolume *mv; /* 8 bytes */
    int u0;                 /* 4 bytes */
    int v0;                 /* 4 bytes */
    int u1;                 /* 4 bytes */
    int v1;                 /* 4 bytes */
};

void ping(void);

float norm(struct Vec3 vec);

struct Vec3 unit_vec(struct Vec3 vec);

struct Vec3 scalar_mult(struct Vec3 vec, float scalar);

struct Vec3 vec_add(struct Vec3 u, struct Vec3 v);

struct Vec3 get_ray_point(struct Ray ray, float distance);

float sphere_SDF(struct Sphere sp, struct Vec3 point);

struct MarchVolume* march_create(void);

void march_destroy(struct MarchVolume *mv);

int march_init(struct MarchVolume *mv, struct Cloud *volumes, int n_vols,
        float resolution, int PROJECTION);

void delete_volume(struct MarchVolume *mv);

void run_march(struct MarchVolume *mv);

void* march_subvolume(void *args);

float march_ray(struct Ray cast, struct MarchVolume *mv);

float test_volumes(struct MarchVolume *mv, struct Vec3 point);
