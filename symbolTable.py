#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# symbolTable.py : 04oct2013 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2013, Clinton Prentiss Mah
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
saved grammar rule symbols for syntactic analysis
plus associated lookup methods

(may be referenced at run-time for Elly error messages)
"""

import ellyBits
import grammarTable

class SymbolTable(object):

    """
    tables of grammatical symbol names for relating different rules

    attributes:
        ntindx - syntactic type lookup
        ntname - syntactic type names
        fsindx - syntactic and semantic feature set names
    """

    def __init__ ( self ):

        """
        initialize

        arguments:
            self
        """

        self.ntindx = { } # start with everything empty
        self.ntname = [ ] #
        self.fsindx = { } #

    def getFeatureSet ( self , fs ):

        """
        get feature index associated with given name in given set

        arguments:
            self  -
            fs    - feature set without enclosing brackets

        returns:
            list of EllyBits - [ positive , negative ]
        """

        fid = fs[0]                # feature set ID
        fnm = fs[1:].split(',')    # feature names
        if not fid in self.fsindx: # known ID?
            self.fsindx[fid] = { } # if not, make it known
        h = self.fsindx[fid]       # for hashing of feature names
        bp = ellyBits.EllyBits(grammarTable.FMAX)
        bn = ellyBits.EllyBits(grammarTable.FMAX)
        for nm in fnm:
            nm = nm.strip()
            if nm[0] == '-':       # negative feature?
                b = bn             # if so, look at negative bits
                nm = nm[1:]
            elif nm[0] == '+':     # positive feature?
                b = bp             # if so, look at positive bits
                nm = nm[1:]
            else:
                b = bp             # positive bits by default

            if not nm in h:        # new name in feature set?
                k = len(h)         # if so, define it
                h[nm] = k

            b.set(h[nm])           # set bit for feature
        return [ bp , bn ]

    def getSyntaxTypeIndexNumber ( self , s ):

        """
        get index number for a syntax type name, defining it if necessary

        arguments:
            self  -
            s     - name

        returns:
            type index index number
        """

        if s in self.ntindx:
            return self.ntindx[s]
        else:
            n = len(self.ntindx)
            self.ntindx[s] = n
            self.ntname.append(s)
            return n

    def getSyntaxTypeName ( self , n ):

        """
        get a syntax type name from its index number

        arguments:
            self  -
            n     - index number

        returns:
            type name as string on success, '' on failure
        """

        if n < len(self.ntname):
            return self.ntname[n]
        else:
            return ''

    def getSyntaxTypeCount ( self ):

        """
        get number of syntax types defined

        arguments:
            self

        returns:
            integer count
        """

        return len(self.ntindx)
