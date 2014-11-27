#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# derivabilityMatrix.py : 04nov2014 CPM
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
bit encoding of derivability relationships between syntax types
"""

import ellyBits

class DerivabilityMatrix(object):

    """
    binary transitive closure matrix for derivability of syntax types

    attributes:
        dm   - row matrix
    """
 
    def __init__ ( self , nmax ):

        """
        initialization

        arguments:
            self  -
            nmax  - how many syntactic types to encode
        """

        self.dm = [ ]                    # empty matrix initially
        for i in range(nmax):
            rw = ellyBits.EllyBits(nmax) # get bit string
            rw.set(i)                    # diagonalize matrix by row
            self.dm.append(rw)           # and save

    def derivable ( self , n , gbs ):

        """
        check whether any specified bits are on in specified matrix row

        arguments:
            self  -
            n     - which row, corresponding to syntactic type
            gbs   - goal bits to check

        returns:
            True if specified bit is on, False otherwise
        """

        return self.dm[n].intersect(gbs)

    def join ( self , left , rght ):

        """
        update derivability with information that left->rght or left-> rght x

        arguments:
            self  -
            left  - syntax type derivable from left  of rule
            rght  - syntax type derived   from right of rule
        """

        if self.dm[rght].test(left):   # derivability already known?
            return                     # if so, done
        rw = self.dm[left]             # otherwise, get transitive closure of derivability
        lm = len(self.dm)              # row count for matrix
        for i in range(lm):            # next row for next syntactic type
            if self.dm[i].test(rght):  # is right derivable for this type?
                self.dm[i].combine(rw) # if so, then everything for left is also derivable

    def row ( self , n ):

        """
        get row of matrix

        arguments:
            self  -
            n     - row index, corresponding to syntactic type

        returns:
            specified row as EllyBits
        """

        return self.dm[n]

#
# unit test
#

if __name__ == '__main__':

    def dump ( m ):
        """ to show bits in matrix for testing
        """
        print 0 , m.dm[0].hexadecimal()
        print 1 , m.dm[1].hexadecimal()
        print 2 , m.dm[2].hexadecimal()
        print 3 , m.dm[3].hexadecimal()
        print 4 , m.dm[4].hexadecimal()
        print 5 , m.dm[5].hexadecimal()
        print ""

    mtx = DerivabilityMatrix(24)
    print mtx
    dump(mtx)
    mtx.join(0,1)
    dump(mtx)
    mtx.join(2,3)
    dump(mtx)
    mtx.join(1,2)
    dump(mtx)
    mtx.join(3,4)
    dump(mtx)
    mtx.join(4,5)
    dump(mtx)
