#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "march.h"

struct MarchVolume *mv;

void initmarch(void)
{
    mv = march_create();
}

void quit_march(void)
{
    march_destroy(mv);
}

int load(int n_clouds, struct Cloud *data, float resolution,
        const char* projection)
{
    int PROJ = 0; /* TODO */

    /* Read job data from stdin */
    struct Cloud *volumes = malloc(n_vols * sizeof(struct Cloud));
    for (int i = 0; i < n_vols; i++)
    {
        //fread((void*)&volumes[i], sizeof(struct Cloud), 1, STDIN_FILENO);
        volumes[i] = data[i];
    }
    march_init(mv, volumes, n_vols, resolution, PROJ);
    return 0;
}

void start(void)
{
    run_march(mv);
}

void retrieve(void)
{
    int cells = mv->matrix_u * mv->matrix_v;
    for (int i = 0; i < cells; i++)
    {
        fwrite((void*)mv->matrix, sizeof(float), 1, STDOUT_FILENO);
    }
}
