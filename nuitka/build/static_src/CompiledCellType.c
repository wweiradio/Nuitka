//     Copyright 2016, Kay Hayen, mailto:kay.hayen@gmail.com
//
//     Part of "Nuitka", an optimizing Python compiler that is compatible and
//     integrates with CPython, but also works on its own.
//
//     Licensed under the Apache License, Version 2.0 (the "License");
//     you may not use this file except in compliance with the License.
//     You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//     Unless required by applicable law or agreed to in writing, software
//     distributed under the License is distributed on an "AS IS" BASIS,
//     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//     See the License for the specific language governing permissions and
//     limitations under the License.
//

#include "nuitka/prelude.h"

#define NUITKA_CELL_FREE_LIST 1
#define MAX_CELL_FREE_LIST_COUNT 1000

#if NUITKA_CELL_FREE_LIST
static struct Nuitka_CellObject *free_list = NULL;
static int free_list_count = 0;
#endif

static void Nuitka_Cell_tp_dealloc( struct Nuitka_CellObject *cell )
{
    Nuitka_GC_UnTrack( cell );
    Py_XDECREF( cell->ob_ref );

    /* We abuse ob_ref for making a list of them. */
#if NUITKA_CELL_FREE_LIST
    if ( free_list != NULL )
    {
        if ( free_list_count > MAX_CELL_FREE_LIST_COUNT )
        {
            PyObject_GC_Del( cell );
        }
        else
        {
            cell->ob_ref = (PyObject *)free_list;
            free_list = cell;

            free_list_count += 1;
        }
    }
    else
    {
        free_list = cell;
        cell->ob_ref = NULL;

        assert( free_list_count == 0 );

        free_list_count += 1;
    }
#else
    PyObject_GC_Del( cell );
#endif
}

#if PYTHON_VERSION < 300
static int Nuitka_Cell_tp_compare( struct Nuitka_CellObject *cell_a, struct Nuitka_CellObject *cell_b )
{
    /* Empty cells compare specifically different. */
    if ( cell_a->ob_ref == NULL )
    {
        if ( cell_b->ob_ref == NULL )
        {
            return 0;
        }

        return -1;
    }

    if ( cell_b->ob_ref == NULL )
    {
        return 1;
    }

    return PyObject_Compare( cell_a->ob_ref, cell_b->ob_ref );
}
#else
static PyObject *Nuitka_Cell_tp_richcompare( PyObject *a, PyObject *b, int op)
{
    PyObject *result;

    CHECK_OBJECT( a );
    CHECK_OBJECT( b );

    if (unlikely( !Nuitka_Cell_Check(a) || !Nuitka_Cell_Check( b ) ))
    {
        result = Py_NotImplemented;
        Py_INCREF( result );

        return result;
    }


    /* Now just dereference, and compare from there by contents. */
    a = ((struct Nuitka_CellObject *)a)->ob_ref;
    b = ((struct Nuitka_CellObject *)b)->ob_ref;

    if (a != NULL && b != NULL)
    {
        return PyObject_RichCompare( a, b, op );
    }

    int res = (b == NULL) - (a == NULL);
    switch (op)
    {
        case Py_EQ:
            result = BOOL_FROM( res == 0 );
            break;
        case Py_NE:
            result = BOOL_FROM( res != 0 );
            break;
        case Py_LE:
            result = BOOL_FROM( res <= 0 );
            break;
        case Py_GE:
            result = BOOL_FROM( res >= 0 );
            break;
        case Py_LT:
            result = BOOL_FROM( res < 0 );
            break;
        case Py_GT:
            result = BOOL_FROM( res > 0 );
            break;
        default:
            PyErr_BadArgument();
            return NULL;
    }

    Py_INCREF( result );
    return result;
}


#endif

static PyObject *Nuitka_Cell_tp_repr( struct Nuitka_CellObject *cell )
{
    if ( cell->ob_ref == NULL )
    {
#if PYTHON_VERSION < 300
        return PyString_FromFormat(
#else
        return PyUnicode_FromFormat(
#endif
            "<compiled_cell at %p: empty>",
            cell
        );
    }
    else
    {
#if PYTHON_VERSION < 300
        return PyString_FromFormat(
#else
        return PyUnicode_FromFormat(
#endif
            "<compiled_cell at %p: %s object at %p>",
            cell,
            cell->ob_ref->ob_type->tp_name,
            cell->ob_ref
        );
     }
}

static int Nuitka_Cell_tp_traverse( struct Nuitka_CellObject *cell, visitproc visit, void *arg )
{
    Py_VISIT( cell->ob_ref );

    return 0;
}

static int Nuitka_Cell_tp_clear( struct Nuitka_CellObject *cell )
{
    Py_CLEAR( cell->ob_ref );

    return 0;
}

static PyObject *Nuitka_Cell_get_contents( struct Nuitka_CellObject *cell, void *closure )
{
    if ( cell->ob_ref == NULL )
    {
        PyErr_SetString( PyExc_ValueError, "Cell is empty" );
        return NULL;
    }

    Py_INCREF( cell->ob_ref );
    return cell->ob_ref;
}

static PyGetSetDef Nuitka_Cell_getsetlist[] =
{
    { (char *)"cell_contents", (getter)Nuitka_Cell_get_contents, NULL, NULL },

    { NULL }
};

PyTypeObject Nuitka_Cell_Type =
{
    PyVarObject_HEAD_INIT(NULL , 0)
    "compiled_cell",
    sizeof(struct Nuitka_CellObject),
    0,
    (destructor)Nuitka_Cell_tp_dealloc,         /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
#if PYTHON_VERSION < 300
    (cmpfunc)Nuitka_Cell_tp_compare,            /* tp_compare */
#else
    0,                                          /* tp_reserved */
#endif
    (reprfunc)Nuitka_Cell_tp_repr,              /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    (traverseproc)Nuitka_Cell_tp_traverse,      /* tp_traverse */
    (inquiry)Nuitka_Cell_tp_clear,              /* tp_clear */
#if PYTHON_VERSION < 300
    0,                                          /* tp_richcompare */
#else
    Nuitka_Cell_tp_richcompare,                 /* tp_richcompare */
#endif
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    Nuitka_Cell_getsetlist,                     /* tp_getset */
};

void _initCompiledCellType( void )
{
    PyType_Ready( &Nuitka_Cell_Type );
}

struct Nuitka_CellObject *Nuitka_Cell_New( void )
{
    struct Nuitka_CellObject *result;

#if NUITKA_CELL_FREE_LIST
    if ( free_list != NULL )
    {
        result = free_list;
        free_list = (struct Nuitka_CellObject *)free_list->ob_ref;
        free_list_count -= 1;
        assert( free_list_count >= 0 );

        _Py_NewReference( (PyObject *)result );
    }
    else
#endif
    {
        result = (struct Nuitka_CellObject *)PyObject_GC_New(
            struct Nuitka_CellObject,
            &Nuitka_Cell_Type
        );
    }

    assert( result != NULL );

    Nuitka_GC_Track( result );

    return result;
}

void Nuitka_Cells_New( struct Nuitka_CellObject **closure, int count )
{
    assert( count > 0 );

    while( count > 0 )
    {
        *closure = Nuitka_Cell_New();
        closure += 1;
        count -= 1;
    }
}
