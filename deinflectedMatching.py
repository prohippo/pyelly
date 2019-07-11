#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PyElly - scripting tool for analyzing natural language
#
# deinflectedMatching.py : 24sep2018 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2018, Clinton Prentiss Mah
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
for matching irrespective of English inflectional endings -S, -ED, and -ING in
a few general cases as part of an input stream match
"""

import ellyChar

Ls = u'\u017F'  # small long s used as special marker

def finAPO ( ss , sp ):

    """
    handle final apostrophes

    arguments:
        ss  - character stream
        sp  - last char of word in stream
    """

    lss = len(ss)
#   print 'finAPO lss=' , lss , ss[sp:]
    if lss > sp + 1:
#       print 'ending=' , ss[sp:]
        if ellyChar.isApostrophe(ss[sp+1]):
            if lss > sp + 2:
#               print 'ss=' , ss[sp:]
                if ss[sp+2].lower() == 's':
                    if terminate(ss,sp+3,lss):
                        sp += 1
#                       print 'sp=' , sp
                        ss[sp] = "'"
                        return
            if ss[sp].lower() == 's' and terminate(ss,sp+2,lss):
                sp += 1
                ss[sp] = Ls

def terminate ( ss , sp , lss=None ):

    """
    check char for termination of match
    arguments:
        ss  - char input stream
        sp  - char position in stream
    returns:
        True if terminating char or past end of input, False otherwise
    """

    if lss == None: lss = len(ss)
    return True if sp >= lss else not ellyChar.isLetterOrDigit(ss[sp])

def icmpr ( cc , tc ):

    """
    compare text against string with case insensitivity

    arguments:
        cc    - chars to compare
        tc    - text chars

    returns:
        0 on match, n if mismatch at n chars before end, -1 if unmatched
    """

    k = len(cc)
    n = len(tc)
    if k > n: return -1
    if k == 0: return n
    for i in range(k):
        if cc[i].lower() != tc[i].lower(): return k - i
    return 0

class DeinflectedMatching(object):

    """
    define simple matching with simple deinflection for
    inheritance by a child class

    attributes:
        endg   - any ending removed for match
    """

    def __init__ ( self ):

        """
        initialization

        arguments:
            self
        """

        self.endg = ''

    def simpleDeinflection ( self , ss , ssp , ssl , mr ):

        """
        handle matching of certain forms of English inflectional endings
        (override this method for other languages)

        arguments:
            self -
            ss   - input string of chars to scan for match
            ssp  - current position in input string
            ssl  - limit of matching in input
            mr   - next chars to look for in input

        returns:
            char count >= 0 on match, -1 otherwise
        """

        self.endg = ''       # null inflection by default
        if len(mr) == 0 and ssp == ssl:
            finAPO(ss,ssp-1)
            return 0
        if ssp < 2 or ss[ssp-2] == ' ':
            return -1
        ts = ss[ssp:]        # where to look for inflection
        mc = ss[ssp-1]       # last char matched
        lm = len(mr)
#       print ts , 'mc=' , mc , 'mr=' , mr
        if not ellyChar.isLetter(mc):
            return -1
        dss = ssl - ssp      #
#       print 'dss=' , dss
        if dss == 0:         # must handle special case here
            if lm == 0:
                finAPO(ss,ssp-1)
                return 0
        elif dss == 1:       # just a single letter left for inflection
            if lm != 0:
                return -1
            elif ts[0].lower() == 's':
                self.endg = '-s'
                finAPO(ss,ssp)
                return 1
            elif mc == 'e' and ts[0].lower() == 'd':
                self.endg = '-ed'
                return 1
        elif dss == 2:       # 2 letters for inflection
            if lm == 0 and ts[0].lower() == 'e':
                if ts[1].lower() == 'd':
                    self.endg = '-ed'
                    return 2
                elif ts[1].lower() == 's':
                    self.endg = '-s'
                    finAPO(ss,ssp+1)
                    return 2
        elif dss == 3:       # 3 letters for inflection
#           print 'ts=' , ts , 'mr=' , mr
            if ts[0].lower() == 'i':
                if ts[1].lower() == 'e':
                    if lm == 1 and mr[0] == 'y':
                        if ts[2].lower() == 's':
                            self.endg = '-s'
                            return 3
                        elif ts[2].lower() == 'd':
                            self.endg = '-ed'
                            return 3
                elif ts[1].lower() == 'n' and ts[2].lower() == 'g':
                    if lm == 0 or lm == 1 and mr[0] == 'e':
                        self.endg = '-ing'
                        return 3
            if lm == 0 and ts[0].lower() == mc and ts[1].lower() == 'e' and ts[2].lower() == 'd':
                self.endg = '-ed'
                return 3
        elif dss == 4:       # 4 letters for inflection
            if lm == 0 and ts[0].lower() == mc and ts[1] == 'i' and ts[2].lower() == 'n' and ts[3].lower() == 'g':
                self.endg = '-ing'
                return 4
            if ts[0].lower() == 'y' and ts[1].lower() == 'i' and ts[2].lower() == 'n' and ts[3].lower() == 'g':
                if lm == 2 and mr[0] == 'i' and mr[1] == 'e':
                    self.endg = '-ing'
                    return 4

        return -1    # something other than inflection found

    def doMatchUp ( self , ccs , txs ):

        """
        match current text with vocabulary entry, possibly removing final inflection
        (this method assumes English; override it for other languages)

        arguments:
            self  -
            ccs   - chars for comparison
            txs   - text chars to be matched

        returns:
            count of txs chars matched, 0 on mismatch
        """

#       print 'match up ccs=' , ccs , 'txs=' ,txs
        self.endg = ''                       # default inflection
        lcc = len(ccs)                       # comparison pattern
        ltx = len(txs)                       # input text chars
        if lcc == 0 or ltx < lcc: return 0

        nr = icmpr(ccs,txs)                  # do match on lists of chars
#       print 'nr=' , nr

        if lcc < 4 and nr > 0:               # no stemming on short words
            return 0

#       try inflectional stemming to realize a match here,
#       but with abbreviated logic

        m = lcc - nr              # how many comparison chars matched so far
        k = m                     # get extent of text to look for termination
        while True:
            if terminate(txs,k,ltx):
                break             # find current end of text to match
            k += 1

#       print 'k=' , k , 'm=' , m

        ns = self.simpleDeinflection(txs,m,k,ccs[m:])

#       print 'ns=' , ns , 'm=' , m , ccs[m:] , txs[m:]

        return 0 if nr > ns or m + ns < lcc else m + ns

#
# unit test
#

import sys

if __name__ == '__main__':

    tstg = [  # default examples
        u'xxxxXY'  ,
        u'xxxxxy’S',
        u'xxxxxyS’',
        u'xxxxxyS’S',
        u'xxxxxyES’S',
        u'xxxxxyS' ,
        u'xxxxxyES',
        u'xxxxxIED',
        u'xxxxxyED'  ,
        u'xxxxxIES'  ,
        u'xxxxxyyED' ,
        u'xxxxxyING' ,
        u'xxxxxyyING',
        u'xxx xyED'  ,
        u'xxx xyS'   ,
        u'xxx xyZ'
    ]

    L = 6   # where to divide for a match in default testing

    dm = DeinflectedMatching()

    if len(sys.argv) > 2:  # test specific matching when arguments are given
        cxs = list(unicode(sys.argv[1],'utf-8'))
        ssb = list(unicode(sys.argv[2],'utf-8'))
        print 'cxs=' , cxs , 'ssb=' , ssb
        adv = dm.doMatchUp(cxs,ssb)
        print 'adv=' , adv , 'endg=' , dm.endg
        print 'ssb=' , ssb
        sys.exit(0)

    for s in tstg:         # or test all default examples
        print '***' , s
        ssb = list(s)
        cxs = ssb[:L]
        if cxs[-1] == 'i':
            cxs[-1] = 'y'  # make more realistic
        elif ssb[L-1:L+1] == 'yi':
            cxs[-1] = 'i'
            cxs.append('e')
        adv = dm.doMatchUp(cxs,ssb)
        print 'adv=' , adv , 'endg=' , dm.endg
        print 'ssb=' , ssb
