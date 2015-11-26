#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# macroTable.py : 26nov2015 CPM
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
    return (m <= n) # must be as many wildcard sequences as maximum binding

def _checkExpansion ( left , right ):

    """
    check that substitution does not produce more non-space chars
    ignoring pattern wildcards and substitutions dependent on bindings

    arguments:
        left  - pattern
        right - substitution

    returns:
        True if substitution is not longer than original string, False otherwise
    """

#   print 'EXPN: left=' , left , 'right=' , right
    nh = 0          # hypen count in pattern
    n = 0           # non-space char count in pattern
    k = 0
    l = len(left)
    while k < l:    # iterate on pattern string
        c = left[k]
        k += 1
        if c == '-':
            n += 1
            nh += 1
        elif c != ' ' and c != '_':    # look at non-space chars
            if not ellyWildcard.isWild(c):
                n += 1

    mh = 0          # hyphen count in substitution
    m = 0           # non-space char count in substitution
    k = 0
    l = len(right)
    while k < l:    # iterate on substitution string
        c = right[k]
        k += 1
        if c == '-':
            m += 1
            mh += 1
        elif c != ' ' and c != '_':    # look at non-space chars
            if k == l:
                m += 1
            elif c == '\\':            # look for binding with \
                d = right[k]
                if '1' > d or d > '9': # if not binding, treat as non-space
                    m += 1
                else:
                    k += 1
            else:
                m += 1

#   print 'EXPN: m=' , m , 'n=' , n

    if m <= n: return True

    n -= nh         # another way to avoid warning
    m -= mh         #

    return (m <= n)

#
####
#
# main code for macro tables

class MacroTable(object):

    """
    table of macro substitutions

    attributes:
        count        - number of patterns altogether
        index        - for macro patterns starting with a text char
        letWx        -   starting with letter  wildcard
        digWx        -            with digit   wildcard
        anyWx        -            with general wildcard

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
        self.index = [ [ ]
            for i in range(lim) ]    # slots for patterns starting with letter or digit
        self.letWx = [ ]             # slot                             letter  wildcard
        self.digWx = [ ]             #                                  digit   wildcard
        self.anyWx = [ ]             #                                  general wildcard

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
        m = 'error' if d == 1 else 'warning'
        print >> sys.stderr , '** macro ' + m + ':' , s
        if l != '':
            print >> sys.stderr , '*  at [' , l , ']'

    def getRules ( self , a ):

        """
        get appropriate macros for text starting with specified first char

        arguments:
            self  -
            a     - first letter of current buffer contents (NOT space!)

        returns:
            a list of macro rules to try out
        """

        if a == '': return [ ]
        if ellyChar.isLetterOrDigit(a):
            k = ellyChar.toIndex(a)
#           print 'index a=' , a , 'k=' , k
            ws = self.letWx if ellyChar.isLetter(a) else self.digWx
            ls = self.index[k] + ws + self.anyWx
        else:
            ls = self.index[0] + self.anyWx
#       print len(ls) , ' rules to check'
        return ls

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
            if left == None or tail == None:
                self._err(l=l)                # report missing part of rule
                continue
            pat = ellyWildcard.convert(left)  # get pattern with encoded wildcards
            if pat == None:
                self._err('bad wildcards',l)
                continue
            pe = pat[-1]
            if pe != ellyWildcard.cALL and pe != ellyWildcard.cEND:
                pat += ellyWildcard.cEND      # pattern must end in $ if it does not end in *
            if not _checkBindings(pat,tail):
                self._err('bad bindings in substitution',l)
                continue
            if not nowarn and not _checkExpansion(pat,tail):
                self._err('substitution longer than original string',l,0)
#           print "rule =" , [ left , tail ]
            if pat == None:
                self._err('no pattern',l)
                continue
            r = [ pat , tail ]
            c = pat[0]                        # first char of pattern
                                              # check type to see how to index rule
#           print 'c=' , ellyWildcard.deconvert(c) , ', pat=' , ellyWildcard.deconvert(pat)
            p = pat
            while c == ellyWildcard.cSOS:     # optional sequence?
                k = p.find(ellyWildcard.cEOS) # if so, find the end of sequence
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

        print 'macro substitutions indexed by first char or wildcard'
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

def _dmpall ( slot ):

    """
    show all rules for one index slot

    arguments:
        slot  - index slot
    """

    for r in slot:
        print u' {:16s}'.format(ellyWildcard.deconvert(r[0])) + ' -> ' , list(r[1])

#
# unit test
#

if __name__ == '__main__':

    import substitutionBuffer
    import ellyDefinitionReader
    import ellyConfiguration

    base = ellyConfiguration.baseSource + '/'
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
    print ''
    print 'mtb=' , mtb , 'with' , mtb.count , 'patterns'
    if mtb.count == 0:                 # check for success
        print >> sys.stderr , 'empty table'
        sys.exit(1)                    # quit on no table
    print ''
    mtb.dump()

    sb = substitutionBuffer.SubstitutionBuffer(mtb)
    while True:
        sys.stdout.write('> ')
        st = sys.stdin.readline()      # get test input
        if len(st) <= 1: break
        ss = st.decode('utf8').strip() # convert to Unicode
        print 'TEXT=' , list(ss) , '(' + str(len(ss)) + ')'
        sb.clear()
        sb.append(ss)

        no = 0
        while True:
            to = sb.getNext()
            if to == None: break
            no += 1
            print ' >>{:2d}'.format(no) , unicode(to)

    sys.stdout.write('\n')
