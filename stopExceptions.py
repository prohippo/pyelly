#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# stopExceptions.py : 02feb2018 CPM
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

def _rejectWild ( p ):

    """
    check that all stopException pattern wildcards are acceptable

    arguments:
        p  - list of pattern elements

    returns:
        True if each element can match only one char, otherwise False
        (the last element of a pattern can be * if there are other elements)
    """

    if p != None and len(p) > 1 and p[-1] == ellyWildcard.cALL:
        p = p[:-1]
    for pc in p:
        if ellyWildcard.isNonSimpleMatch(pc): return True
    return False

class StopExceptions(object):

    """
    implement special pattern matching for stop punctuation special cases

    attributes:
        lstg  - listing of punctuation patterns as Python dictionary keyed on the punctuation
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

        self.lstg = { }    # empty at start
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

            idc = ps[0][-1]                # last char of left part of pattern = possible punc
            left  = ellyWildcard.convert(ps[0][:-1])
            right = ellyWildcard.convert(ps[1])
#           print 'idc=' , idc , 'left=' , left , 'right=' , right
            if left  == None or _rejectWild(left) or len(left) == 0:
                print >> sys.stderr , 'bad left context in pattern' , '<' + df + '>'
                nerr += 1
                continue
            if right == None or _rejectWild(right) or len(right) > 1:
                print >> sys.stderr , 'bad right context in pattern' , '<' + df + '>'
                nerr += 1
                continue

            if not idc in self.lstg:       # make sure punctuation is already in dictionary
                self.lstg[idc] = [ ]

            pat = self.Pattern(left,right)
            self.lstg[idc].append(pat)     # save pattern in dictionary
#           print 'lstg=' , self.lstg.keys()

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

#       print 'matching for txt=' , txt , 'pnc= [' , pnc , ' ] ctx=' , ctx

        if matchtoo(txt,pnc,ctx):     # exception by complex match?
            return True
#       print 'matchtoo() returned False'

        sep = ctx[0] if len(ctx) > 0 else ''
        if sep == ellyChar.THS:
            return True
        nxt = ctx[1] if len(ctx) > 1 else ''

#       print 'lstg=' , self.lstg.keys()
        if not pnc in self.lstg:     # get stored patterns for punctuation
            return False

        lp = self.lstg[pnc]

#       print len(lp) , 'patterns'

        ltx = len(txt)               # current length of accumulated text so far
        ntr = 1
        while ntr <= ltx:
            if not ellyChar.isLetterOrDigit(txt[-ntr]):
                break
            ntr += 1
        nrg = ntr
        ntr -= 1                     # available trailing chars for  wildcard * match

        while nrg <= ltx:
            c = txt[-nrg]
            if not ellyChar.isLetterOrDigit(c) and not ellyChar.isEmbeddedCombining(c):
#               print 'break at nrg=' , nrg , txt[-nrg]
                break
            nrg += 1
        nrg -= 1                     # end of range for all pattern matching

#       print 'ntr=' , ntr , 'nrg=' , nrg

        txt = txt[-nrg:]             # reset text to limit for matching
        ltx = len(txt)               # its new length

#       print 'txt= ' + unicode(txt) + ' pnc= [' + pnc + '] nxt=[' + nxt + ']'

        for p in lp:                 # try matching each listed exception pattern

            if p.left != None and len(p.left) > 0:

                pat = p.left
                star = pat[-1] == ellyWildcard.cALL
                n = len(pat)         # it each pattern element matches one sequence char
                if star:             # except for a final wildcard *
#                   print 'pattern ending with *'
                    n -= 1
#                   print 'ltx=' , ltx , 'n=' , n
                    if ltx < n:
                        continue     # cannot match pattern properly
                    pat = pat[:-1]
                    t = txt[:n]
                else:
                    if ltx < n:
                        continue     # cannot match pattern properly
                    t = txt[-n:]

                if not ellyWildcard.match(pat,t,0):
#                   print 'no possible pattern match'
                    continue

                k = ltx - n          # extra chars beyond any match
#               print 'k=' , k , 't=' , t
#               print 'txt=' , txt
#               print 'pat=' , '[' + ellyWildcard.deconvert(pat) + ']'
#               print 'matches' , n , 'chars'
                if not star and k > 0:
#                   print 'check text before [' , txt[-n] , ']'
                    if ellyChar.isLetterOrDigit(txt[-n]):
                        c = txt[-n-1]
#                       print 'preceding= [', c , ']'
                        if ellyChar.isLetterOrDigit(c) or c == '&':
                            continue # because break in text is required

#           print 'pat=' , ellyWildcard.deconvert(p.left)
#           print 'n=' , n , 'ltx=' , ltx
#           print 'txt=' , txt

#           nc = '\\n' if nxt == '\n' else nxt
#           print 'right pat=' , '[' + ellyWildcard.deconvert(p.right) + ']'
#           print 'versus c=' , nc

            rp = p.right
            if rp == [] or rp[0] == ellyWildcard.cALL:
                return True
            pcx = rp[0]
            if pcx == nxt:                     # check for specific char after possible stop
#               print 'right=' , nxt
                return True
            elif pcx == ellyWildcard.cALF:     # check for alphabetic
                if ellyChar.isLetter(nxt):
#                   print 'right is alphabetic=' , nxt
                    return True
            elif pcx == ellyWildcard.cDIG:     # check for numeric
                if ellyChar.isDigit(nxt):
#                   print 'right is numeric=' , nxt
                    return True
            elif pcx == ellyWildcard.cUPR:     # check for upper case
                if ellyChar.isUpperCaseLetter(nxt):
                    return True
            elif pcx == ellyWildcard.cLWR:     # check for lower case
                if ellyChar.isLowerCaseLetter(nxt):
                    return True
            elif pcx == ellyWildcard.cCAN:     # check for non-alphanumeric
                if ellyChar.isLetter(nxt):
#                   print 'right is alphabetic=' , nxt
                    return True

#       print "no matches"
        return False

##

def matchtoo ( txt , pnc , ctx ):

    """
    complex checks - currently only for rightmost period of A.M. or P.M.

    arguments:
        txt   - list of text chars leading up to punctuation char
        pnc   - punctuation char
        ctx   - list of chars in context after punctuation

    returns:
        True on match, False otherwise
    """

    ln = len(txt)
#   print 'nomatch() ln=' , ln , txt
    nxt = ctx[0] if len(ctx) > 0 else ''
    if pnc != '.' or not ellyChar.isWhiteSpace(nxt) or ln < 5:
        return False
#   print 'check' , txt[-3:]
    if not txt[-1] in ['M','m'] or txt[-2] != '.' or not txt[-3] in ['P','p','A','a'] or txt[-4] != ' ':
        return False
    ch = txt[-5]
#   print 'ch=' , ch
    if ellyChar.isDigit(ch):        # only 1 digit will be checked here!
#       print 'ONE DIGIT'
        return True                 # erring on the side of not to break sentence
    elif not ellyChar.isLetter(ch):
        return False

#
#   the following code is needed only when number transforms are turned off
#

    nn = 6
    while nn <= ln and ellyChar.isLetter(txt[-nn]):
        nn += 1

#   print 'nn=' , nn
    if nn < 3 or nn > 6:
        return False
    elif nn > ln:
        if not txt[-nn] in [ ' ' , '-' ]:
            return False
    wd = ''.join(txt[:-nn]).lower()

#   print 'wd=' , wd
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
    print 'pattern(s) for' , np , 'punctuation mark(s)'
    if np == 0: sys.exit(0)

    for px in stpx.lstg:
        pxs = stpx.lstg[px]
        print '<' + px + '>'
        for pxc in pxs:
            print '    ' , unicode(pxc)

    SQW = ellyWildcard.wAPO
    THS = ellyChar.THS

    test = [
        list(u'u.s.s. wasp') ,
        list(u'mr. ') ,
        list(u'xmr. ') ,
        list(u'pp. ') ,
        list(u'nn. ') ,
        list(u'Ph.D. ') ,
        list(u'g.i. ') ,
        list(u' A. ') ,
        list(u"-' ") ,
        list(u':-)') ,       # emoticon
        list(u'xxxx. Y') ,
        list(u' . ') ,
        list(u' m. morrel' + SQW + 's sal') ,
        list(u'J.S. Dillon') ,
        list(u'John S. Dillon') ,
        list(u'two P.M. ') ,
        list(u'after six p.m. ') ,
        list(u'2:00. ') ,
        list(u'abc.' + THS + 'def') ,
        list(u'XXX: 123') ,
        list(u'XXX: Boo') ,
        list(u'S.A.F. \u201cA') ,
        list(u'2002. \u201cA') ,
        list(u'2:45 a.m. Friday')
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
            print ts , 'SKIPPED'
            continue
        res = stpx.match( ts[:ku-1] , ts[ku-1] , ts[ku:] )
        print '[ ' + ''.join(ts) + ' ] @' , ku-1 ,
        print 'stop EXCEPTION' if res else 'sentence stopped'
