#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# prefixTreeLogic.py : 30mar2017 CPM
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
morphological analyzer for prefixes
"""

import treeLogic
import ellyException

class PrefixTreeLogic(treeLogic.TreeLogic):

    """
    encapsulated stemmer for prefix removal

    attributes:
    """

    addn = u'+'  # special addition for root modification, overrides TreeLogic

    def __init__ ( self , inp ):

        """
        initialization

        arguments:
            self  -
            inp   - definition reader

        exceptions:
            TableFailure on error
        """

        super(PrefixTreeLogic,self).__init__(inp)

    def sequence ( self , lstg ):

        """
        obtain list of chars for tree logic processing (overrides parent class)

        arguments:
            self  -
            lstg  - listing of chars in word to stem

        returns:
            list of chars on success, None otherwise
        """

        return lstg  # i.e.  no reversal of chars

    def rewrite ( self , token , leng , node ):

        """
        rewrite token with new reduced root and suffixes

        arguments:
            self  -
            token - Elly token for results of stemming
            leng  - number of chars matched by tree logic
            node  - node for match

        returns:
            True on success, False otherwise
        """

        return node.actns.applyFWD(token,leng)

#
# unit test
#

if __name__ == '__main__':

    import sys
    import ellyToken
    import ellyConfiguration
    import ellyDefinitionReader

    system = sys.argv[1] if len(sys.argv) > 1 else 'test'
    print 'system=' , system

    base = ellyConfiguration.baseSource + '/'
    dfn = ellyDefinitionReader.EllyDefinitionReader(base + system + '.ptl.elly')
    if dfn.error != None:
        print >> sys.stderr , dfn.error
        sys.exit(1)
    n = dfn.linecount()
    print n , 'definition lines'
    if n == 0: sys.exit(0)

    try:
        pre = PrefixTreeLogic(dfn)
    except ellyException.TableFailure:
        print >> sys.stderr , 'cannot load prefix table'
        sys.exit(1)

    print 'pre=' , pre

    treeLogic.dumpLT(pre.indx)

    xs = [                           # test cases
        'telegraph +graph' ,
        'telephone +phone'   ,
        'transportation +portation' ,
        'pseudopod +pod'
    ]

    nfail = 0

    for x in xs:
        rec = x.strip().split()      # next test case
        if len(rec) != 2: continue   # better be [ input , expected output ]

        w = rec[0]                   # get separate components
        r = rec[1]

        t = ellyToken.EllyToken(w)   # make token for matching
        b = pre.match(t)
        a = ''.join(t.root)
        if not b:
            print ' NO MATCH=' , rec
        m = (r == a)
        if not m:
            print '     FAIL=' , rec , '!= <' + a + '>'
            nfail += 1

    print nfail , 'examples failed'
