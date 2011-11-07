#
#     Copyright 2011, Kay Hayen, mailto:kayhayen@gmx.de
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     If you submit Kay Hayen patches to this software in either form, you
#     automatically grant him a copyright assignment to the code, or in the
#     alternative a BSD license to the code, should your jurisdiction prevent
#     this. Obviously it won't affect code that comes to him indirectly or
#     code you don't submit to him.
#
#     This is to reserve my ability to re-license the code at any time, e.g.
#     the PSF. With this version of Nuitka, using it for Closed Source will
#     not be allowed.
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
"""SCons.Tool.Perforce.py

Tool-specific initialization for Perforce Source Code Management system.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

__revision__ = "src/engine/SCons/Tool/Perforce.py 5134 2010/08/16 23:02:40 bdeegan"

import os

import SCons.Action
import SCons.Builder
import SCons.Node.FS
import SCons.Util

# This function should maybe be moved to SCons.Util?
from SCons.Tool.PharLapCommon import addPathIfNotExists


# Variables that we want to import from the base OS environment.
_import_env = [ 'P4PORT', 'P4CLIENT', 'P4USER', 'USER', 'USERNAME', 'P4PASSWD',
                'P4CHARSET', 'P4LANGUAGE', 'SystemRoot' ]

PerforceAction = SCons.Action.Action('$P4COM', '$P4COMSTR')

def generate(env):
    """Add a Builder factory function and construction variables for
    Perforce to an Environment."""

    def PerforceFactory(env=env):
        """ """
        import SCons.Warnings as W
        W.warn(W.DeprecatedSourceCodeWarning, """The Perforce() factory is deprecated and there is no replacement.""")
        return SCons.Builder.Builder(action = PerforceAction, env = env)

    #setattr(env, 'Perforce', PerforceFactory)
    env.Perforce = PerforceFactory

    env['P4']      = 'p4'
    env['P4FLAGS'] = SCons.Util.CLVar('')
    env['P4COM']   = '$P4 $P4FLAGS sync $TARGET'
    try:
        environ = env['ENV']
    except KeyError:
        environ = {}
        env['ENV'] = environ

    # Perforce seems to use the PWD environment variable rather than
    # calling getcwd() for itself, which is odd.  If no PWD variable
    # is present, p4 WILL call getcwd, but this seems to cause problems
    # with good ol' Windows's tilde-mangling for long file names.
    environ['PWD'] = env.Dir('#').get_abspath()

    for var in _import_env:
        v = os.environ.get(var)
        if v:
            environ[var] = v

    if SCons.Util.can_read_reg:
        # If we can read the registry, add the path to Perforce to our environment.
        try:
            k=SCons.Util.RegOpenKeyEx(SCons.Util.hkey_mod.HKEY_LOCAL_MACHINE,
                                      'Software\\Perforce\\environment')
            val, tok = SCons.Util.RegQueryValueEx(k, 'P4INSTROOT')
            addPathIfNotExists(environ, 'PATH', val)
        except SCons.Util.RegError:
            # Can't detect where Perforce is, hope the user has it set in the
            # PATH.
            pass

def exists(env):
    return env.Detect('p4')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4: