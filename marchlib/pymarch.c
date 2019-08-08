#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "march.h"

#define die_perror(msg)     \
do {                        \
    perror(msg);            \
    exit(1);                \
} while (0)

struct MarchVolume *mv = NULL;
//int data_fd = 0;

void initmarch(void);
void quit_march(void);
int load_stdin(int n_clouds, float resolution, const char *projection);
int load(int n_clouds, struct Cloud *data, float resolution,
        const char *projection);
void start(void);
void retrieve(void);

int main(int argc, char *argv[])
{
    /* Arg1: n_clouds   (int)
     * Arg2: resolution (float)
     * Arg3: projection (string)
     */
    int n_clouds = (int)strtol(argv[1], NULL, 10);
    float resolution = strtof(argv[2], NULL);
    const char *projection = argv[3];

    initmarch();

    fprintf(stderr, "Beginning load: write charge clouds to STDIN\n");
    load_stdin(n_clouds, resolution, projection);
    fprintf(stderr, "Loading complete, beginning sim\n");
    start();
    fprintf(stderr, "Simulation complete, writing matrix to STDOUT\n");
    retrieve();
    fprintf(stderr, "Write complete, exiting\n");

    quit_march();
    return 0;
}

void initmarch(void)
{
    mv = march_create();
}

void quit_march(void)
{
    march_destroy(mv);
}

int load_stdin(int n_clouds, float resolution, const char* projection)
{
    int PROJ = 0; /* TODO */
    struct Cloud *volumes = malloc(n_clouds * sizeof(struct Cloud));

    for (int i = 0; i < n_clouds; i++)
    {
        if (read(STDIN_FILENO, (void*)&volumes[i], sizeof(struct Cloud)) < 0)
        {
            die_perror("Charge data read failed");
        }
        volumes[i].volume.r *= 1e3f;
    }
    march_init(mv, volumes, n_clouds, resolution, PROJ);
    return 0;
}

void start(void)
{
    run_march(mv);
}

void retrieve(void)
{
    // Write dimensions of data to STDOUT
    if (write(STDOUT_FILENO, (void*)&mv->matrix_u, sizeof(int)) < 0)
        die_perror("Writing data dimensions (u) failed");
    if (write(STDOUT_FILENO, (void*)&mv->matrix_v, sizeof(int)) < 0)
        die_perror("Writing data dimensions (v) failed");

    // Write data matrix to STDOUT
    for (int u = 0; u < mv->matrix_u; u++)
    {
        for (int v = 0; v < mv->matrix_v; v++)
        {
            int retval = write(STDOUT_FILENO,
                    (void*)&mv->matrix[u + v*mv->matrix_u], sizeof(float));

            if (retval < 0)
                die_perror("Failure writing matrix data");

        }
    }
}
