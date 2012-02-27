#     Copyright 2012, Kay Hayen, mailto:kayhayen@gmx.de
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     If you submit patches or make the software available to licensors of
#     this software in either form, you automatically them grant them a
#     license for your part of the code under "Apache License 2.0" unless you
#     choose to remove this notice.
#
#     Kay Hayen uses the right to license his code under only GPL version 3,
#     to discourage a fork of Nuitka before it is "finished". He will later
#     make a new "Nuitka" release fully under "Apache License 2.0".
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, version 3 of the License.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#     Please leave the whole of this copyright notice intact.
#
""" Python operator tables

These are mostly used to resolve the operator in the module operator and to know the list
of operations allowed.

"""

from .Utils import getPythonVersion

import operator

if getPythonVersion() >= 300:
    operator.div = operator.truediv
    operator.idiv = operator.itruediv

binary_operator_functions = {
    "Add"       : operator.add,
    "Sub"       : operator.sub,
    "Pow"       : operator.pow,
    "Mult"      : operator.mul,
    "Div"       : operator.div,
    "FloorDiv"  : operator.floordiv,
    "TrueDiv"   : operator.truediv,
    "Mod"       : operator.mod,
    "LShift"    : operator.lshift,
    "RShift"    : operator.rshift,
    "BitAnd"    : operator.and_,
    "BitOr"     : operator.or_,
    "BitXor"    : operator.xor,
    "IAdd"      : operator.iadd,
    "ISub"      : operator.isub,
    "IPow"      : operator.ipow,
    "IMult"     : operator.imul,
    "IDiv"      : operator.idiv,
    "IFloorDiv" : operator.ifloordiv,
    "ITrueDiv"  : operator.itruediv,
    "IMod"      : operator.imod,
    "ILShift"   : operator.ilshift,
    "IRShift"   : operator.irshift,
    "IBitAnd"   : operator.iand,
    "IBitOr"    : operator.ior,
    "IBitXor"   : operator.ixor,
}

unary_operator_functions = {
    "UAdd"   : operator.pos,
    "USub"   : operator.neg,
    "Invert" : operator.invert,
    "Repr"   : repr,
    # Boolean not is treated an unary operator.
    "Not"    : operator.not_,
}


rich_comparison_functions = {
    "Lt"    : operator.lt,
    "LtE"   : operator.le,
    "Eq"    : operator.eq,
    "NotEq" : operator.ne,
    "Gt"    : operator.gt,
    "GtE"   : operator.ge
}

other_comparison_functions = {
    "Is"    : operator.is_,
    "IsNot" : operator.is_not,
    "In"    : lambda value1, value2: value1 in value2,
    "NotIn" : lambda value1, value2: value1 not in value2
}


all_comparison_functions = dict( rich_comparison_functions)
all_comparison_functions.update( other_comparison_functions )
