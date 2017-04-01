#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# cognitiveDefiner.py : 30mar2017 CPM
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
define cognitive semantics to compute plausibility scores for phrases
assigning positive or negative votes according to individual semantic
characteristics of phrases
"""

import ellyBits
import ellyChar
import ellyException
import semanticCommand
import featureSpecification
import symbolTable
import sys

_check = [ (lambda s : True)  ,
           (lambda s : symbolTable.featureConsistencyExtend(s.res,s.lft,s.rht,s.lh,s.rh)) ,
           (lambda s : symbolTable.featureConsistencySplit (s.res,s.lft,s.rht,s.lh,s.rh)) ]

class Status(object):
    """
    to group arguments for feature inheritance checking
    """
    def __init__ (self):
        self.res = None
        self.lft = None
        self.rht = None
        self.lh  = False
        self.rh  = False
        self.id  = None

def convertDefinition ( stb , inp , nwy ):

    """
    defines cognitive semantic procedure for a syntax rule

    arguments:
        stb   - symbol table
        inp   - EllyDefinitionReader for procedure definition
        nwy   - 0 = vocabulary
                1 = extending rule
                2 = splitting rule

    returns:
        procedure body as a list of commands and data on success, None otherwise
    """

    id = [None]*3 # for feaature id consistency check

    store = [ ]   # where to put resulting procedure

    while True:   # process every clause

        s = Status()                                  # initialize for inheritance check
        s.id = id                                     #

        line = inp.readline()                         # get next input line
        if len(line) == 0: break                      # end of input test
#       print "cog def:",line

        elem = line.lower().split('>>')               # mandatory for all clauses
        if len(elem) < 2:
            print >> sys.stderr , '** incomplete cognitive semantic clause'
            return None
        if elem[0].strip() == '?' and elem[1].strip() == '?':
            left  = [ [ semanticCommand.Ctrc , [ ] ] ]
            right = [ ]
        else:
            left  = _leftside (stb,elem[0].strip(),s) # conditions for clause
            right = _rightside(stb,elem[1].strip(),s) # actions
            if left == None or right == None:
                return None
        if not (_check[nwy])(s):                      # apply inheritance check by rule type
            print >> sys.stderr , '** bad semantic feature inheritance'
            return None
        store.append([ left , right ])                # save clause

    return store

def _err ( ms ):

    """
    show an error message
    arguments:
        ms  - message string
    returns:
        None
    """

    print >> sys.stderr , '** cognitive semantic error:' , ms
    return None

sS = 0  # indices for feature ids in status frame
lS = 1  #
rS = 2  #

def _leftside ( stb , txt , sta ):

    """
    process conditions for a clause and store

    arguments:
        stb  - symbol table
        txt  - string input for left side of single clause
        sta   - for status reporting

    returns:
        predicate list on success, None otherwise
    """

#   print "left side"
    pred = [ ]
    txt = txt.rstrip()

    while len(txt) > 0:
        txt = txt.lstrip()
#       print 'clause=' , txt
        if len(txt) <= 1:
            _err('malformed conditions for clause')
            return None
        side = txt[0]
        txt = txt[1:]

        if side == 'n' or side == 'p':
            sns = txt[0]
            txt = txt[1:]
            if sns != '<' and sns != '>':
                _err('invalid comparison in clause condition=' + sns)
                return None
            if side == 'n':
                op = semanticCommand.Cngt if sns == '>' else semanticCommand.Cnlt
            else:
                op = semanticCommand.Cpgt if sns == '>' else semanticCommand.Cplt
            nd = 0
            lt = len(txt)
            while nd < lt:
                if not ellyChar.isDigit(txt[nd]): break
                nd += 1
            if nd == 0:
                _err('no token count for condition')
                return None
            test = int(txt[:nd])
            txt = txt[nd:]
            pred.append([ op , test ])
            continue
        k = 0
        if txt[0] == '[':                   # semantic feature check?
            k = txt.find(']')               # if so, look for closing bracket
            if k < 0:
                return _err('incomplete semantic features to check')
            p = txt[:k+1]                   # get semantic feature string

#           print "side:" , side , "test:" , p

            try:
                f = featureSpecification.FeatureSpecification(stb,p,'semantic')
            except ellyException.FormatFailure:
                return _err('bad semantic features to check')

            if side == 'l':
                if sta.id[lS] == None:
                    sta.id[lS] = f.id
                elif f.id != sta.id[lS]:
                    _err('inconsistency: left features=' + p)
                    return None
            else:
                if sta.id[rS] == None:
                    sta.id[rS] = f.id
                elif f.id != sta.id[rS]:
                    _err('inconsistency: right features=' + p)
                    return None

            op = semanticCommand.Crhtf if side == 'r' else semanticCommand.Clftf

            if side == 'r':
                sta.rht = f
            else:
                sta.lft = f
#           print 'test:' , f.positive.hexadecimal() , f.negative.hexadecimal()
            test = ellyBits.join(f.positive,f.negative)
#           print test
            pred.append([ op , test ])

        elif txt[0] == '(':                 # semantic concept check?
#           print "txt=\"" + txt +"\""
            k = txt.find(')')               # if so, look for closing parenthesis
            if k < 0:
                return _err('incomplete concept check')
            s = txt[1:k].strip().upper()    # normalize concepts
            p = s.split(',')                # allow for multiple disjunctive checks
#           print "p=\"" + p + "\""

            op = semanticCommand.Crhtc if side == 'r' else semanticCommand.Clftc
            pred.append([ op , p ])

        txt = txt[k+1:].lstrip()            # advance to next predicate

#       print "NEXT"

    return pred

def _rightside ( stb , txt ,sta ):

    """
    process actions for a clause

    arguments:
        stb   - symbol table
        txt   - string input for single clause
        sta   - for status reporting

    returns:
        action list on success, None otherwise
    """

#   print "right side"

    actn = [ ]
    val  = 0
    cnc  = ''                        # default is no concept specified

    m = txt.rfind(']')               # look for semantic features to set or reset
    n = txt.rfind(' ')               # look for space marking explicit concept

#   print 'n=',n
#   print "0 txt=[" , txt , "]"

    if n > m:                        # space must not be in semantic feature specification
        cnc = txt[n:].strip().upper()
        txt = txt[:n]                # remove concept from right size of clause

#   print "1 txt=[" , txt , "]"

    if len(txt) > 1:

        if txt[0] == '*':            # inherit from phrase component?
            c = txt[1]
            if c == 'l':
                actn.append([ semanticCommand.Clhr ])
                sta.lh = True
            elif c == 'r':
                actn.append([ semanticCommand.Crhr ])
                sta.rh = True
            else:
                return _err('bad inheritance')
            txt = txt[2:].strip()

#   print "2 txt=[" , txt , "]"

    if len(txt) > 3 and txt[0] == '[':

        n = txt.find(']')        # set or unset semantic features for phrase?
#       print 'n=' , n
        if n < 3:
            return _err('incomplete semantic features to set or unset')
        try:
            f = featureSpecification.FeatureSpecification(stb,txt[:n+1],semantic=True)
            sta.res = f
        except ellyException.FormatFailure:
            return _err('bad semantic features to set or unset')

        if sta.id[sS] == None:
            sta.id[sS] = f.id
        elif f.id != sta.id[sS]:
            _err('inconsistency: final features=' + txt[:n+1])
            return None

#       print 'features=' , f.positive , f.negative
        actn.append([ semanticCommand.Csetf , f.positive ])
        if not f.negative.zeroed():
            f.negative.complement()
            actn.append([ semanticCommand.Crstf , f.negative ])
#       print 'set:' , actn[-1]
        txt = txt[n+1:]

#   print "3 txt=[" , txt , "]"

    if len(txt) > 0:

        c = txt[0]                   # check for sign of plausibility change

        if c != '+' and c != '-':
            if ellyChar.isDigit(c):
                return _err('plausibility must begin with + or -')
            else:
                return _err('bad cognitive semantic action: ' + txt)

#       print "2 txt=[",txt,"]"

        if len(txt) == 1:
            val = 1
        elif ellyChar.isDigit(txt[1]):
            try:
                val = int(txt[1:])   # explicit numerical change
            except ValueError:
                return _err('bad cognitive plausibility: ' + txt)
        elif c == txt[1]:            # alternate notation for plausibility change
            val = 2
            for xc in txt[2:]:
                if xc != c:
                    return _err('must be all + or all -')
                val += 1             # count up value
        else:
            return _err('cannot interpret clause: ' + txt)

        if c == '-': val = -val      # get right sign

#   print 'val=' , val

    if len(cnc) > 0:
        actn.append([ semanticCommand.Csetc , cnc ])

    if val != 0:
        actn.append([ semanticCommand.Cadd , val ])

    return actn

cmprcode = [
    semanticCommand.Cngt , semanticCommand.Cnlt ,
    semanticCommand.Cpgt , semanticCommand.Cplt
]

def showCode ( cod ):

    """
    show compiled cognitive semantic code

    arguments:
        cod   - code to display
    """

    if cod == None:
        print 'No code'
        return

    for c in cod:  # iterate on clauses

        pred = c[0]
        prs = [ ]  # to collect conditional predicates of cognitive clause
        for p in pred:
            opn = p[0]
            arg = p[1]
            if opn == semanticCommand.Clftf or opn == semanticCommand.Crhtf:
#               print 'double bit arg =' , arg
                s = ellyBits.show(arg)
            elif opn in cmprcode:
                s = str(arg)
            else:
#               print 'cnc args=' , arg
                s = ",".join(arg)
            prs.append(semanticCommand.Copn[opn] + ' ' + s)
        print '|' ,
        if len(prs) > 0: print ' and '.join(prs) ,
        print '>>' ,
        actn = c[1]
        acs = [ ]  # to collect actions of cognitive clause
        for a in actn:
            opn = a[0]
            arg = a[1] if len(a) > 1 else ''
            if opn == semanticCommand.Csetf or opn == semanticCommand.Crstf:
#               print 'single bit arg =' , arg
                s = arg.hexadecimal(False)
            else:
                s = str(arg)
            acs.append(semanticCommand.Copn[opn] + ' ' + s)
        print ', '.join(acs)

#
# unit test
#

if __name__ == "__main__":

    import ellyDefinitionReader

    ustb = symbolTable.SymbolTable()

    usrc = sys.argv[1] if len(sys.argv) > 1 else 'cognitiveDefinerTest.txt'

    uinp = ellyDefinitionReader.EllyDefinitionReader(usrc)

    if uinp.error != None:
        print >> sys.stderr, uinp.error
        sys.exit(1)

    ucod = convertDefinition(ustb,uinp,2)
    if ucod == None:
        print >> sys.stderr, "conversion error"
        sys.exit(1)

    print len(ucod),"clauses from" , usrc

    showCode(ucod)
