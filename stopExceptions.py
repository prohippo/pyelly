#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# stopExceptions.py : 28may2017 CPM
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
# SERVICES LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

"""
special patterns of punctuation to ignore as sentence delimiters

each pattern specifies a sequence of one or more characters before a
potential stop punctuation character (left context) and one character
or none after it (right context)
"""

import sys
import ellyChar
import ellyWildcard
import ellyException

class StopExceptions(object):

    """
    implement special pattern matching for stop punctuation special cases

    attributes:
        lstg  - listing of punctuation patterns as Python dictionary keyed on the punctuation
        maxl  - maximum length of left parts of pattern
    """

    class Pattern(object):
        """
        exception pattern instances

        attributes:
            left  - left  context
            right - right context
        """
        def __init__ ( self , left , right ):
            """ initialization
            """
            self.left  = left
            self.right = right
        def __unicode__ ( self ):
            """ representation
            """
            return ( ellyWildcard.deconvert(self.left) + ' | ' +
                     ellyWildcard.deconvert(self.right) )

    def __init__ ( self , defs=None ):

        """
        initialize

        arguments:
            self  -
            defs  - EllyDefinitionReader for pattern input

        exceptions:
            TableFailure on error
        """

        self.lstg = { }  # empty at start
        self.maxl = 0    # maximum is zero to start with
        if defs != None: self.load(defs)

    def load ( self , defs ):

        """
        get pattern definitions from reader and convert wildcards

        arguments:
            self  -
            defs  - EllyDefinitionReader

        exceptions:
            TableFailure on error
        """

        lno = 0
        nerr = 0
        while True:

            df = defs.readline().strip()
#           print 'df=' , df
            if len(df) == 0: break
            lno += 1
            if len(df) <= 1:
                print >> sys.stderr , 'bad pattern=[' + df + '] (@' + str(lno) + ')'
                nerr += 1
                continue
            ps = df.split('|')
            if len(ps) == 1:
                print >> sys.stderr , 'missing | in pattern=[' + df + '] (@' + str(lno) + ')'
                nerr += 1
                continue
#           print 'ps=' , ps

            idc = ps[0][-1]                # last char of left part of pattern
            left  = ellyWildcard.convert(ps[0][:-1])
            right = ellyWildcard.convert(ps[1])
#           print 'idc=' , idc , 'left=' , left , 'right=' , right
            if left == None:
                print >> sys.stderr , 'bad left context in pattern' , '<' + df + '>'
                nerr += 1
                continue
            if len(right) > 1:
                print >> sys.stderr , 'bad right context in pattern' , '<' + df + '>'
                nerr += 1
                continue

            if not idc in self.lstg:       # make sure punctuation is already in dictionary
                self.lstg[idc] = [ ]

            pat = self.Pattern(left,right)
            self.lstg[idc].append(pat)     # save pattern in dictionary
#           print 'lstg=' , self.lstg.keys()

            ll = len(left)
            if self.maxl < ll : self.maxl = ll

        if nerr > 0:
            raise ellyException.TableFailure

    def match ( self , txt , pnc , ctx ):

        """
        compare a punctuation mark and its context with a pattern

        arguments:
            self  -
            txt   - list of text chars leading up to punctuation char
            pnc   - punctuation char
            ctx   - next chars after punctuation

        returns:
            True on match, False otherwise
        """

#       print 'matching for txt=' , txt , 'pnc=' , pnc , 'ctx=' , ctx

        if nomatch(txt,pnc,ctx):
            return False
#       print 'nomatch() False'

        nxt = ctx[1] if len(ctx) > 1 else ''

#       print 'lstg=' , self.lstg.keys()
        if not pnc in self.lstg:  # get stored patterns for punctuation
            return False

        lp = self.lstg[pnc]

#       print len(lp) , 'patterns'

        txs = txt[-self.maxl:] if len(txt) > self.maxl else txt

        lt = len(txs)             # its length

#       print 'txs= ' + unicode(txs) + ' pnc= [' + pnc + '] nxt=[' + nxt + ']'

        for p in lp:              # try matching each pattern

            if p.left != None:

                n = len(p.left)   # assume each pattern element must match one sequence char
#               print 'n=' , n , 'p=' , unicode(p)
                if n > lt:
                    continue      # fail immediately because of impossibility of match
                t = txs if n == lt else txs[-n:]
#               print 'left pat=' , '[' + ellyWildcard.deconvert(p.left) + ']'
#               print 'versus t=' , t
                if not ellyWildcard.match(p.left,t,0):
#                   print 'no left match'
                    continue
                if n < lt and ellyChar.isLetterOrDigit(t[0]):
                    if ellyChar.isLetterOrDigit(txs[-n-1]):
                        continue  # fail because of no break in text

#           nc = '\\n' if nxt == '\n' else nxt
#           print 'right pat=' , '[' + ellyWildcard.deconvert(p.right) + ']'
#           print 'versus c=' , nc

            if p.right == []:
                return True
            pcx = p.right[0]
            if pcx == nxt:                     # check for specific char after possible stop
