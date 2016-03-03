#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# patternTable.py : 02mar2016 CPM
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
finite-state automaton (FSA) for inferring the syntactic type of single tokens
"""

import sys
import ellyChar
import ellyWildcard
import ellyException
import syntaxSpecification

class Link(object):

    """
    for defining FSA transitions with Elly pattern matching

    attributes:
        patn  - Elly pattern to match
        nxts  - next state on match
        catg  - syntactic category
        synf  - syntactic features
    """

    def __init__ ( self , syms , dfls ):

        """
        initialization

        arguments:
            self  -
            syms  - Elly grammatical symbol table
            dfls  - definition elements in list

        exceptions:
            FormatFailure on error
        """

#       print 'dfls=' , dfls
        if len(dfls) != 3:                                # must have 3 elements
            raise ellyException.FormatFailure
        else:
            if dfls[0] == '\\0':
                self.patn = u'\x00'                       # special nul pattern
            else:
                self.patn = ellyWildcard.convert(dfls[0]) # encode Elly pattern
            if dfls[0] != '$':
                if self.patn == None or ellyWildcard.minMatch(self.patn) == 0:
                    print >> sys.stderr , '** bad link pattern:' , dfls[0]
                    raise ellyException.FormatFailure
#               print 'appended patn=' , list(self.patn) , '=' , len(self.patn)

            self.catg = None                          # defaults
            self.synf = None                          #
            sss = dfls[1].lower()                     # assumed not to be Unicode
#           print 'sss=' , sss
            if sss != '-':                            # allow for no category
                syx = syntaxSpecification.SyntaxSpecification(syms,sss)
                if syx != None:
                    self.catg = syx.catg              # syntactic category
                    self.synf = syx.synf.positive     # syntactic features

            try:
                n = int(dfls[2])                      # next state for link
            except:
                raise ellyException.FormatFailure     # unrecognizable number

            if n < 0:                                 # final transition?
                if self.patn == u'\x00':
                    raise ellyException.FormatFailure # final state not allowed here
                pe = self.patn[-1]                    # if so, get last pattern element
                if ( pe != ellyWildcard.cALL and      # final pattern must end with * or $
                     pe != ellyWildcard.cEND ):
                    self.patn += ellyWildcard.cEND    # default is $
                    print >> sys.stderr , '** final $ added to pattern' , list(self.patn)

            self.nxts = n                             # specify next state

    def __unicode__ ( self ):

        """
        string representation of link

        arguments:
            self

        returns:
            string for printing out
        """

        if self.patn == None:
            return u'None'
        else:
            if self.patn == u'\x00':
                p = '\\0              '
            else:
                p = u'{0:<24}'.format(ellyWildcard.deconvert(self.patn))
            c = unicode(self.catg)
            f = u'None' if self.synf == None else self.synf.hexadecimal(False)
            return p + ' ' + ' ' + c + ' ' + f + ' next=' + unicode(self.nxts)

Trmls = ellyWildcard.Trmls

def bound ( segm ):

    """
    get maximum limit on string for pattern matching
    (override this method if necessary)

    arguments:
        segm  - text segment to match against

    returns:
        char count
    """

    lm = len(segm)   # limit can be up to total length of text for matching
    ll = 0
    while ll < lm:   # look for first space in text segment
        if segm[ll] == ' ': break
        ll += 1
#   print 'll=' , ll , ', lm=' , lm
    ll -= 1
    while ll > 0:    # exclude trailing non-alphanumeric from matching
                     # except for '.' and '*' and bracketing
        c = segm[ll]
        if c in Trmls or c == '*' or ellyChar.isLetterOrDigit(c): break
        ll -= 1
    return ll + 1

class PatternTable(object):

    """
    FSA with Elly patterns to determine syntax types

    attributes:
        indx      - for FSA states and their links

        _errcount - running input error count
     """

    def __init__ ( self , syms=None , fsa=None ):

        """
        initialize

        arguments:
            self  -
            syms  - symbol table for syntax categories and features
            fsa   - EllyDefinitionReader for FSA patterns plus syntax specifications

        exceptions:
            TableFailure on error
        """

        self.indx = [ ]     # start empty
        self._errcount = 0  # no errors yet
        if fsa != None and syms != None:
            self.load(syms,fsa)

    def _err ( self , s='malformed FSA transition' , l='' ):

        """
        for error handling

        arguments:
            self  -
            s     - error message
            l     - problem line
        """

        self._errcount += 1
        print >> sys.stderr , '** pattern error:' , s
        if l != '':
            print >> sys.stderr , '*  at [' , l , ']'

    def load ( self , syms , fsa ):

        """
        convert text input to get FSA with encoded syntax

        arguments:
            self  -
            syms  - symbol table for syntax categories and features
            fsa   - FSA link input from Elly definition reader

        exceptions:
            TableFailure on error
        """

                        # for error checking
        ins = [ 0 ]     # states with incoming links
        sss = [   ]     # starting states
        lss = [ 0 ]     # all defined states

        nm = 0                               # states producing matches
#       print 'FSA definition line count=' , fsa.linecount()
        while True: # read all input from ellyDefinitionReader
            line = fsa.readline()
#           print 'input line=' , line
            if len(line) == 0: break         # EOF check
            ls = line.strip().split(' ')     # get link definition as list
#           print 'ls=' , ls
            sts = ls.pop(0)                  # starting state for FSA link
            try:
                stn = int(sts)               # numerical starting state
            except ValueError:
                self._err('bad start state',line)
                continue
            n = len(self.indx)

            while stn >= n:                  # make sure state index has enough slots
                self.indx.append([ ])
                n += 1

            try:
                lk = Link(syms,ls)           # allocate new link
            except ellyException.FormatFailure:
                self._err('bad FSA option',line)
                continue
#           print 'load lk=' , lk

            if lk.nxts < 0:                  # final state?
                if lk.catg != None:
                    nm += 1                  # count link category for match
                else:
                    self._err('missing category for final state',line)
                    continue
            elif lk.catg != None:
                self._err('unexpected category for non-final state' , line)

            if not stn in lss: lss.append(stn)
            if not stn in sss: sss.append(stn)
            if lk.nxts >= 0:                 # -1 is stop, not state
                if not lk.nxts in lss: lss.append(lk.nxts)
                if not lk.nxts in ins: ins.append(lk.nxts)

            self.indx[stn].append(lk)        # add to its slot in FSA state index
#           print '=' , self.indx[stn]

        if len(self.indx) == 0 and self._errcount == 0:
            return                           # in case of empty definition file

        if nm == 0:                          # FSA must have at least one match state
            self._err('no match states')
#       print 'ins=' , ins
#       print 'lss=' , lss

        ns = len(lss)                        # total number of states
        if len(ins) != ns:
            self._err('some states unreachable')
        if len(sss) != ns:
            self._err('some non-stop states are dead ends')

        if self._errcount > 0:
            print >> sys.stderr , '**' , self._errcount , 'pattern errors in all'
            print >> sys.stderr , 'pattern table definition FAILed'
            raise ellyException.TableFailure

    def match ( self , segm , tree ):

        """
        compare text segment against FSA patterns

        arguments:
            self  -
            segm  - segment to match against
            tree  - parse tree in which to put leaf nodes for final matches

        returns:
            text length matched by FSA
        """

#       print 'comparing' , segm

        if len(self.indx) == 0: return 0  # no matches if FSA is empty

        lim = bound(segm)                 # get limit for matching

        mtl  = 0        # accumulated match length
        mtls = 0        # saved final match length

        state = 0       # set to mandatory initial state for FSA

        stk = [ ]       # for tracking multiple possible matches

        ls = self.indx[state]
        ix = 0
        sg = segm[:lim] # text subsegment for matching
        capd = False if len(sg) == 0 else ellyChar.isUpperCaseLetter(sg[0])

        while True:                 # run FSA to find all possible matches
#           print 'state=' , state
#           print 'count=' , mtl , 'matched so far'
#           print 'links=' , len(ls)
            nls = len(ls)           # how many links from current state

            if ix == nls:           # if none, then must back up
                if len(stk) == 0: break
                r = stk.pop()       # restore match status
                state = r[0]        # FSA state
                ls  = r[1]          # remaining links to check
                sg  = r[2]          # input string
                mtl = r[3]          # total match length
                ix = 0
                continue

            m = 0
            while ix < nls:
                lk = ls[ix]         # get next link at current state
                ix += 1             # and increment link index
#               print 'lk= [' , unicode(lk), '] , sg=' , sg
                if lk.patn == u'\x00': # do state change without matching?
                    m = 0           # no match length
                else:
#                   print 'match lk=' , unicode(lk) , 'sg=' , sg
                    bds = ellyWildcard.match(lk.patn,sg)
#                   print 'bds=' , bds
                    if bds == None: continue

                    m = bds[0]      # get match length, ignore wildcard bindings

                    if lk.nxts < 0: # final state?
                        if tree.addLiteralPhrase(lk.catg,lk.synf,False,capd): # make phrase
                            mtls = mtl + m
                            tree.lastph.lens = mtls                   # save its length
#                           print 'match state=' , state , 'length=' , mtls
#                       else:
#                           print 'lastph=' , tree.lastph
#                           print 'seg=' , sg
#                           print 'cat=' , lk.catg, 'synf=' , lk.synf

#               print 'ix=' , ix , 'nls=' , nls
                if ix < nls:        # any links not yet checked?
                    r = [ state , ls[ix:] , sg , mtl ]
#                   print 'r=' , r
                    stk.append(r)   # if not, save info for later continuation

                mtl += m            # update match length
                break               # leave loop at this state, go to next state
            else:
#               print 'no matches'
                continue            # all patterns exhausted for state

            ix = 0
            sg = sg[m:]             # move up in text input
            state = lk.nxts         # next state
            if state < 0:
                ls = [ ]
            else:
                ls = self.indx[state]
#           print 'sg=' , sg
#           print 'state=' , state
#           print 'len(ls)=' , len(ls)

        return mtls

    def dump ( self ):

        """
        show contents of pattern table

        arguments:
            self
        """

        nn = 0   # nul pattern count
        for k in range(len(self.indx)):
            lks = self.indx[k]
            if lks == None or lks == [ ]:
                continue
            print '[state ' + str(k) + ']'
            for lk in lks:
                print u'  ' + unicode(lk)
                if lk.patn == u'\x00': nn += 1
        print nn , 'nul pattern(s)'
        print ''

#
# unit test
#

if __name__ == '__main__':

    import ellyConfiguration
    import ellyDefinitionReader
    import dumpEllyGrammar
    import parseTest
    import stat
    import os

    mode = os.fstat(0).st_mode       # to check for redirection of stdin (=0)
    interact = not ( stat.S_ISFIFO(mode) or stat.S_ISREG(mode) )

    tre = parseTest.Tree()           # dummy parse tree for testing
    ctx = parseTest.Context()        # dummy interpretive context for testing
    print ''

    basn = ellyConfiguration.baseSource + '/'
    filn = sys.argv[1] if len(sys.argv) > 1 else 'test' # which FSA definition to use
    inp = ellyDefinitionReader.EllyDefinitionReader(basn + filn + '.p.elly')

    print 'pattern test with' , '<' + filn + '>'

    if inp.error != None:
        print inp.error
        sys.exit(1)

    patn = None
    try:
        patn = PatternTable(ctx.syms,inp) # try to define FSA
    except ellyException.TableFailure:
        print 'no pattern table generated'
        sys.exit(1)

    print len(patn.indx) , 'distinct FSA state(s)'

    print ''
    dumpEllyGrammar.dumpCategories(ctx.syms)
    print ''
    patn.dump()

    print 'enter tokens to recognize'

    while True: # try FSA with test examples

        if interact: sys.stdout.write('> ')
        t = sys.stdin.readline().strip()
        if len(t) == 0: break
        print 'text=' , '[' , t , ']'
        nma = patn.match(list(t),tre)
        print '    from <'+ t + '>' , nma , 'chars matched' , '| leaving <' + t[nma:] + '>'

    if interact: sys.stdout.write('\n')

    tre.showQueue()
