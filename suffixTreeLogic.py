#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# suffixTreeLogic.py : 06nov2014 CPM
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
morphological analyzer for suffixes
"""

import treeLogic
import ellyException

class SuffixTreeLogic(treeLogic.TreeLogic):

    """
    encapsulated stemmer for suffix removal

    attributes:
    """

    def __init__ ( self , inp ):

        """
        initialization

        arguments:
            self  -
            inp   - Elly definition reader

        exceptions:
            TableFailure on error
        """

        super(SuffixTreeLogic,self).__init__(inp)

    def sequence ( self , lstg ):

        """
        obtain list of chars for tree logic processing (overrides parent class)

        arguments:
            self  -
            lstg  - listing of chars in word to stem

        returns:
            list of chars on success, None otherwise
        """

        return lstg[::-1]  # i.e. token chars must be reversed

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

        return node.actns.applyRVS(token,leng,self)

#
# unit test
#

if __name__ == '__main__':

    import sys
    import ellyToken
    import ellyConfiguration
    import ellyDefinitionReader
    import inflectionStemmerEN

    filn = sys.argv[1] if len(sys.argv) > 1 else 'default'

    basn = ellyConfiguration.baseSource + '/'
    dfn = ellyDefinitionReader.EllyDefinitionReader(basn + filn + '.stl.elly')
    if dfn.error != None:
        print >> sys.stderr , dfn.error
        sys.exit(1)
    print dfn.linecount() , 'definition lines for' , filn + '.stl.elly'

    try:
        inf = inflectionStemmerEN.InflectionStemmerEN()
        suf = SuffixTreeLogic(dfn)
    except ellyException.TableFailure:
        print >> sys.stderr , 'cannot load stemming tables'
        sys.exit(1)
    suf.infl = inf
#   print 'suf=' , suf
#   print 'index=' , map(lambda x: ellyChar.toChar(ellyChar.toIndex(x)) , suf.indx.keys())
    print ''

    while True:
        sys.stdout.write('> ')
        wrd = sys.stdin.readline().strip()
        if len(wrd) == 0: break
        t = ellyToken.EllyToken(wrd)
        b = suf.match(t)
        a = ''.join(t.root)
        print t.getPrefixes() , a , t.getSuffixes() , ': status=' , b
    sys.stdout.write('\n')
