#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# morphologyAnalyzer.py : 17sep2015 CPM
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
morphological analysis
"""

import suffixTreeLogic
import prefixTreeLogic
import ellyConfiguration
import ellyException

class MorphologyAnalyzer(object):

    """
    prefix and suffix handling

    attributes:
        pref  - prefix logic
        suff  - suffix logic
    """

    def __init__ ( self , sufdfn=None , predfn=None ):

        """
        initialization

        arguments:
            self   -
            sufdfn - suffix logic definition as EllyDefinitionReader
            predfn - prefix logic definition

        exceptions:
            TableFailure on error
        """

        self.pref = None
        self.suff = None
        if not ellyConfiguration.morphologicalStemming:
            return
        if sufdfn != None:
            self.suff = suffixTreeLogic.SuffixTreeLogic(sufdfn)
        if predfn != None:
            self.pref = prefixTreeLogic.PrefixTreeLogic(predfn)

    def analyze ( self , token ):

        """
        analyze token

        arguments:
            self  -
            token - token to be analyzed

        returns:
            True if affixes removed, False otherwise

        exceptions:
            StemmingError
        """

#       print 'token: ' , token.root
        if self.suff == None and self.pref == None:
            return False
        rs = token.root[0]
        re = token.root[-1]
        if rs == '+' or rs == '-' or re == '+':
            return False
#       print 'analysis:' , token
        suc = False
        if self.suff != None:
            if self.suff.match(token):
                suc = True
        if self.pref != None:
            if self.pref.match(token):
                suc = True
        return suc

#
# unit test
#

if __name__ == '__main__':

    import sys
    import ellyToken
    import ellyDefinitionReader
    import inflectionStemmerEN
    import os,stat

    print 'morphology test from sys.stdin'

    if not ellyConfiguration.morphologicalStemming:
        print 'Elly not configured for morphological analysis'
        sys.exit(1)

    mode = os.fstat(0).st_mode     # sys.stdin file status
    intr = not stat.S_ISREG(mode)  # flag for reading from keyboard

    sfil = sys.argv[1] if len(sys.argv) > 1 else 'default'
    pfil = sys.argv[2] if len(sys.argv) > 2 else sfil

    base = ellyConfiguration.baseSource + '/'
    sdfn = ellyDefinitionReader.EllyDefinitionReader(base + sfil + '.stl.elly')
    pdfn = ellyDefinitionReader.EllyDefinitionReader(base + pfil + '.ptl.elly')

    if sdfn.error != None or pdfn.error != None:
        print >> sys.stderr, 'suf error=' , sdfn.error
        print >> sys.stderr, 'pre error=' , pdfn.error

    try:
        inf = inflectionStemmerEN.InflectionStemmerEN()
        mor = MorphologyAnalyzer(sdfn,pdfn)
    except ellyException.TableFailure:
        print >> sys.stderr, 'initialization failed'
        sys.exit(1)

    mor.suff.infl = inf # set up root restoration

    nfail = 0  # count of instances when root fails to match expectation
    ntry  = 0  # total number of tries

    while True:
        if intr: sys.stdout.write('> ')
        lin = sys.stdin.readline()
        if len(lin) == 0:            # EOF check
            break
        lin = lin.strip()
        if len(lin) == 0:
            if intr: break           # empty line quits look on interactive input
            else: continue           # but otherwise continues
        lin = lin.split(' ')
        if len(lin) < 2:
            lin.append('-')          # should be [ word , root ] tuple
        w = lin[0]                   # unpack
        r = lin[1]
        if r != '-':
            ntry += 1                # input pair to be added to testing
        t = ellyToken.EllyToken(w)
#       print '0o t=' , t
        try:
            inf.apply(t)             # apply inflectional  stemming
        except ellyException.StemmingError:
            print 'stemming error'
            sys.exit(1)
#       print '1i t=' , t
        if not mor.analyze(t):       # apply morphological stemming
            msg = 'no morphological change'
        else:
            msg = ''
#       print '2m t=' , t
        nr = ''.join(t.root)         # resulting root
        if nr != r and r != '-':
            nfail += 1
            print 'FAILed: expected' , w , '->' , r , 'not' , nr
        else:
            print w , '-->>' , t.getPrefixes() , nr , t.getSuffixes() , msg

    print nfail , 'FAILures out of' , ntry , 'tests'
