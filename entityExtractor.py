#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# entityExtractor.py : 21may2017 CPM
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
runs extraction methods and generates phrases
"""

import ellyBits
import ellyChar
import ellyConfiguration
import syntaxSpecification
import featureSpecification

noBits = ellyBits.EllyBits()

class EntityExtractor(object):

    """
    handler for information extraction (IE)

    attributes:
        ptr   - parse tree for extracted information
        sym   - saved symbol table
        exs   - extraction procedure list
    """

    def __init__ ( self , ptr , sym ):

        """
        initialization

        arguments:
            self  -
            ptr   - parse tree
            sym   - symbol table

        exceptions:
            FormatFailure on error
        """

        self.ptr = ptr
        self.sym = sym
        self.exs = [ ]
        for x in ellyConfiguration.extractors:
            proc = x[0]
            synt = syntaxSpecification.SyntaxSpecification(sym,x[1].lower())
            entry = [ proc , synt.catg , synt.synf.positive ]
            if len(x) > 2:
                f = None if x[2] == '-' else x[2].lower()
                smnt = featureSpecification.FeatureSpecification(sym,f,True)
                entry.append(smnt.positive)
            if len(x) > 3:
                entry.append(x[3])
            self.exs.append(entry)

    def dump ( self ):

        """
        show defined extractors

        arguments:
            self
        """
        for ex in self.exs:
            print ex[0] ,
            print  'syntax cat=' , self.sym.getSyntaxTypeName(ex[1]).upper() ,
            print ' fet=' , ex[2].hexadecimal(False) ,
            if len(ex) > 3:
                print ' sem=' , ex[3].hexadecimal(False) ,
            if len(ex) > 4:
                print ' pls=' , str(ex[4]) ,
            print ''

    def run ( self , segm ):

        """
        execute each extractor and store results

        arguments:
            self  -
            segm  - input buffer

        returns:
            returns number of chars matched on success, 0 otherwise
        """

        mx = 0
        ms = [ ]
        capd = ellyChar.isUpperCaseLetter(segm[0])
        for xr in self.exs:       # try each extraction procedure in order
            m = xr[0](segm)       #
            if m > 0:             # match?
                if mx > m:        # if so, it has to be longer than the longest previous
                    continue
                elif mx < m:      # if longer than longest previous, discard the previous
                    mx = m
                    ms = [ ]
                ms.append(xr[1:]) # add to match list
        nmatch = 0
        if mx > 0:                # any matches?
            for mr in ms:         # if so, make phrases for them
                sbs = mr[2] if len(mr) > 2 else noBits
                bia = mr[3] if len(mr) > 3 else 0
                if self.ptr.addLiteralPhraseWithSemantics(mr[0],mr[1],sbs,bia,None,False,capd):
                    self.ptr.lastph.lens = mx
                    nmatch += 1

        return mx if nmatch > 0 else 0

#
# unit test
#

if __name__ == '__main__':

    import parseTest
    import sys

    print 'test entity extraction'
    utre = parseTest.Tree()
    uctx = parseTest.Context()

    ee = EntityExtractor(utre,uctx.syms)
    print 'procedures:'
    ee.dump()
    print ''

    while True:
        sys.stdout.write('> ')
        l = sys.stdin.readline()
        if len(l) <= 1: break
        b = list(l)
        mn = ee.run(b)
        print 'match n=' , mn
        if mn > 0:
            print utre.lastph
            print 'new buffer:' , b
    sys.stdout.write('\n')
