#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <pthread.h>
#include <assert.h>
#include <string.h>
#include "march.h"

void hello(void)
{
    printf("Hello, world!\n");
}

float norm(struct Vec3 vec)
{
    return sqrt(vec.x*vec.x + vec.y*vec.y + vec.z*vec.z);
}

struct Vec3 unit_vec(struct Vec3 vec)
{
    return scalar_mult(vec, 1.0f/norm(vec));
}

struct Vec3 scalar_mult(struct Vec3 vec, float scalar)
{
    struct Vec3 vect;
    vect.x = vec.x * scalar;
    vect.y = vec.y * scalar;
    vect.z = vec.z * scalar;
    return vect;
}

struct Vec3 vec_add(struct Vec3 u, struct Vec3 v)
{
    struct Vec3 vect;
    vect.x = u.x + v.x;
    vect.y = u.y + v.y;
    vect.z = u.z + v.z;
    return vect;
}

struct Vec3 get_ray_point(struct Ray ray, float distance)
{
    return vec_add(ray.origin, scalar_mult(unit_vec(ray.direction), distance));
}

float sphere_SDF(struct Sphere sp, struct Vec3 point)
{
    float x = sp.origin.x - point.x;
    float y = sp.origin.y - point.y;
    float z = sp.origin.z - point.z;
    return sqrt(x*x + y*y + z*z) - sp.r;
}

struct MarchVolume* march_create(void)
{
    struct MarchVolume *mv = malloc(sizeof(struct MarchVolume));
    memset(mv, 0xCC, sizeof(struct MarchVolume));
    *mv = (struct MarchVolume) {(struct Vec3) {0.0f, 0.0f, 0.0f}, 0, NULL,
        NULL, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0, 0, 0.0f, 0.0f,
        0.0f, 0.0f};
    return mv;
}

void march_destroy(struct MarchVolume *mv)
{
    free(mv->volumes);
    free(mv->matrix);
    free(mv);
}


int march_init(struct MarchVolume *mv, struct Cloud *volumes, int n_vols,
        float resolution, int PROJECTION)
{
    mv->volumes = volumes;
    mv->resolution = resolution;

    float r_max = 0.0f;

    struct Vec3 point;
    for (int i = 0; i < n_vols; i++)
    {
        point = volumes[i].volume.origin;
        if (point.x < mv->x_min)
            mv->x_min = point.x;
        if (point.x > mv->x_max)
            mv->x_max = point.x;
        if (point.y < mv->y_min)
            mv->y_min = point.y;
        if (point.y > mv->y_max)
            mv->y_max = point.y;
        if (point.z < mv->z_min)
            mv->z_min = point.z;
        if (point.z > mv->z_max)
            mv->z_max = point.z;

        if (volumes[i].volume.r > r_max)
            r_max = volumes[i].volume.r;
    }
    mv->x_max += r_max;
    mv->x_min -= r_max;
    mv->y_max += r_max;
    mv->y_min -= r_max;
    mv->z_max += r_max;
    mv->z_min -= r_max;

    float vol_width = 0.0f, vol_height = 0.0f;
    switch (PROJECTION)
    {
        case XY:
            vol_width = mv->x_max - mv->x_min;
            vol_height = mv->y_max - mv->y_min;
            break;
        case YZ:
            break;
        case ZX:
            break;
    }
    mv->matrix_u = (int)(vol_width / resolution);
    mv->matrix_v = (int)(vol_height / resolution);
    mv->u_cell_width = vol_width / mv->matrix_u;
    mv->v_cell_height = vol_height / mv->matrix_v;

    if (mv->matrix)
        free(mv->matrix);
    mv->matrix = malloc(sizeof(float) * mv->matrix_u * mv->matrix_v);
    if (!mv->matrix)
        return -1;
    return 0;
}

void run_march(struct MarchVolume *mv)
{
    if (!USE_THREADING)
    {
        // Run in main thread
        struct Subregion full;
        full.mv = mv;
        full.u0 = 0;
        full.v0 = 0;
        full.u1 = mv->matrix_u;
        full.v1 = mv->matrix_v;
        march_subvolume((void*)&full);
        return;
    }

    // Require NUM_THREADS to be a multiple of 2 for easy workload division
    assert(NUM_THREADS % 2 == 0);
    pthread_t pool[NUM_THREADS];

    // Find an intermediate divisor of NUM_THREADS to calculate grid meshing
    // We assert that NUM_THREADS is even above so NUM_THREADS % 2 is
    // guaranteed to produce a valid arrangement
    int cols = (int)sqrt(NUM_THREADS);
    for (; cols > 2; cols--)
    {
        if (NUM_THREADS % cols == 0)
            break;
    }
    int rows = NUM_THREADS / cols;

    // Compute the corners of the subregions and launch threads
    struct Subregion chunks[NUM_THREADS];
    for (int v = 0; v < rows; v++)
    {
        for (int u = 0; u < cols; u++)
        {
            struct Subregion *region = &chunks[u + cols*v];
            region->mv = mv;
            region->u0 = u;
            region->v1 = v;
            if (u == cols - 1)
                region->u1 = mv->matrix_u;
            else
                region->u1 = u + mv->matrix_u / cols;
            if (v == rows - 1)
                region->v1 = mv->matrix_v;
            else
                region->v1 = v + mv->matrix_v / rows;
            int result_code = pthread_create(&pool[u + cols*v], NULL,
                    march_subvolume, (void*)region);
            assert(!result_code);
        }
    }

    // Wait for threads to finish
    for (int i = 0; i < NUM_THREADS; i++)
    {
        int result_code = pthread_join(pool[i], NULL);
        assert(!result_code);
    }
}

void* march_subvolume(void *args)
    //struct MarchVolume *mv, int u0, int v0, int u1, int v1)
{
    struct Subregion *region = (struct Subregion*)args;
    struct MarchVolume *mv = region->mv;
    struct Ray cast;
    cast.direction = mv->proj_direction;
    cast.origin.z = mv->w_img_plane; // Generalize
    for (int u = region->u0; u < region->u1; u++)
    {
        for (int v = region->v0; v < region->v1; v++)
        {
            cast.origin.x = u*mv->u_cell_width;
            cast.origin.y = u*mv->v_cell_height;

            mv->matrix[u + v * mv->matrix_u] = march_ray(cast, mv);
        }
    }
    return NULL;
}

float march_ray(struct Ray cast, struct MarchVolume *mv)
{
    float value = 0.0f;
    float depth = 0.0f;
    while (depth < mv->w_depth_bound)
    {
        depth += mv->resolution;
        value += test_volumes(mv, get_ray_point(cast, depth));
    }
    return value;
}

float test_volumes(struct MarchVolume *mv, struct Vec3 point)
{
    float sum = 0.0f;
    for (int i = 0; i < mv->n_vols; i++)
    {
        if (sphere_SDF(mv->volumes[i].volume, point) < 0.0f)
        {
            sum += mv->volumes[i].density;
        }
    }
    return sum;
}

