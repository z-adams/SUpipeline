#include "drude_refract.h"
#include "march.h"
#include <math.h>

#define eps_0 8.85e-12          // Vacuum permittivity (F/m)
#define eps_m (16.8 * eps_0)    // CdTe permittivity
#define n_m sqrt(eps_m/eps_0)   // CdTe refractive index
#define e 1.60217662e-19        // electron charge (C)
#define lambda 1.5e-6           // Target wavelength (m)
#define c 3e8
#define w (2*M_PI*c/lambda)     // Angular velocity
#define mee 0.11                // Rel. electron eff. mass
#define mhh 0.76                // Rel. hole eff. mass
#define m0 9.109e-31            // Electron rest mass (kg)
#define me (mee*m0)             // Electron eff. mass
#define mh (mhh*m0)             // Hole eff. mass
#define ue 1100e-4              // Electron mobility (m^2 / V*s)
#define uh 100e-4               // Hole mobility (m^2 / V*s)

struct Values
{
    float refract;
    float absorption;
};

double sq(double arg)
{
    return arg * arg;
}

double cu(double arg)
{
    return arg * arg * arg;
}

float mean(float *data, int n)
{
    float sum = 0.0f;
    for (int i = 0; i < n; i++)
    {
        sum += data[i];
    }
    return sum / n;
}

/**
 *
delt_n = -(e^2 lamb^2 / 8 pi^2 c^2 E0 n) * (delt_Ne/M_ce + delt_Nh/M_ch)
delt_a = -(e^3 lamb^3 / 4 pi^2 c^3 E0 n)
            * (delt_Ne/M_cd^2 mu_e + delt_Nh/M_cd^2 mu_h)
 */
void drude_ref(struct MarchVolume *mv, struct Vec3 point, int u, int v)
{
    float sdf = 0.0f;
    for (int i = 0; i < mv->n_vols; i++)
    {
        sdf = sphere_SDF(mv->volumes[i].volume, point);
        if (sdf < 0.0f)
        {
            struct Values* val =
                &((struct Values*)mv->matrix)[u + v * mv->matrix_u];
            double drude_n = mv->volumes[i].density;
            double drude_p = 0.0f;

            double c2 = c*c;
            double c3 = c*c*c;
            double pi2 = M_PI*M_PI;

            /*
            double denom = 4*sq(M_PI)*cu(c)*eps_0*n_m;
            double numer = -(sq(e) * sq(lambda));
            double mlpcd = (drude_n/me + drude_p/mh);
            //float refraction_diff = -(sq(e) * sq(lambda)) / (2*denom) *
            //    (drude_n/me + drude_p/mh);*/
            double refract_diff = -(sq(e*lambda)/(8*pi2*c2*eps_0*n_m))
                    * (drude_n/me + drude_p/mh);
            //double refraction_diff = numer / (2*denom) * mlpcd;
            double abs_coeff = -(cu(e*lambda)/4*pi2*c3*eps_0*n_m)
                    * (drude_n/(sq(me) * ue) + drude_p/(sq(mh) * uh));
            /*double abs_coeff = -((cu(e) * sq(lambda)) / denom) * 
                (drude_n/sq(me)/ue + drude_p/sq(mh)/uh) * 1e-2;  // to cm^-1*/
            val->refract += refract_diff;
            val->absorption += abs_coeff;
        }
    }
}
/*
void compute_n_dV(struct MarchVolume *mv, struct Vec3 point, int u, int v)
{
    //int n;
    //float drude_n = mean(data, n) * 1e6;
    //float drude_p = mean(data, n) * 1e6;
    float drude_n = n;
    float drude_p = p;
    float denom = 4*sq(M_PI)*cu(c)*eps_0*n_m;
    float refraction_diff = -(sq(e_q) * sq(lambda)) / (2*denom) *
        (drude_n/me + drude_p/mh);
    float abs_coeff = -((cu(e_q) * sq(lambda)) / denom) * 
        (drude_n/sq(me)/ue + drude_p/sq(mh)/uh) * 1e-2;  // to cm^-1
}*/
