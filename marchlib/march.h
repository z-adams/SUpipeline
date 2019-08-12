#pragma once

#ifndef MARCH_H
#define MARCH_H

// PROJECTIONS

#define XY 0
#define YZ 1
#define ZX 2

/** Use multithreading: 1 = Yes, 0 = No */
#define USE_THREADING 1

/** Number of threads to use (integer multiple of 2 please) */
#define NUM_THREADS 4

/** Basic cartesian vector in R3*/
struct Vec3  /* total: 12 bytes */
{
    float x;    /* 4 bytes */
    float y;    /* 4 bytes */
    float z;    /* 4 bytes */
};

/** Spherical volume defined by its position and radius */
struct Sphere  /* total: 16 bytes */
{
    struct Vec3 origin;     /* 12 bytes */
    float r;                /* 4  bytes */
};

/** A charge cloud defined by its spherical volume and charge density */
struct Cloud  /* total: 20 bytes */
{
    struct Sphere volume;   /* 16 bytes */
    float density;          /* 4  bytes */
};

/** A geometric ray defined by an origin point and a direction vector */
struct Ray  /* total: 24 bytes */
{
    struct Vec3 origin;     /* 12 bytes */
    struct Vec3 direction;  /* 12 bytes */
};

struct MarchVolume;

/** "Evaluator" function used as the integrand when performing march
 * The client program passes a function to the ray marcher, allowing
 * for generalization of output
 */
typedef void (*Evaluator)(struct MarchVolume *mv, struct Vec3 point,
        int u, int v);

/** Contains the information necessary to perform volume integration
 * The system stores a list of volumetric information (volumes) which are then
 * integrated over using marching rays. The results are written to a matrix of
 * values. Upon initialization, the user passes an "evaluator" function and
 * information about the matrix data, allowing the system to be agnostic to the
 * results format and allow easy swapping of models for calculating the results.
 */
struct MarchVolume  /* total: 96 bytes */
{
    struct Vec3 proj_direction;     /* 12 bytes */ /*12*/
    int n_vols;                     /* 4  bytes */
    struct Cloud *volumes;          /* 8  bytes */ /*12*/
    int matrix_element_size;        /* 4  bytes */
    //struct Values *matrix;          /* 8  bytes */
    void *matrix;                   /* 8  bytes */
    /*void (*evaluate)(
            struct MarchVolume *mv,
            struct Vec3 point,
            int u, int v);          * 8  bytes */
    Evaluator evaluate;             /*8  bytes */
    float resolution;               /* 4  bytes */

    float x_min;                    /* 4  bytes */ /*24*/
    float x_max;                    /* 4  bytes */
    float y_min;                    /* 4  bytes */
    float y_max;                    /* 4  bytes */ /*12*/
    float z_min;                    /* 4  bytes */
    float z_max;                    /* 4  bytes */

    int matrix_u;                   /* 4  bytes */ /*12*/
    int matrix_v;                   /* 4  bytes */
    float u_cell_width;             /* 4  bytes */
    float v_cell_height;            /* 4  bytes */ /*12*/

    float w_img_plane;              /* 4  bytes */
    float w_depth_bound;            /* 4  bytes */
    char pad[4];                    /* 4  bytes */ /*12*/
};

/** Used to facilitate multithreading
 * A subregion contains a pointer to the MarchVolume object of interest as well
 * as the corners of the rectangle of matrix elements that the thread is
 * responsible for computing.
 */
struct Subregion  /* 24 bytes */
{
    struct MarchVolume *mv; /* 8 bytes */
    int u0;                 /* 4 bytes */
    int v0;                 /* 4 bytes */
    int u1;                 /* 4 bytes */
    int v1;                 /* 4 bytes */
};

/** Prints "hello world", for testing python integration */
void ping(void);

/**
 * norm - Compute the norm (magnitude) of a vector
 * @vec: the vector
 *
 * Return: The length of @vec
 */
float norm(struct Vec3 vec);

/**
 * unit_vec - Compute a unit vector in the direction of vec
 * @vec: the (un-normalized) vector
 *
 * Return: a vector with length 1 in the direction of @vec
 */
struct Vec3 unit_vec(struct Vec3 vec);

/**
 * scalar_mult - Multiply a vector by a scalar float
 * @vec: the vector to multiply
 * @scalar: the scalar to multiply it by
 *
 * Return: the new resulting vector
 */
struct Vec3 scalar_mult(struct Vec3 vec, float scalar);

/**
 * vec_add - Perform vector addition
 * @u, v: the vectors to add
 *
 * Return: the resultant vector
 */
struct Vec3 vec_add(struct Vec3 u, struct Vec3 v);

/**
 * get_ray_point - Compute a point some distance along a ray
 * @ray: the ray along which to find the point
 * @distance: the distance along the ray from its origin
 *
 * Return: a vector describing the point in space
 */
struct Vec3 get_ray_point(struct Ray ray, float distance);

/**
 * sphere_SDF - Calculate the Signed Distance Function of a sphere
 * @sp: the sphere in question
 * @point: the point in question
 *
 * The Signed Distance Function returns the distance from the surface of an
 * object and is used to calculate whether or not a point lies inside or outside
 * a volume, usually a primitive like a sphere or cube.
 * 
 * Return: The distance from the surface of @sp; < 0.0f if @point is outside
 * @sp, else > 0.0f
 */
float sphere_SDF(struct Sphere sp, struct Vec3 point);

/**
 * march_create - Allocates and zero-initializes a MarchVolume object
 * 
 * Return: a new MarchVolume object, or NULL if alloc failure
 */
struct MarchVolume* march_create(void);

/**
 * march_destroy - Deallocates a MarchVolume object
 *
 * Return: 0 on success, -1 if mv was invalid
 */
int march_destroy(struct MarchVolume *mv);

/**
 * march_init - Initialize a MarchVolume object
 * @mv: an allocated MarchVolume object
 * @volumes: a list of charge clouds (initial dataset)
 * @n_vols: the number of charge clouds
 * @resolution: the step size (in centimeters)
 * @PROJECTION: int desribing projection direction
 * @eval: an evaluator function, the integrand of the marching (see defn above)
 * @mat_cell_bytes: number of bytes per matrix element
 *
 * Initializes a MarchVolume. Takes the matrix format and evaluator function,
 * computes limits of integration and allocates matrix to be filled in by
 * @eval at runtime
 *
 * Return: 0 on success, -1 on failure to allocate matrix
 */
int march_init(struct MarchVolume *mv, struct Cloud *volumes, int n_vols,
        float resolution, int PROJECTION, Evaluator eval, int mat_cell_bytes);

/**
 * run_march - Perform ray marching on @mv
 * @mv: the MarchVolume object specifying the job properties
 *
 * Return: 0 on success, -1 if mv is not properly initialized
 */
int run_march(struct MarchVolume *mv);

/**
 * march_subvolume - Performs image-plane iteration, called to execute march
 * @args: (void arg for pthreading) - a Subregion object
 *
 * Return: NULL
 */
void* march_subvolume(void *args);

/**
 * march_ray - Perform depth iteration for computing single matrix element
 * @cast: the ray to project through the volume
 * @mv: the volume information
 * @u, v: the coordinates of the associated matrix element
 */
void march_ray(struct Ray cast, struct MarchVolume *mv, int u, int v);

/**
 * test_volumes - Basic evaluator function
 * Simply computes the charge density
 */
void test_volumes(struct MarchVolume *mv, struct Vec3 point, int u, int v);

#endif /* MARCH_H */
