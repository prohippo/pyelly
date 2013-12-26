#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# stopExceptions.py : 24dec2013 CPM
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

class StopExceptions(object):

    """
    implement special pattern matching for stop punctuation special cases

    attributes:
        lstg  - listing of punctuation patterns as Python dictionary keyed on the punctuation
        maxl  - maximum length of left parts of pattern

        _plvl - parentheses level
        _blvl - bracket level
    """

    class Pattern(object):
        """
        exception pattern instances
        attributes:
            left  - left  context
            right - right context
        """
        def __init__ ( self , left , right ):
            self.left  = left
            self.right = right
        def __unicode__ ( self ):
            return ( ellyWildcard.deconvert(self.left) + ' | ' +
                     ellyWildcard.deconvert(self.right) )

    def __init__ ( self , defs=None ):

        """
        initialize

        arguments:
            self  -
            defs  - EllyDefinitionReader for pattern input
        """

        self.lstg = { }  # empty at start
        self.maxl = 0    # maximum is zero to start with
        self.resetBracketing()
        if defs != None: self.load(defs)

    def load ( self , defs ):

        """
        get pattern definitions from reader and convert wildcards

        arguments:
            self  -
            defs  - EllyDefinitionReader
        """
        
        lno = 0
        while True:

            df = defs.readline().lower().strip()
            if len(df) == 0: break
            lno += 1
            if len(df) <= 1:
                print >> sys.stderr , 'bad pattern=[' + df + '] (' + str(lno) + ')'
                break

            ps = df.split('|')
            if len(ps) == 1:
                print >> sys.stderr , 'missing | in pattern=[' + df + '] (' + str(lno) + ')'
                break
#           print 'ps=' , ps

            id = ps[0][-1]                 # last char of left part of pattern
            left  = ellyWildcard.convert(ps[0][:-1])
            right = ellyWildcard.convert(ps[1])
            if left == None:
                print >> sys.stderr , 'error:' , '<' + df + '>' , '<' + right + '>'
                break
            
            if not id in self.lstg:        # make sure punctuation is already in dictionary
                self.lstg[id] = [ ]

            p = self.Pattern(left,right)
            self.lstg[id].append(p)        # save pattern in dictionary

            if left != None:               # update maximum length of left contexts
                ll = len(left)
                if self.maxl < ll : self.maxl = ll

    def noteBracketing ( self , c ):

        """
        track level of bracketing within sentence being accumulated

        arguments:
            self  -
            c     - bracketing char to take account of
        """
    
        if   c == u'(':
            self._plvl += 1
        elif c == u'[':
            self._blvl += 1
        elif c == u')':
            self._plvl -= 1
        elif c == u']':
            self._blvl -= 1
    
    def resetBracketing ( self ):

        """
        reset bracketing levels
    
        arguments:
            self
        """

        self._plvl = 0
        self._blvl = 0
    
    def inBracketing ( self ):

        """
        check whether the current punctuation is within parentheses or brackets

        arguments:
            self
        """
    
        return (self._plvl > 0 or self._blvl > 0)
    
    def match ( self , txt , pnc , nxt ):

        """
        compare a punctuation mark and its context with a pattern

        arguments:
            self  -
            txt   - list of text chars up to and including punctuation char
            pnc   - punctuation char
            nxt   - single char after punctuation

        returns:
            True on match, False otherwise
        """

        self.noteBracketing(pnc)  # just in case this is bracketing

        if not pnc in self.lstg:  # get stored patterns for punctuation
            return False

        lp = self.lstg[pnc]

        txl = txt[-self.maxl:] if len(txt) > self.maxl else txt
        
        txs = map(lambda x: x.lower(),txl) # actual left context for matching

#       print 'txs= ' + str(txs) + ' pnc= [' + pnc + '] nxt=[' + nxt + ']'

        lt = len(txs)             # its length

#       print len(lp) , 'patterns'

        for p in lp:              # try matching each pattern

            if p.left != None:
                
                n = len(p.left)   # assume each pattern element must match one sequence char
#               print n , 'pattern elements' , lt , 'chars'
                if n > lt:
                    continue      # fail immediately because of impossibility of match
                if n < lt and ellyChar.isLetterOrDigit(txs[-n-1]):
                    continue      # fail because of text to match is after alphanumeric
                t = txs if n == lt else txs[-n:]
#               print 'pat=' , '[' + ellyWildcard.deconvert(p.left) + ']'
                if not ellyWildcard.match(p.left,t,0):
                    continue

#           nc = '\\n' if nxt == '\n' else nxt
#           print 'nxt=' , '[' + nc + ']'
#           print 'pat=' , '[' + ellyWildcard.deconvert(p.right) + ']'
#           if len(p.right) > 0: print '    ' ,  ord(p.right)

            if p.right == u'' or p.right == nxt: # check for specific char after possible stop
                return True
            if p.right == ellyWildcard.cCAN:     # check for nonalphanumeric
                if nxt == u'' or not  ellyChar.isLetterOrDigit(nxt):
                    return True
            if p.right == ellyWildcard.cSPC:     # check for white space
#               print 'looking for space'
                if nxt == u'' or nxt == u' ' or nxt == u'\n':
                    return True
            if p.right == u'.':                  # check for any punctuation
                if not ellyChar.isLetterOrDigit(nxt) and not ellyChar.isWhiteSpace(nxt):
                    return True

        return False

#
# unit test
#

if __name__ == '__main__':

    import ellyConfiguration
    import ellyDefinitionReader

    base = ellyConfiguration.baseSource + '/'
    nam = sys.argv[1] if len(sys.argv) > 1 else 'default'
    dfs = base + nam + '.sx.elly'
    print 'reading from' , dfs

    inp = ellyDefinitionReader.EllyDefinitionReader(dfs)
    stpx = StopExceptions(inp)

    np = len(stpx.lstg)
    print np , 'sets of punctuation patterns'
    if np == 0: sys.exit(0)

    for px in stpx.lstg:
        ps = stpx.lstg[px]
        print '<' + px + '>'
        for p in ps:
            print '    ' , unicode(p)

    test = [
        [ 'u' , '.' , 's' , '.' , 's' , '.' , ' ' , 'w' , 'a' , 's' , 'p' ] ,
        [ 'm' , 'r' , '.' , ' ' ] ,
        [ 'x' , 'm' , 'r' , '.' , ' ' ] ,
        [ 'p' , 'p' , '.' , ' ' ] ,
        [ 'n' , 'n' , '.' , ' ' ] ,
        [ '-' , "'" , ' ' ] ,
        [ ':' , '-' , ')' ] ,       # emoticon
        [ 'x' , 'x' , 'x' , 'x' , '.' , ' ' , 'Y' ]
    ]

    n = len(sys.argv) - 2
    if n > 0:             # add to test cases?
        for a in sys.argv[2:]:
            test.append(list(a.decode('utf8')))
        print 'added' , n , 'test case' + ('' if n == 1 else 's')
    else:
        print 'no added test cases'

    for t in test:
        k = 0
        l = len(t)
        while k < l:
            c = t[k]
            k += 1
            if c in stpx.lstg:
                if k == l or not ellyChar.isLetterOrDigit(t[k]):
                    break
        else:
            continue
        res = stpx.match( t[:k-1] , t[k-1] , t[k] )
        print 'exception match:' , '[' + ''.join(t) + ']' , res
