#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "march.h"

struct MarchVolume *mv;

static PyMethodDef MarchMethods[] = {
    {"load", load, METH_VARARGS, "Read charge cloud data from STDIN"},
    {"start", start, METH_VARARGS,
        "Perform volume integration of charge density"},
    {"retrieve", retrieve, METH_VARARGS, "Write results to STDOUT"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initmarch(void)
{
    (void) Py_InitModule("march", MarchMethods);
    mv = march_create();
    Py_AtExit(quit_march);
}

void quit_march(void)
{
    march_destroy(mv);
}

static PyObject* load(PyObject *self, PyObject *task)
{
    /* Parse march job spec */
    PyObject *container = NULL;
    if (!PyArg_ParseTuple(task, "O", &container))
    {
        PyErr_SetString(PyExc_RuntimeError, "Bad argument");
        return NULL;
    }

    /* Parse member data from job spec */
    PyObject *n_clouds = PyObject_GetAttr(container, "num_clouds");
    PyObject *res = PyObject_GetAttr(container, "resolution");
    PyObject *proj = PyObject_GetAttr(container, "projection");
    int n_vols = 0;
    float resolution = 0.0f;
    const char *projection = NULL;
    if (!PyArg_ParseTuple(n_clouds, "i", &n_vols))
    {
        PyErr_SetString(PyExc_RuntimeError, "Bad num_clouds");
        return NULL;
    }
    if (!PyArg_ParseTuple(res, "f", &resolution))
    {
        PyErr_SetString(PyExc_RuntimeError, "Bad resolution");
        return NULL;
    }
    if (!PyArg_ParseTuple(proj, "s", &projection))
    {
        PyErr_SetString(PyExc_RuntimeError, "Bad projection");
        return NULL;
    }

    int PROJ = 0; /* TODO */

    /* Read job data from stdin */
    struct Cloud *volumes = malloc(n_vols * sizeof(struct Cloud));
    if (!volumes)
    {
        PyErr_SetString(PyExc_RuntimeError, "Malloc failed");
        return NULL;
    }
    for (int i = 0; i < n_vols; i++)
    {
        fread((void*)&volumes[i], sizeof(struct Cloud), 1, STDIN_FILENO);
    }
    march_init(mv, volumes, n_vols, resolution, PROJ);
    return Py_None;
}

static PyObject* start(PyObject *self, PyObject *args)
{
    run_march(mv);
    return Py_None;
}

static PyObject* retrieve(PyObject *self)
{
    int cells = mv->matrix_u * mv->matrix_v;
    for (int i = 0; i < cells; i++)
    {
        fwrite((void*)mv->matrix, sizeof(float), 1, STDOUT_FILENO);
    }
    return Py_None;
}
