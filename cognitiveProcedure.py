#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# cognitiveProcedure.py : 17jun2015 CPM
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

import sys
import ellyBits
import semanticCommand
import cognitiveDefiner
import ellyException

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
#       print 'cognitive scoring'

        trce = False           # enable diagnostic tracing
        clno = 0               # clause index
        psum = 0               # to accumulate plausibility score

        for cls in self.logic: # go through all clauses

            clno += 1
            for p in cls[0]:   # go through all predicates of clause
                op = p[0]
                if phrs.lftd == None:
                    pass
                elif op == semanticCommand.Ctrc:
                    print >> sys.stderr , ''
                    print >> sys.stderr , '  tracing phrase' , phrs.seqn , 'rul=' , phrs.rule.seqn
                    trce = True
                    break
                elif op == semanticCommand.Clftf or op == semanticCommand.Crhtf:
                    # test features of descendants
                    dph = ( phrs.lftd if op == semanticCommand.Clftf or phrs.rhtd == None
                            else phrs.rhtd )
                    bts = dph.semf.compound()
                    if not ellyBits.check(p[1],bts): break
                elif op == semanticCommand.Clftc or op == semanticCommand.Crhtc:
                    # check concepts of descendants
                    dph = ( phrs.lftd if op == semanticCommand.Clftc or phrs.rhtd == None
                            else phrs.rhtd )
                    cnc = dph.cons
                    cx = p[1]  # concepts to check against
                    mxw = -1
                    mxc = None
                    for c in cx:
                        w = cntx.wghtg.hier.isA(cnc,c)
                        if mxw < w:
                            mxw = w
                            mxc = c
                    if mxw < 0: break
                    cntx.wghtg.noteConcept(mxc)
                else:
                    # unknown command
                    print >> sys.stderr , 'bad cog sem action=' , op
                    break

            else:             # execute actions of clause if ALL predicates satisfied
                if trce:
                    print >> sys.stderr , '  cog sem at clause' , clno
                    print >> sys.stderr , '  l:' , phrs.lftd
                    print >> sys.stderr , '  r:' , phrs.rhtd
                for a in cls[1]:                      # get next action
                    op = a[0]
                    if op == semanticCommand.Cadd:    # add to score?
                        psum += a[1]
                    elif op == semanticCommand.Csetf: # set semantic features?
                        phrs.semf.combine(a[1])
                    elif op == semanticCommand.Csetc: # set concepts?
                        phrs.cncp = a[1]
                    elif phrs.lftd == None:
                        pass
                    elif op == semanticCommand.Clhr:  # inherit from left descendant?
                        phrs.semf.combine(phrs.lftd.semf)
                        phrs.cncp = phrs.lftd.cncp
                    elif op == semanticCommand.Crhr:  # inherit from right?
                        dsc = phrs.rhtd if phrs.rhtd != None else phrs.lftd
                        phrs.semf.combine(dsc.semf)
                        phrs.cncp = dsc.cncp

                break  # ignore subsequent clauses on taking action

        inc = 0                  # compute conceptual contribution
        rwy = phrs.rule.nmrg
#       print >> sys.stderr , 'conceptual plausibility'
        if rwy == 2:             # 2-branch splitting rule?
#           print '2-branch!'
            inc = cntx.wghtg.relateConceptPair(phrs.lftd.cncp,phrs.rhtd.cncp)
#           print >> sys.stderr , phrs.lftd.cncp , ':' , phrs.rhtd.cncp , '=' , inc , '!'
            if inc > 1:
                phrs.ctxc = cntx.wghtg.getIntersection()
#           print >> sys.stderr , '2-way bias incr=' , inc
        elif phrs.lftd != None:  # 1-branch extending rule?
#           print >> sys.stderr , '1-branch!'
            dst = cntx.wghtg.interpretConcept(phrs.lftd.cncp)
            if dst > 0:
                phrs.ctxc = cntx.wghtg.getIntersection()
                inc = 1
#           print >> sys.stderr , '1-way bias incr=' , inc
        if inc > 0: psum += inc  # only positive increments contribute
#       print >> sys.stderr , 'phrase' , phrs.seqn, 'intersect=' , phrs.ctxc

        if trce:
            print >> sys.stderr , '  incremental scoring=' , psum ,
            print >> sys.stderr , 'sem[' + phrs.semf.hexadecimal() + ']'
        return psum

#
# unit test
#

if __name__ == '__main__':

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
    try:
        cgs = CognitiveProcedure(stb,inp)
    except ellyException.FormatFailure:
        print >> sys.stderr , "cognitive semantic conversion error"
        sys.exit(1)

    cognitiveDefiner.showCode(cgs.logic)

    s = cgs.score(ctx,phr)
    print 'plausibility=' , s
