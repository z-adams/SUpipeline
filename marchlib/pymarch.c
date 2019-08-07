#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "march.h"

struct MarchVolume *mv = NULL;
int data_fd = 0;

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
    data_fd = open("binary_clouds.hx", O_RDONLY);
}

void quit_march(void)
{
    march_destroy(mv);
    close(data_fd);
}

int load_stdin(int n_clouds, float resolution, const char* projection)
{
    int PROJ = 0; /* TODO */
    struct Cloud *volumes = malloc(n_clouds * sizeof(struct Cloud));
    int items_read = 0;

    //dup2(data_fd, STDIN_FILENO);

    for (int i = 0; i < n_clouds; i++)
    {
        items_read += read(data_fd, (void*)&volumes[i], sizeof(struct Cloud));
        volumes[i].volume.r *= 1e3f;
    }
    march_init(mv, volumes, n_clouds, resolution, PROJ);
    return 0;
}

int load(int n_clouds, struct Cloud *data, float resolution,
        const char* projection)
{
    int PROJ = 0; /* TODO */

    /* Read job data from stdin */
    struct Cloud *volumes = malloc(n_clouds * sizeof(struct Cloud));
    for (int i = 0; i < n_clouds; i++)
    {
        //fread((void*)&volumes[i], sizeof(struct Cloud), 1, STDIN_FILENO);
        volumes[i] = data[i];
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
    //int cells = mv->matrix_u * mv->matrix_v;
    //int output = open("output.hx", O_CREAT, S_IRWXU);
    //dup2(output, STDOUT_FILENO);
    FILE *fptr = fopen("output.txt", "w");
    for (int u = 0; u < mv->matrix_u; u++)
    {
        for (int v = 0; v < mv->matrix_v; v++)
        {
            //char c = (mv->matrix[u + v*mv->matrix_u] > 0.1f) ? '#' : '.';
            //printf("%f ", mv->matrix[u + v*mv->matrix_u]);
            float value = mv->matrix[u + v*mv->matrix_u];
            fprintf(fptr, "%f ", value);
        }
        fprintf(fptr, "\n");
    }
    //flush(output);


    //write(output, (void*)mv->matrix, cells * sizeof(float));
    /*
    for (int i = 0; i < cells; i++)
    {
        fwrite((void*)mv->matrix, sizeof(float), 1, stdout); //STDOUT_FILENO);
    }*/
}
