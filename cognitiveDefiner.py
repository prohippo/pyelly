#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# cognitiveDefiner.py : 22oct2013 CPM
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
import semanticCommand
import featureSpecification

def convertDefinition ( stb , inp ):

    """ 
    defines cognitive semantic procedure for a syntax rule

    arguments:
        stb   - symbol table
        inp   - EllyDefinitionReader for procedure definition

    returns:
        procedure body as a list of commands and data on success, None otherwise
    """

    store = [ ]  # where to put resulting procedure

    while True:  # process every clause

        line = inp.readline()
        if len(line) == 0: break
#       print "cog def:",line

        elem = line.lower().split('>>')         # mandatory for all clauses
        if len(elem) < 2 or len(elem[1]) == 0: return None
        left  = _leftside (stb,elem[0].strip()) # conditions for clause
        right = _rightside(stb,elem[1].strip()) # actions
        if left == None or right == None: return None
        store.append([ left , right ])          # save clause
        
    return store

def _leftside ( stb , txt ):

    """
    process conditions for a clause and store

    arguments:
        stb  - symbol table
        txt  - string input for single clause

    returns:
        predicate list on success, None otherwise
    """
#   print "left side"
    pred = [ ]
    if len(txt) == 0: return pred
    ps = txt.split('&')
#   print len(ps),"components",ps
    for p in ps:
        p = p.strip()
        if len(p) == 0: continue
        side = p[0]                       # left or right
        if p[1] == '[' and p[-1] ==']':   # semantic feature check?

#           print "condition:",p
            f = featureSpecification.FeatureSpecification(stb,p[1:],'semantic')
            if f == None or side == 'b': return None
            op = semanticCommand.Clftf if side == 'l' else semanticCommand.Crhtf
#           print 'test:' , f.positive.hexadecimal() , f.negative.hexadecimal()
            test = ellyBits.join(f.positive,f.negative)
            pred.append([ op , test ])

        elif p[0] == '(' and p[-1] == ')': # semantic concept check?

            cs = p[1:-1].split(',')
            if side == 'b':
                if len(cs) != 2: return None
                pred.append([ semanticCommand.Cbthc , cs[0].strip() , cs[1].strip() ])
            else:
                op = semanticCommand.Clftc if side == 'l' else semanticCommand.Crhtc
                pred.append([ op , cs[0].strip() ])

#       print "NEXT" 

    return pred

def _rightside ( stb , txt ):

    """
    process actions for a clause

    arguments:
        stb   - symbol table
        txt   - string input for single clause

    returns:
        action list on success, None otherwise
    """

#   print "right side"
    actn = [ ]

    n = txt.rfind(' ')           # look at final action
#   print n,txt

    if n < 0:
        inc = txt                # only single action specified
        txt = ''
    else:
        inc = txt[n+1:]          # otherwise break off last action
#       print "inc=[",inc,"]"
        txt = txt[:n].strip()

    if len(inc) < 1: return None # must be present

    c = inc[0]                   # check for sign of plausibility change

    if c != '+' and c != '-':
        return None              # must begin with + or -

    if len(inc) == 1:            
        val = 1
    elif ellyChar.isDigit(inc[1]):
        try:
            val = int(inc[1:])   # explicit numerical change
        except:
            print >> sys.stderr , 'bad cognitive plausibility' , txt + ' ' + inc
            return None
    elif c == inc[1]:            # alternate notation for plausibility change
        val = 2
        for xc in inc[2:]:
            if xc != c: return None
            val += 1             # count up value
    else:
        return None

    if c == '-': val = -val      # get right sign

    ret = [ semanticCommand.Cadd , val ]

    if len(txt) > 1:
        if txt[0] == '*':  # inherit from phrase component?
            c = txt[1]
            if c == 'l':
                actn.append([ semanticCommand.Clhr ])
            elif c == 'r':
                actn.append([ semanticCommand.Crhr ])
            else:
                return None
            txt = txt[2:].strip()

    while len(txt) > 0:

        x = txt[0]
        if x == '(':       # set concepts for phrase?
            n = txt.find(')')
            if n < 0: return None
            cs = txt[1:n].split(',')
            sq = [ semanticCommand.Csetc ]
            for c in cs:
                c = c.strip()
                sq.append(c)
        elif x == '[':     # set semantic features for phrase?
            n = txt.find(']')
            if n < 0: return None
            f = featureSpecification.FeatureSpecification(stb,txt[:n+1],semantic=True)
            if f == None: return None
            sq = [ semanticCommand.Csetf , f ]
        else:
            return None

        txt = txt[n+1:].strip()
        actn.append(sq)

    actn.append(ret)
    return actn

def showCode ( cod ):

    """
    show cognitive semantic code

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
            op = p[0]
            p = p[1:]
            if len(p) == 1 and type(p[0]) != 'unicode':
                s = ellyBits.show(p[0])
            else:
                s = str(p)
            prs.append(semanticCommand.Copn[op] + ' ' + s)
        print '>' ,
        if len(prs) > 0: print ' and '.join(prs) , 
        print '>>' ,
        actn = c[1]
        acs = [ ]  # to collect actions of cognitive clause
        for a in actn:
            op = a[0]
            a = a[1:]
            acs.append(semanticCommand.Copn[op] + ' ' + str(a))
        print ', '.join(acs)

#
# unit test
#

if __name__ == "__main__":

    import sys
    import ellyDefinitionReader
    import symbolTable

    stb = symbolTable.SymbolTable()

    src = sys.argv[1] if len(sys.argv) > 1 else 'cognitiveDefinerTest.txt'

    inp = ellyDefinitionReader.EllyDefinitionReader(src)

    if inp.error != None:
        sys.exit(1)

    cod = convertDefinition(stb,inp)
    if cod == None:
        print >> sys.stderr, "conversion error"
        sys.exit(1)

    print len(cod),"clauses from" , src

    showCode(cod)