#               print 'right=' , nxt
                return True
            if pcx == ellyWildcard.cCAN:       # check for nonalphanumeric
                if nxt == u'' or not ellyChar.isLetterOrDigit(nxt):
#                   print 'right nonalphanumeric=' , nxt
                    return True
            if pcx == ellyWildcard.cSPC:       # check for white space
#               print 'looking for space'
                if nxt == u'' or nxt == u' ' or nxt == u'\n':
#                   print 'right space'
                    return True
#           print 'last check'
            if p.right == u'.':                # check for any punctuation
                if not ellyChar.isLetterOrDigit(nxt) and not ellyChar.isWhiteSpace(nxt):
#                   print 'right punc=' , nxt
                    return True

#       print "no matches"
        return False

##

def nomatch ( txt , pnc , ctx ):

    """
    special case checks - currently only for period in A.M. or P.M.

    for overriding the checking done by the match() member method

    arguments:
        txt   - list of text chars leading up to punctuation char
        pnc   - punctuation char
        nxt   - single char after punctuation

    returns:
        True on match, False otherwise
    """

    ln = len(txt)
#   print 'nomatch ln=' , ln , txt
    nxt = ctx[0] if len(ctx) > 0 else ''
    if pnc != '.' or not ellyChar.isWhiteSpace(nxt) or ln < 5:
        return False
#   print 'check' , txt[-3:]
    if not txt[-1] in [ 'M' , 'm' ] or txt[-2] != '.' or not txt[-3] in [ 'P' , 'p' , 'A' , 'a' ] or txt[-4] != ' ':
        return False
    ch = txt[-5]
#   print 'ch=' , ch
    if ellyChar.isDigit(ch):
        return True
    elif not ellyChar.isLetter(ch):
        return False

    nn = 6
    while nn <= ln and ellyChar.isLetter(txt[-nn]):
        nn += 1

#   print 'nn=' , nn
    if nn > ln:
        wd = ''.join(txt[:-4]).lower()
    elif not txt[-nn] in [ ' ' , '-' ]:
        return False
    else:
        wd = ''.join(txt[-nn+1:-4]).lower()

    if wd in [ 'one' , 'two' , 'three' , 'four' , 'five' , 'six' , 'seven' ,
               'eight' , 'nine' , 'ten' , 'eleven' , 'twelve' ]:
        if len(ctx) < 2 or ellyChar.isUpperCaseLetter(ctx[1]):
            return False
        else:
            return True
    else:
        return False

#
# unit test
#

if __name__ == '__main__':

    import ellyConfiguration
    import ellyDefinitionReader

    base = ellyConfiguration.baseSource
    nam = sys.argv[1] if len(sys.argv) > 1 else 'default'
    dfs = base + nam + '.sx.elly'
    print 'reading from' , dfs

    inp = ellyDefinitionReader.EllyDefinitionReader(dfs)
    if inp.error != None:
        print >> sys.stderr , inp.error
        sys.exit(1)
    try:
        stpx = StopExceptions(inp)
    except ellyException.TableFailure:
        print >> sys.stderr , '** failed to load stop exceptions'
        sys.exit(1)

    np = len(stpx.lstg)
    print np , 'sets of punctuation pattern(s)'
    if np == 0: sys.exit(0)

    for px in stpx.lstg:
        pxs = stpx.lstg[px]
        print '<' + px + '>'
        for pc in pxs:
            print '    ' , unicode(pc)

    SQW = ellyWildcard.wAPO

    test = [
        list('u.s.s. wasp') ,
        list('mr. ') ,
        list('xmr. ') ,
        list('pp. ') ,
        list('nn. ') ,
        list('Ph.D. ') ,
        list('g.i. ') ,
        list(' A. ') ,
        list("-' ") ,
        list(':-)') ,       # emoticon
        list('xxxx. Y') ,
        list(' . ') ,
        list(' m. morrel' + SQW + 's sal') ,
        list('J.S. Dillon') ,
        list('two P.M. ') ,
        list('after six p.m. ') ,
        list('2:00. ')
    ]

    nlu = len(sys.argv) - 2
    if nlu > 0:                     # add to test cases?
        for a in sys.argv[2:]:      # get commandline args to test
            test.append(list(a.decode('utf8')))
        print 'added' , nlu , 'test case' + ('' if nlu == 1 else 's')
    else:
        print 'no added test cases'
    print '--------'
    print len(test) , 'cases in all'

    for ts in test:
        ku = 0
        lu = len(ts)
        for cu in ts:             # scan input line
            ku += 1
            if cu in stpx.lstg:   # find first candidate stop
                if ku == lu or not ellyChar.isLetterOrDigit(ts[ku]):
                    break         # must not be followed by letter or digit
        else:
            continue
        res = stpx.match( ts[:ku-1] , ts[ku-1] , ts[ku] )
        print '[ ' + ''.join(ts) + ' ] @' , ku-1 ,
        print 'stop EXCEPTION' if res else 'sentence stopped'
