#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyPickle.py : 30sep2017 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2015, Clinton Prentiss Mah
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

"""
serialization of Elly objects for grammar rule set
"""

import pickle

def save ( ob , nm ):

    """
    save an Elly object

    arguments:
        ob  - the object
        nm  - destination file name

    returns:
        True on success, False otherwise
    """

    try:
        outs = open(nm,'wb')
        pickle.dump(ob,outs)
        outs.close()
        return True
    except IOError:
        return False

def load ( nm ):

    """
    load an Elly object

    arguments:
        nm  - source file name

    returns:
        unpickled PyElly object on success, None on failure
    """

    try:
        ins = open(nm,'rb')
        ob = pickle.load(ins)
        ins.close()
        return ob
    except IOError:
        return None

