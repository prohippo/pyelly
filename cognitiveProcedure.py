#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# cognitiveProcedure.py : 29jun2014 CPM
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
procedure to determine plausibility of phrase in Elly parse
"""

import ellyBits
import semanticCommand
import featureSpecification
import cognitiveDefiner

class CognitiveProcedure(object):

    """
    cognitive semantic procedure attached to grammar rule

    attributes:
        logic   - code and data for procedure
    """
 
    def __init__ ( self , syms , defn ):

        """
        initialization from EllyDefinitionReader input

        arguments:
            self  -
            defn  - EllyDefinitionReader
        """

        self.logic = cognitiveDefiner.convertDefinition(syms,defn)

    def score ( self , cntx , phrs ):

        """
        compute plausibility score

        arguments:
            self  -
            cntx  - interpretive context
            phrs  - associated phrase

        returns:
            integer plausibility score
        """

        if self.logic == None: return 0

        sum = 0               # to accumulate plausibility score

        for c in self.logic:  # go through all clauses

            concept = None    # for communicating from predicate side to action side
            value   = None    # of clauses

            for p in c[0]:    # go through all predicates of clause
                op = p[0]
                if op == semanticCommand.Clftf or op == semanticCommand.Crhtf:
                    # test features of descendants
                    dph = phrs.lftd if op == semanticCommand.Clftf else phrs.rhtd
                    bts = dph.semf.compound()
                    if not ellyBits.check(p[1],bts): break
                elif op == semanticCommand.Clftc or op == semanticCommand.Crhtc:
                    # check concepts of descendants
                    dph = phrs.lftd if op == semanticCommand.Clftc else phrs.rhtd
                    cns = dph.cons
                    cx = p[1]
                    mxw = -1
                    if cx == '*':
                        for c in cns:
                            w = cntx.wghtg.interpretConcept(c)
                            if mxw < w: mxw = w
                        if mxw < 0: break
                    else:
                        for c in cns:
                            w = cntx.wghtg.hier.isA(c,cx)
                            if mxw < w: mxw = w
                        if mxw < 0: break
                    cntx.wghtg.noteConcept(c)
                    value = mxw
                elif op == semanticCommand.Cbthc:
                    # check conceptual relatedness of descendants
                    lcns = phrs.lftd.cons
                    rcns = phrs.rhtd.cons
                    mxw = 0
                    mxc = None
                    for lc in lcns:
                        for rc in rcns:
                            w = cntx.wghtg.relateConceptPair(lc,rc)
                            if mxw < w:
                                mxw = w
                                mxc = cntx.wghtg.hier.intersection()
                    if mxw <= 0: break
                    value = mxw
                    concept = mxc
                    cntx.wghtg.note(mxc)
                else:
                    # unknown command
                    break

            else:             # execute actions of clause if ALL predicates satisfied
                for a in c[1]:                        # get mext action
                    op = a[0]
                    if op == semanticCommand.Cadd:    # add to score?
                        sum += a[1]
                    elif op == semanticCommand.Clhr:  # inherit from left descendant?
                        phrs.semf.combine(phrs.lftd.semf)
                        phrs.cncp = phrs.lftd.cncp
                    elif op == semanticCommand.Crhr:  # inherit from right?
                        phrs.semf.combine(phrs.rhtd.semf)
                        phrs.cncp = phrs.rhtd.cncp
                    elif op == semanticCommand.Csetf: # set semantic features?
                        phrs.semf.combine(a[1])
                    elif op == semanticCommand.Csetc: # set concepts?
                        phrs.cncp = a[1]

        rul = phrs.rule
        if rul.nmrg == 2:
            sum += cntx.wghtg.relateConceptPair(phrs.lftd.cncp,phrs.rhtd.cncp)
        return sum

#
# unit test
#

if __name__ == '__main__':

    import sys
    import ellyDefinitionReader
    import procedureTestFrame

    frame = procedureTestFrame.ProcedureTestFrame()
    phr = frame.phrase
    ctx = frame.context
    stb = ctx.syms

    src = sys.argv[1] if len(sys.argv) > 1 else 'cognitiveDefinerTest.txt'
    inp = ellyDefinitionReader.EllyDefinitionReader(src)
    if inp.error != None:
        sys.exit(1)
    cgs = CognitiveProcedure(stb,inp)
    if cgs == None:
        print >> sys.stderr, "conversion error"
        sys.exit(1)

    cognitiveDefiner.showCode(cgs.logic)

    s = cgs.score(ctx,phr)
    print 'plausibility=',s
