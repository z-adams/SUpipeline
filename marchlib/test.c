#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "march.h"

int main(void)
{
    printf("Vec3: %d\n", (int)sizeof(struct Vec3));
    printf("Sphere: %d\n", (int)sizeof(struct Sphere));
    printf("Cloud: %d\n", (int)sizeof(struct Cloud));
    printf("Ray: %d\n", (int)sizeof(struct Ray));
    printf("MarchVolume: %d\n", (int)sizeof(struct MarchVolume));
    printf("Subregion: %d\n", (int)sizeof(struct Subregion));

    struct MarchVolume *mv = march_create();
    struct MarchVolume mv2;
    memcpy(mv, &mv2, sizeof(struct MarchVolume));

    printf("Osets:\n");
    printf("p_d:%d\n", (int)offsetof(struct MarchVolume, proj_direction));
    printf("n:%d\n", (int)offsetof(struct MarchVolume, n_vols));
    printf("vols:%d\n", (int)offsetof(struct MarchVolume, volumes));
    printf("mat:%d\n", (int)offsetof(struct MarchVolume, matrix));
    printf("res:%d\n", (int)offsetof(struct MarchVolume, resolution));
    printf("xm:%d\n", (int)offsetof(struct MarchVolume, x_min));
    printf("xM:%d\n", (int)offsetof(struct MarchVolume, x_max));
    printf("ym:%d\n", (int)offsetof(struct MarchVolume, y_min));
    printf("yM:%d\n", (int)offsetof(struct MarchVolume, y_max));
    printf("zm:%d\n", (int)offsetof(struct MarchVolume, z_min));
    printf("zM:%d\n", (int)offsetof(struct MarchVolume, z_max));
    printf("mu:%d\n", (int)offsetof(struct MarchVolume, matrix_u));
    printf("mv:%d\n", (int)offsetof(struct MarchVolume, matrix_v));
    printf("uw:%d\n", (int)offsetof(struct MarchVolume, u_cell_width));
    printf("vh:%d\n", (int)offsetof(struct MarchVolume, v_cell_height));
    printf("wp:%d\n", (int)offsetof(struct MarchVolume, w_img_plane));
    printf("wb:%d\n", (int)offsetof(struct MarchVolume, w_depth_bound));
    return 0;
}
