#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# dumpEllyGrammar.py : 05jun2014 CPM
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
methods to dump a grammar table
"""

import cognitiveDefiner
import generativeDefiner

def dumpAll ( symbols , table , level ):

    """
    show the rules in an Elly grammar table

    arguments:
        symbols - symbol table
        table   - grammar table
        level   - degree of detail
    """

    print len(symbols.ntindx) , 'syntactic categories'

    dumpInitializations(table.initzn)
    dumpMatrix(symbols,table.mat)
    dumpFeatures(symbols)
    dumpSubprocedures(table.pndx,level > 0)
    dumpSplits(symbols,table.splits,level > 2)
    dumpExtensions(symbols,table.extens,level > 2)
    dumpDictionary(symbols,table.dctn,level > 1)

    print "DONE"

def dumpInitializations ( inits ):

    """
    show global variable initializations

    arguments:
        inits  - DerivabilityMatrix object
    """

    print ""
    print "Global Variable Initializations"
    print "-------------------------------------------------"

    for x in inits:
        print '{:<12.12s} = '.format(x[0]) , x[1]

def dumpMatrix ( stb , matrix ):

    """
    show derivability matrix

    arguments:
        stb     - symbol table
        matrix  - DerivabilityMatrix object
    """

    print ""
    print "Derivability Matrix for Syntactic Structure Types"
    print "-------------------------------------------------"

    mat = matrix.dm
    ntno = len(stb.ntindx)
    for i in range(ntno):
        print '{:2} '.format(i) ,
        print '{:<6.6s} : '.format(stb.ntname[i]) ,
        bmr = mat[i]
        for j in range(ntno):
            if i != j and bmr.test(j):
                print '{} '.format(stb.ntname[j]) ,
        print ""
        print "    " + bmr.hexadecimal() + " " + str(bmr.count()) + ' bytes'

def dumpCategories ( stb ):

    """
    show syntactic categories

    arguments:
        stb     - symbol table
    """

    ntno = len(stb.ntname)
    for i in range(ntno):
        print '{:2}'.format(i) , stb.ntname[i]

def dumpFeatures ( stb ):

    """
    show feature sets

    arguments:
        stb     - symbol table

    """

    print ""
    print "Feature Sets"
    print "------------"

    lb = [ 'syntactic' , 'semantic' ]
    for fs in [ stb.sxindx , stb.smindx ]:
        lbl = lb.pop(0)
        print '----' , lbl
        fids = fs.keys()
        nols = len(fids)
        for i in range(nols):
            id = fids[i]
            fl = fs[id].keys()
            print '[{0:2}] {1} '.format(i,id) ,
            for f in fl:
                print f + ' ' ,
            print ""

def dumpSubprocedures ( index , all ):

    """
    show standalone procedures

    arguments:
        index  - procedure index
        all    - flag for full dump
    """

    print ""
    print "Semantic Subprocedures"
    print "----------------------"

    lps = index.keys()
    for p in lps:
        print ""
        print p
        if all:
            generativeDefiner.showCode(index[p].logic);

def showMask ( msk ):

    """
    produce hexadecimal representation of feature mask

    arguments:
        msk  - bit string for mask

    returns:
        hexadecimal string
    """

    ln = len(msk)/2
    hi = msk[ln:]
    lo = msk[:ln]

    sb = [ ]
    sb.append('+')
    for i in range(ln):
        sb.append('{:02x}'.format(lo[i]))
    sb.append('-')
    for i in range(ln):
        sb.append('{:02x}'.format(hi[i]))

    return ''.join(sb)

def showProcedures ( stb , r ):

    """
    show semantic procedures for rule

    arguments:
        stb  - symbol table
        r    - rule
    """

    print '  ** cognitive'
    if r.cogs != None:
        cognitiveDefiner.showCode(r.cogs.logic)
    print '  ** generative'
    if r.gens != None:
        generativeDefiner.showCode(r.gens.logic);
    print ''

def dumpSplits ( stb , splits , all ):

    """
    show 2-branch rules

    arguments: 
        stb    - symbol table
        splits - listing of 2-branch rules
        all    - flag for full dump
    """

    print ""
    print "Splitting Rules"
    print "---------------"

    no = 0
    for i in range(len(splits)):
        rv = splits[i]
        k = len(rv);
        if k == 0:
            continue

        ty = stb.ntname[i]

        for j in range(k):
            r = rv[j]
            print '(' + str(r.seqn) + ')' ,
            print stb.ntname[r.styp] ,
            print '[{}]->'.format(r.sfet.hexadecimal(False)) ,
            print ty + ' ' + showMask(r.ltfet) + ' ' ,
            print stb.ntname[r.rtyp] + ' ' + showMask(r.rtfet)

            if all: showProcedures(stb,r)

        no += k

    print no , "2-branch rules"

def dumpExtensions ( stb, extens , all ):

    """
    show 1-branch rules

    arguments:
        stb    - symbol table
        extens - listing of 1-branch rules
        all    - flag for full dump
    """

    print ''
    print "Extending Rules"
    print "---------------"

    no = 0

    for i in range(len(extens)):
        rv = extens[i]
        k = len(rv)
        if k == 0:
            continue

        ty = stb.ntname[i]

        for r in rv:
            print '(' + str(r.seqn) + ')' ,
            print stb.ntname[r.styp] ,
            print '[{}]->'.format(r.sfet.hexadecimal(False)) ,
            print ty + ' ' + showMask(r.utfet) 

            if all: showProcedures(stb,r)

        no += k

    print no , "1-branch rules"

def dumpDictionary ( stb, dctn , all ):

    """
    dump grammar dictionary

    arguments:
        stb   - symbol table
        dctn  - dictionary
        all   - flag for full dump
    """

    print ''
    print "Dictionary Entries"
    print "------------------"

    no = 0

    ws = dctn.keys()

    for w in ws:

        dv = dctn[w]

        k = len(dv)
        if k == 0:
            continue

        for dr in dv:
            print stb.ntname[dr.styp] ,
            print '[{}]->'.format(dr.sfet.hexadecimal(False)) ,
            print '"' + w + '"'

            if all: showProcedures(stb,dr)

        no += k;

    print len(dctn) , 'unique words in' , no , "entries"
