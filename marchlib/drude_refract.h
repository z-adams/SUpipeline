#pragma once

#ifndef DRUDE_REF_H
#define DRUDE_REF_H

#include "march.h"

//void compute_n_dv(struct MarchVolume *mv, struct Vec3 point, int u, int v);

void drude_ref(struct MarchVolume *mv, struct Vec3 point, int u, int v);

#endif
