#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# macroTable.py : 16feb2018 CPM
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
for defining the rewriting of input in tokenization

this uses an extension of the macro substitutions described in
Kernighan and Plauger's "Software Tools"
"""

import sys
import ellyChar
import ellyWildcard
import ellyException
import definitionLine

cEOS = ellyWildcard.cEOS

####
#
# the next two functions check for common problems in macro rules

special = ellyWildcard.Separate

def _checkBindings ( left , right ):

    """
    check if all bindings have associated wildcards

    arguments:
        left  - pattern
        right - substitution

    returns:
        True if bindings are valid, False otherwise
    """

#   print 'BIND: left=' , left , ' right=' , right
    mxb = '0'       # maximum binding
    k = 0
    l = len(right)
    while k < l:    # iterate on pattern string
        c = right[k]
        k += 1
        if c == '\\':
            if k == l:
                break
            b = right[k]
            k += 1
            if '1' <= b and b <= '9':  # note character comparisons!
                if mxb < b: mxb = b

#       print 'mxb=' , mxb

    if mxb == '0': return True

    m = int(mxb)    # maximum binding

    n = 0           # to count up possible wildcard bindings
    k = 0           # to iterate on pattern string
    l = len(left)   # iteration limit
    while True:
        while k < l:
            c = left[k]
            k += 1
            if c in special:
                n += 1
            elif ellyWildcard.isWild(c):
                if c != ellyWildcard.cEND: n += 1
                break
        if k == l:
            break
        while k < l:
            c = left[k]
            k += 1
            if c in special:
                n += 1
                break
            elif not ellyWildcard.isWild(c):
                break

#       print 'BIND: m=' , m , 'n=' , n
    return m <= n   # must be as many wildcard sequences as maximum binding

def _checkExpansion ( left , right ):

    """
    check that substitution does not produce more non-space chars
    ignoring pattern wildcards and substitutions dependent on bindings

    arguments:
        left  - pattern (converted)
        right - substitution (chars with escapes)

    returns:
        True if substitution is not longer than original text, False otherwise
    """

#   print 'expansion check: left=' , ellyWildcard.deconvert(left) , 'right=' , right
    inOpt = False
    nw = 0          # wildcard count in pattern
    n = 0           # literal char count
    for c in left:  # iterate on pattern string
#       print u'c= {:04x}'.format(ord(c))
        if not ellyWildcard.isWild(c):
            if not inOpt: n += 1
        elif c == ellyWildcard.cSOS:
            inOpt = True
        elif c == ellyWildcard.cEOS:
            inOpt = False
        elif not c in [ ellyWildcard.cEND , ellyWildcard.cALL ]:
            nw += 1

    afterEsc = False
    mw = 0          # wildcard binding count in substitution
    m = 0           # literal char count
    for c in right: # iterate on substitution string
        if afterEsc:
            if c >= '1' and c <= '9':     # if binding reference, ignore in count
                mw += 1
            else:
                m += 1
            afterEsc = False
        elif c == '\\':                   # look for binding reference
            afterEsc = True
        else:
            m += 1

    if afterEsc:                          # count lone \ at end of substitution
        m += 1

#   print 'expansion check: m=' , m , 'n=' , n , 'nw=' , nw , 'mw=' , mw

    return mw + m <= nw + n

#
####
#
# main code for macro tables

class Rule(object):

    """
    hashable rule object for macro table

    attributes:
        patn  - pattern with possible wildcards
        nspm  - space count in pattern
        subs  - substitution for matched text
    """

    def __init__ ( self , patn , nspm , subs ):

        """
        initialize rule

        arguments:
            self  -
            patn  - PyElly pattern
            nspm  - space count in pattern
            subs  - substitution string for matched text
        """

        self.patn = patn
        self.nspm = nspm
        self.subs = subs

    def __str__ ( self ):

        """
        display rule

        arguments:
            self  -
        """

        return str(self.patn) + '(' + str(self.nspm) + ') [ ' + self.subs + ' ]'

    def unpack ( self ):

        """
        get rule elements as a list

        arguments:
            self  -

        returns:
            list of rule attributes: [ patn , nspm , subs ]
        """

        return [ self.patn , self.nspm , self.subs ]

def uniqueAdd ( resl , newl ):

    """
    append unique elements of new list to result list
    while preserving order

    arguments:
        resl  - result list of unique elements
        newl  - list of elements to add
    """

    for r in newl:
        if not r in resl: resl.append(r)

class MacroTable(object):

    """
    table of macro substitutions

    attributes:
        count        - number of patterns altogether
        index        - for macro patterns starting with a text char
        letWx        -   starting with letter  wildcard
        digWx        -            with digit   wildcard
        anyWx        -            with general wildcard
        apoWx        -            with apostrophe

        _errcount    - running input error count
    """

    def __init__ ( self , defs=None , nowarn=False ):

        """
        initialize table for macro rules from file

        arguments:
            self   -
            defs   - EllyDefinitionReader for substitution rules
            nowarn - whether to turn warnings off

        exceptions:
            TableFailure on error
        """

        lim = ellyChar.Max + 11      # number of simple alphabetic + 10 digits + 1
        self.index = [ [ ] for i in range(lim) ] # starting with letter or digit
        self.letWx = [ ]             #                           letter  wildcard
        self.digWx = [ ]             #                           digit   wildcard
        self.anyWx = [ ]             #                           general wildcard
        self.apoWx = [ ]             #                           apostrophe

        self.count = 0               # start with empty table

        self._errcount = 0           # no errors yet

        if defs != None:
            self._store(defs,nowarn) # fill in  macro definitions

    def _err ( self , s='malformed macro substitution' , l='' , d=1 ):

        """
        for error reporting

        arguments:
            self -
            s    - error message
            l    - problem line
            d    - error count increment, 0 = warning only
        """

        self._errcount += d
        m = 'error' if d == 1 else 'WARNING'
        print >> sys.stderr , '** macro ' + m + ':' , s
        if l != '':
            print >> sys.stderr , '*  at [' , l , ']'

    def getRules ( self , a ):

        """
        get appropriate macros for text with specified starting char

        arguments:
            self  -
            a     - first letter of current buffer contents (NOT space!)

        returns:
            a list of unpacked macro rules to try out
        """

#       print 'getRules(a=' , a , ')'
        if a == '': return [ ]
        if ellyChar.isLetterOrDigit(a):
            k = ellyChar.toIndex(a)
            ls = self.index[k]
#           print 'index a=' , a , 'k=' , k
            ws = self.letWx if ellyChar.isLetter(a) else self.digWx
            uniqueAdd(ls,ws)
            uniqueAdd(ls,self.anyWx)
        elif ellyChar.isApostrophe(a):
            ls = self.apoWx
        else:
            ls = self.index[0]
            uniqueAdd(ls,self.anyWx)
#       print len(ls) , ' rules to check'
        return [ r.unpack() for r in ls ]

    def _store ( self , defs , nowarn ):

        """
        put macro substitutions into table with indexing by first char of pattern

        arguments:
            self   -
            defs   - list of macro definition as strings
            nowarn - whether to turn warnings off

        exceptions:
            TableFailure on error
        """

#       print defs.linecount() , 'lines'
        while True:
            l = defs.readline()               # next macro rule
#           print "rule input=" , l
            if len(l) == 0: break             # EOF check
            dl = definitionLine.DefinitionLine(l,False)
            left = dl.left                    # pattern to be matched
            tail = dl.tail                    # transformation to apply to match
#           print 'dl.left=' , left
            if left == None or tail == None:
                self._err(l=l)                # report missing part of rule
                continue
            if left.find(' ') >= 0:           # pattern side of macro rule
                ms = 'pattern in macro contains spaces'
                self._err(s=ms,l=l,d=1)       # cannot contain any space chars
                continue

            lefts = list(left)
#           print 'left=' , lefts
            nspm = ellyWildcard.numSpaces(lefts)
            pat = ellyWildcard.convert(left)  # get pattern with encoded wildcards
            if pat == None:
                self._err('bad wildcards',l)
                continue
#           print 'pat=' , ellyWildcard.deconvert(pat) , 'len=' , len(pat)
#           print 'pat=' , list(pat)
            pe = pat[-1]
            if not pe in [ ellyWildcard.cALL , ellyWildcard.cEND , ellyWildcard.cSPC ]:
                pat += ellyWildcard.cEND      # pattern must end in $ if it does not end in * or _
            if not _checkBindings(pat,tail):
                self._err('bad bindings in substitution',l)
                continue
            if not nowarn and not _checkExpansion(pat,tail):
                self._err('substitution may be longer than original string',l,0)

#           print "rule =" , [ left , nspm , tail ]
            if pat == None:
                self._err('no pattern',l)
                continue

            r = Rule( pat , nspm , tail )

            c = pat[0]                        # first char of pattern
                                              # check type to see how to index rule
#           print 'c=' , ellyWildcard.deconvert(c) , ', pat=' , ellyWildcard.deconvert(pat)
            p = pat
            while c == ellyWildcard.cSOS:     # optional sequence?
                if not cEOS in p:
                    break
                k = p.index(cEOS)             # if so, find the end of sequence
                if k < 0 or k == 1: break     # if no end or empty sequence, stop
                k += 1
                if k == len(pat): break       # should be something after sequence
                m = ellyChar.toIndex(pat[1])  # index by first char of optional sequence
                self.index[m].append(r)       #   (must be non-wildcard)
                p = p[k:]                     # move up in pattern
                c = p[0]                      #   but check for another optional sequence

            if c == ellyWildcard.cSOS:
                self._err(l=l)
                continue                      # bad sequence, skip this rule

#           print 'c=' , ord(c)
            if ellyChar.isLetterOrDigit(c):   # check effective first char of pattern
                m = ellyChar.toIndex(c)
                self.index[m].append(r)       # add to index under alphanumeric char
            elif ellyChar.isText(c):
                self.index[0].append(r)       # add to index under punctuation
            elif not c in ellyWildcard.Matching:
                if c == ellyWildcard.cEND:
                    print >> sys.stderr , '** macro warning: pattern can have empty match'
                    print >> sys.stderr , '*  at [' , l , ']'
                else:
                    dc = '=' + str(ord(c) - ellyWildcard.X)
                    self._err('bad wildcard code' , dc)
                continue
            elif c == ellyWildcard.cANY or c == ellyWildcard.cALL:
                self.anyWx.append(r)          # under general wildcards
            elif c == ellyWildcard.cCAN:
                self.index[0].append(r)       # under punctuation
            elif c == ellyWildcard.cDIG or c == ellyWildcard.cSDG:
                self.digWx.append(r)          # under digit wildcards
            elif c == ellyWildcard.cSAN:
                self.digWx.append(r)          # under both digit and
                self.letWx.append(r)          #   letter wildcards
            elif c == ellyWildcard.cAPO:      # right single quote or apostrophe
                self.apoWx.append(r)          #
            elif c == ellyWildcard.cSPC or c == ellyWildcard.cEND:
                self._err('bad wildcard in context',l)
                continue                      # wildcards unacceptable here
            else:
                self.letWx.append(r)          # everything else under letter wildcard

            self.count += 1                   # count up macro substitution
#           print 'count=' , self.count

        if self._errcount > 0:
            print >> sys.stderr , '**' , self._errcount , 'macro errors in all'
            print >> sys.stderr , 'macro table definition FAILed'
            raise ellyException.TableFailure

    def dump ( self ):

        """
        show contents of macro table

        arguments:
            self
        """

        print 'macro substitutions indexed by first char or wildcard in pattern'
        if len(self.index[0]) > 0:
            print '[.]:'
            _dmpall(self.index[0])
        i = 0
        for slot in self.index:
            if len(slot) > 0:
                if i == 0:
                    print '[ ]:'
                else:
                    print '[' + ellyChar.toChar(i) + ']:'
                _dmpall(slot)
            i += 1
        if len(self.letWx) > 0:
            print '[LETTER]:'
            _dmpall(self.letWx)
        if len(self.digWx) > 0:
            print '[DIGIT]:'
            _dmpall(self.digWx)
        if len(self.anyWx) > 0:
            print '[ANY]:'
            _dmpall(self.anyWx)
        if len(self.apoWx) > 0:
            print '[APOSTROPHE]:'
            _dmpall(self.apoWx)

def _dmpall ( slot ):

    """
    show all rules for one index slot

    arguments:
        slot  - index slot
    """

    for r in slot:
        print u' {:16s}'.format(ellyWildcard.deconvert(r.patn)) ,
        print u'    ({:2d} spWC)'.format(r.nspm) ,
        print '->' , list(r.subs)

#
# unit test
#

if __name__ == '__main__':
    import substitutionBuffer
    import ellyDefinitionReader
    import ellyConfiguration

    base = ellyConfiguration.baseSource
    name = sys.argv[1] if len(sys.argv) > 1 else 'test'
    dfns = base + name + '.m.elly'

    print 'source=' , dfns
    inp = ellyDefinitionReader.EllyDefinitionReader(dfns)

    if inp.error != None:
        print inp.error
        sys.exit(1)

    try:
        mtb = MacroTable(inp)          # create macro table from specified definition file
    except ellyException.TableFailure:
        sys.exit(1)                    # quit on failure

#   print 'mtb=' , mtb , 'with' , mtb.count , 'patterns'
    if mtb.count == 0:                 # check for success
        print >> sys.stderr , 'empty table'
        sys.exit(1)                    # quit on no table
    print ''
    mtb.dump()

#######################################################################
# this code will test macro substitution indirectly through a PyElly  #
# substitutionBuffer, which supports basic tokenization from a stream #
# of input text; it does NONE of the tokenization associated with     #
# recognizing token types by character patterns, entity extraction or #
# vocabulary table lookup                                             #
#######################################################################

    sb = substitutionBuffer.SubstitutionBuffer(mtb)
    while True:
        sys.stdout.write('\n> ')
        st = sys.stdin.readline()      # get test input
        if len(st) <= 1: break
        ss = st.decode('utf8').strip() # convert to Unicode
        print 'RAW =' , st.strip()
        print 'TEXT=' , list(ss) , '(' + str(len(ss)) + ')'
        sb.clear()
        sb.append(ss)
        print ' '

        no = 0
        while True:
            print '+' , sb.buffer
            to = sb.getNext()
            if to == None: break
            no += 1
            print ' >>{:2d}: '.format(no) , unicode(to)

    sys.stdout.write('\n')
