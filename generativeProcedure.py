#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# generativeProcedure.py : 02apr2018 CPM
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
generative semantic procedure object with run() method
"""

import sys
import copy
import semanticCommand
import generativeDefiner
import conceptualHierarchy
import grammarRule
import ellyChar
import ellyBits

#
## for debugging only
#

def _showa ( ph ):
    """
    dump ambiguity listing for phrase
    arguments:
        ph  - phrase node object
    """
    print ''
    while ph != None:        # look at alternatives in failure
        krn = ph.krnl
        print '*  phr=' , krn.seqn , 'rule=' , krn.rule.seqn ,
        print 'type=' , krn.typx , 'bias=' , krn.bias
        ph = ph.alnk

def _showb ( ls ):
    """
    dump multi-buffer contents
    arguments:
        ls  - buffer char lists
    """
    if ls == None:
        return
    n = 0
    for s in ls:
        print str(n) + ':<' ,
        print u''.join(s) + '>'
        n += 1

#
## generative semantic machine implementation
#

class Code(object):

    """
    iteration on list of commands with jumps for a semantic procedure

    attributes:
        lstg  - the list
        indx  - keeping track of where we are
        idno  - ID for code object
    """

    def __init__ ( self , lstg , idno=-1 ):

        """
        initialize

        arguments:
            self  -
            lstg  - to iterate on
            idno  - identifier for code
        """

        self.lstg = lstg
        self.indx = 0
        self.idno = idno

    def __str__ ( self ):

        """
        show ID for code

        arguments:
            self  -

        returns:
            ID string
        """

        return 'CODE: ' + str(self.idno) + ' (cnt= ' + str(len(self.lstg)) + ')'

    def next ( self ):

        """
        get next list element

        arguments:
            self

        returns:
            next element on success, semanticCommand.Gretn otherwise
        """

        if self.indx >= len(self.lstg):
            return semanticCommand.Gretn
        else:
            x = self.lstg[self.indx]
            self.indx += 1
            return x

    def skip ( self ):

        """
        set index to new list position from contents of current list element

        arguments:
            self  -
        """

        self.indx = self.lstg[self.indx]

BAD  = -99     # bias for phrase with failed generative semantics
LSTJ = ','     # substring for joining substrings in list value
PNAM = '_pnam' # variable for last procedure call in local stack

space = { u'\n':u'\\n' , u'\r':u'\\r' , u' ':ellyChar.NBS , u'\t':u'\\t' }

def despace ( strs ):

    """
    get Unicode string with ASCII space chars normalized for dumping

    arguments:
        strs  - string to convert

    returns:
        normalized string
    """

    lstg = [ ]
    for c in strs:
        if c in space:
            lstg.append(space[c])
        else:
            lstg.append(c)
    return u''.join(lstg)

class GenerativeProcedure(object):

    """
    define and execute generative semantics

    attributes:
        logic  - compiled procedure
    """

    def __init__ ( self , syms , defs ):

        """
        initialize from text definition

        arguments:
            self  -
            syms  - symbol table for interpreting procedure definition
            defs  - ellyDefinitionReader
        """

        self.logic = generativeDefiner.compileDefinition(syms,defs)

    def __unicode__ ( self ):

        """
        show procedure logic

        arguments:
            self
        """

        generativeDefiner.showCode(self.logic)

    def doRun ( self , cntx , phrs ):

        """
        manage execution of generative semantics
        including recovery from FAIL command

        arguments:
            self  -
            cntx  - interpretive context
            phrs  - phrase to which procedure is attached

        returns:
            True on success, False otherwise
        """

#       print 'doRun for phrs=' , phrs.krnl.seqn
        phs = phrs
        scbn = cntx.buffn                       # save buffer index for any failure
        if phrs.alnk == None:
            scbs = None
        else:                                   # copy current and split-off buffers
            scbs = copy.deepcopy(cntx.buffs[scbn:])
#       _showb(scbs)
        code = Code(self.logic,phs.krnl.seqn)
#       print 'original =' , code
        while True:                             # for phrase
            if self.run(code,cntx,phs):         # try to run generative procedure
#               print 'after run'               #
#               _showb(cntx.getBufferContents())
#               cntx.printStatus()              # dump buffers for debugging
                break                           # if success, all done here
#           _showa(phs)              # dump ambiguities
            phs.krnl.bias = BAD      # mark as implausible
            phs.order()              # get next most plausible phrase
#           _showa(phs)              # dump ambiguities again
#           print 'at buffer=' , scbn
#           _showb(cntx.getBufferContents())
            rest = copy.deepcopy(scbs)
            cntx.buffn = scbn                   # restore previous buffers before retry
            if scbs == None:
                pass
            elif scbn == 0:                     #
#               print '++++replace'
                cntx.buffs = rest
            else:
#               print '++++extend'
                cntx.buffs = cntx.buffs[:scbn] + rest
#           _showb(cntx.getBufferContents())
            if phs.krnl.bias == BAD:            # if out of alternatives,
                return False                    #   fail completely
            code = Code(phs.krnl.rule.gens.logic,phs.krnl.seqn)
#           print 'alternate=' , code

#       print 'running' , phs, 'ctxc=' , phs.krnl.ctxc

        if phs.krnl.ctxc != conceptualHierarchy.NOname: cntx.cncp = phs.krnl.ctxc

        if phs.alnk != None:         # on ambiguity, adjust biases for phrase rules
#           print 'adjust rule bias for:' , phs
            mnb = phs.krnl.bias - 1  # plausibility lower limit
            phi = phs
            rls = [ ]                # for list of unique rules for ambiguities
            while phi != None:
                if phi.krnl.bias >= mnb and not phi.krnl.rule in rls:
                    rls.append(phi.krnl.rule)
                phi = phi.alnk
            ru  = rls[0]             # first rule is the one chosen for phrase analysis
            rls = rls[1:]            # remaining unique rules
#           print 'rls=' , rls
#           print 'ru=' , unicode(ru)
            if len(rls) > 0:
                if ru.bias == 0:     # if zero bias for chosen rule,
                    ru.bias = -1     #   mark it to be less favored next time
#                   print '0 bias to -1'
                else:
                    for ru in rls:
                        ru.bias = 0  # make all rule biases zero
#                   print 'restore all biases to 0'

        return True

    def run ( self , code , cntx , phrs , pnam=None ):

        """
        execute a generative procedure in context

        arguments:
            self  -
            code  - actual generative semantics to run
            cntx  - interpretive context
            phrs  - phrase to which procedure is attached
            pnam  - procedure name to associate with call

        returns:
            True on success, False otherwise
        """

        if code == None:
            return True         # trivial success
        if phrs == None:
            print >> sys.stderr , 'null phrase:' , self
            return False
#       print 'run code =' , code
#       if len(code.lstg) > 4:
#           generativeDefiner.showCode(code.lstg)

#       print 'run semantics for phr' , phrs.krnl.seqn , 'rule=' , phrs.krnl.rule.seqn

        cntx.pushStack()        # ready for any local variables
#       print 'pnam=' , pnam
        if pnam != None:        # save any procedure name for TRACE
            cntx.defineLocalVariable(PNAM,pnam)

        status = True           # success flag to be return

        while status:

            op = code.next()    # iterate on operations in code
#           print 'op=' , op , 'code @' + str(code.index)

            if op < 0: break    # op codes are non-negative numeric

            if   op == semanticCommand.Gnoop:  # no op
                pass
            elif op == semanticCommand.Gretn:  # successful return
#               print 'return'
                break
            elif op == semanticCommand.Gfail:  # unsuccessful return
                print >> sys.stderr , 'generative semantic FAIL'
                status = False
            elif op == semanticCommand.Gleft:  # go to procedure for left descendant
                if phrs.krnl.lftd == None:
                    print >> sys.stderr , 'no left descendant for:' , phrs
                    status = False
                else:
#                   print 'to left descendant'
                    status = phrs.krnl.lftd.krnl.rule.gens.doRun(cntx,phrs.krnl.lftd)
            elif op == semanticCommand.Grght:  # go to procedure for right descendant, or left
#               print 'descent from' , phrs
                if phrs.krnl.rhtd == None:
                    if phrs.krnl.lftd == None:
                        print >> sys.stderr , 'no descendants for:' , phrs
                        status = False
#                   print 'to left descendant instead'
                    status = phrs.krnl.lftd.krnl.rule.gens.doRun(cntx,phrs.krnl.lftd)
                else:
#                   print 'to right descendant'
                    status = phrs.krnl.rhtd.krnl.rule.gens.doRun(cntx,phrs.krnl.rhtd)
            elif op == semanticCommand.Gblnk:  # insert space into output buffer
                cntx.insertCharsIntoBuffer(u' ')
            elif op == semanticCommand.Glnfd:  # insert linefeed into output buffer
                cntx.insertCharsIntoBuffer(u'\n ')
            elif op == semanticCommand.Gsplt:  # split off new buffer for output
                cntx.splitBuffer()
#               print "split",
#               cntx.printStatus()
            elif op == semanticCommand.Gback:  # go back to previous buffer
                cntx.backBuffer()
#               print "back",
#               cntx.printStatus()
            elif op == semanticCommand.Gmrge:  # merge buffers into current one
                cntx.mergeBuffer()
#               print "merge",
#               cntx.printStatus()
            elif op == semanticCommand.Gchng:  # merge with substitution
                ts = code.next()
                ss = code.next()
                cntx.mergeBufferWithReplacement(ts,ss)
            elif ( op == semanticCommand.Gchck or
                   op == semanticCommand.Gnchk ):
                sens = (op == semanticCommand.Gchck)
                ids = code.next()
                ref = code.next()
                val = cntx.getLocalVariable(ids)
#               print "chk",ids,"[",ref,"]","[",val,"]"
#               print (val in ref),sens
                if (val in ref) == sens:
#                   print "match"
                    code.next()
                    continue
#               print "no match"
                code.skip()                    # match fails
            elif op == semanticCommand.Gchkf:
                refr = code.next()
                dblb = phrs.krnl.semf.compound()
                if ellyBits.check(dblb,refr):
                    code.next()
                    continue
                code.skip()                    # match fails
            elif op == semanticCommand.Gskip:  # unconditional branch
                code.skip()
            elif op == semanticCommand.Gvar:   # define new local variable
                var = code.next()
                val = code.next()
#               print "var",var,"[",val,"]"
                cntx.defineLocalVariable(var,val)
            elif op == semanticCommand.Gpeek:
                var = code.next()
                sns = code.next()
                val = cntx.peekIntoBuffer(nxtb=sns)
                cntx.setLocalVariable(var,val)
            elif ( op == semanticCommand.Gset  or
                   op == semanticCommand.Gextl or
                   op == semanticCommand.Gextr ):
                var = code.next()              # set a local variable
                if op == semanticCommand.Gset:
                    val = code.next()                                  # from string
                elif op == semanticCommand.Gextl:                      # source is current buffer
                    val = cntx.extractCharsFromBuffer(code.next(),m=0) #   get buffer chars
                else:                                                  # source is next    buffer
                    val = cntx.extractCharsFromBuffer(code.next(),m=1) #   get buffer chars
#               print 'val=' , val
                cntx.setLocalVariable(var,val)
            elif ( op == semanticCommand.Ginsr or
                   op == semanticCommand.Ginsn ):
                var = code.next()              # insert value local variable into buffer
                s = cntx.getLocalVariable(var)
                if s != '':
                    if op == semanticCommand.Ginsn:
                        cntx.insertCharsIntoBuffer(s,m=1)
                    else:
                        cntx.insertCharsIntoBuffer(s,m=0)
            elif op == semanticCommand.Gshft:  # shift text between buffers
                cntx.moveCharsBufferToBuffer(code.next())
            elif op == semanticCommand.Gdele:  # delete text from buffers
                cntx.deleteCharsFromBuffer(code.next())
            elif op == semanticCommand.Gdelt:  # delete to subsequence
                s = code.next()
                t = code.next()
                if t > 0:
                    cntx.deleteCharsInBufferTo(s)
                else:
                    cntx.deleteCharsInBufferFrom(s)
            elif op == semanticCommand.Gstor:  # save deletion to variable
                var = code.next()              # set a local variable from string
                nde = code.next()              # deletion count
#               print 'var=',var,'nde=',nde
                val = cntx.getDeletion()       # last deleted sequence
#               print 'val=',val
                if abs(nde) >= len(val):
                    val = [ ]                  # set to empty sequence
                elif nde > 0:
                    val = val[:-nde]           # drop final chars
                elif nde < 0:
                    val = val[-nde:]           # drop initial chars
                cntx.setLocalVariable(var,val) # set variable to deleted string
            elif op == semanticCommand.Gfnd:   # find sequence in buffer
                cntx.findCharsInBuffer(code.next(),code.next())
            elif op == semanticCommand.Galgn:  # align buffer to start of line
                sens = code.next()             # direction of alignment
                cntx.findCharsInBuffer('\n',sens)
                if sens:
                    if cntx.peekIntoBuffer(False) == '\n':
                        cntx.moveCharsBufferToBuffer(1)  # move over expected space after \n
                else:
                    if cntx.peekIntoBuffer(True) == '\n':
                        cntx.moveCharsBufferToBuffer(2)  # move \n + space to current buffer
            elif op == semanticCommand.Gpick:  # use local variable to select text
                var = code.next()              #   to insert into buffer
                s = cntx.getLocalVariable(var)
#               print 'pick with',s
                dct = code.next()
#               print 'in',dct
                if not s in dct:
                    if '' in dct:
                        s = ''
                    else:
                        continue
                cntx.insertCharsIntoBuffer(dct[s])
            elif op == semanticCommand.Gappd:  # append explicit text to current buffer
                s = code.next()
                cntx.insertCharsIntoBuffer(s)
            elif op == semanticCommand.Gget:   # assign global value to local variable
                var = code.next()
                gvn = code.next()
                cntx.setLocalVariable(var,cntx.getGlobalVariable(gvn))
            elif op == semanticCommand.Gput:   # assign value of local variable to global
                var = code.next()
                gvn = code.next()
                cntx.setGlobalVariable(gvn,cntx.getLocalVariable(var))
            elif op == semanticCommand.Gassg:  # assign one local variable to another
                dst = code.next()              # note order difference here!
                src = code.next()
                cntx.setLocalVariable(dst,cntx.getLocalVariable(src))
            elif op == semanticCommand.Gque:   # queue up or count down iteration
                dst = code.next()              # note order difference here!
                src = code.next()
                cno = code.next()              # > 0 for QUEUE, < 0 for UNQUEUE
                val = cntx.getLocalVariable(src)
                if len(val) == 0:              # src is empty string?
                    if cno == 0: continue      # if so, do nothing for QUEUE
                    it = ''                    # otherwise set dst to ''
                elif cno <= 0:
#                   print 'dst=',dst
                    it = cntx.getLocalVariable(dst) + val # QUEUE concatenates
                else:
                    if cno > len(val):         # UNQUEUE pops up to n chars for dst
                        cno = len(val)
                    it = val[:cno]
                    cntx.setLocalVariable(src,val[cno:])
                cntx.setLocalVariable(dst,it)  # new value for dst
#               print 'op=',op,'dst=',it
            elif op in [semanticCommand.Gunio,semanticCommand.Gintr,semanticCommand.Gcomp]:
                dst = code.next()                  # note order difference here!
                src = code.next()
#               print 'dst=',dst,'src=',src
                dv = cntx.getLocalVariable(dst)
                sv = cntx.getLocalVariable(src)
#               print 'op=',op,'dv=',dv,'sv=',sv
                lstd = [ ] if len(dv) == 0 else dv.split(LSTJ)
                lsts = [ ] if len(sv) == 0 else sv.split(LSTJ)
                ls   = [ ]
                if op == semanticCommand.Gunio:    # union of two list values
                    for x in lsts:
                        if not x in lstd:
                            lstd.append(x)
                    ls = lstd
                elif op == semanticCommand.Gintr:  # intersection of two list values
                    for x in lsts:
                        if x in lstd:
                            ls.append(x)
                else:                              # complement of list value
                    for x in lstd:
                        if not x in lsts:
                            ls.append(x)

                js = LSTJ.join(ls)
#               print 'ls=',ls,'js=',js
                cntx.setLocalVariable(dst,js)

            elif op == semanticCommand.Gobtn:  # obtain string for current parse position
                tok = cntx.getNthTokenInListing(phrs.krnl.posn)
#               print 'obtain: ' , tok.toUnicode()
                cntx.insertCharsIntoBuffer(tok.toUnicode())
            elif op == semanticCommand.Gcapt:  #   capitalize first char in next buffer
                c = cntx.extractCharsFromBuffer(m=1)
                if c != '':
                    cntx.insertCharsIntoBuffer(c.upper(),m=1)
            elif op == semanticCommand.Gucpt:  # uncapitalize first char in next buffer
                c = cntx.extractCharsFromBuffer(m=1)
                if c != '':
                    cntx.insertCharsIntoBuffer(c.lower(),m=1)
            elif op == semanticCommand.Gtrce:  # show phrase info to trace execution
                cat = cntx.syms.getSyntaxTypeName(phrs.krnl.typx)
                brn = 1 if isinstance(phrs.krnl.rule,grammarRule.ExtendingRule) else 2
                pnam = cntx.getLocalVariable(PNAM)
                fm = u'TRACE @{0:d} type={1:s} rule={2:d} ({3:d}-br)'
                fs = fm.format(phrs.krnl.posn,cat,phrs.krnl.rule.seqn,brn)
                sys.stderr.write(fs)
                sys.stderr.flush()
                cntx.printStatus(pnam)
            elif op == semanticCommand.Gshow:   # show local variable
                vr = code.next()
                ms = code.next()
                st = despace(cntx.getLocalVariable(vr))
                fm = u'SHOW @phr {0:d} : [{1:s}] VAR {2:s}= [{3:s}]'
                fs = fm.format(phrs.krnl.seqn,ms,vr,st)
                sys.stderr.write(fs)
                sys.stderr.write('\n')
                sys.stderr.flush()
            elif op == semanticCommand.Gview:   # show current and new buffers partially
                nc = code.next()
                cbl , nbl = cntx.viewBufferDivide(nc)
                cbn = cntx.getCurrentBuffer()
                fm = u'VIEW ={0:2d} @phr {1:d} : {2:s} | {3:s}\n'
                st = fm.format(cbn,phrs.krnl.seqn,str(cbl),str(nbl))
                sys.stderr.write(st)
                sys.stderr.flush()
            elif op == semanticCommand.Gproc:  # semantic subprocedure
                name = code.next()
#               print >> sys.stderr , 'run procedure (' + name + ')' , 'in' , phrs
                if name == '': continue        # null procedure is no operation`
                proc = cntx.getProcedure(name) # generative semantics object
                if proc == None:
                    print >> sys.stderr , 'unknown subprocedure name' , name
                    status = False
                else:
                    status = proc.run(Code(proc.logic),cntx,phrs,name)
            else:
                print >> sys.stderr , '** unknown generative semantic op=' , op , 'in' , phrs
                status = False

        cntx.popStack()  # undefine local variables for procedure
        return status

#
# unit testing from file input
#

if __name__ == "__main__":

    import ellyDefinitionReader
    import procedureTestFrame
    from generativeDefiner import showCode

    frame = procedureTestFrame.ProcedureTestFrame()
    phr = frame.phrase
    ctx = frame.context
    stb = ctx.syms

    args = sys.argv[1:] if len(sys.argv) > 1 else [ 'testProcedure.0.txt' ]

    for srcn in args:                      # test all specified input files
        ctx.clearLocalStack()              # reset context
        ctx.clearBuffers()
        print "------------" , srcn
        inp = ellyDefinitionReader.EllyDefinitionReader(srcn)
        if inp.error != None:              # check if input readable
            print >> sys.stderr, "cannot read procedure definition" , srcn
            print >> sys.stderr, inp.error
            continue
        for ln in inp.buffer:              # echo input file
            print ln
        print ''

        gp = GenerativeProcedure(stb,inp)  # compile procedure

        print '*CODE*'
        if gp.logic != None:
            showCode(gp.logic)             # dump procedure logic
        else:
            print 'no logic'
            continue
        res = gp.doRun(ctx,phr)            # run the procedure

        print '----'
        print 'run status=' , res          # show status
        print '----'
        frame.showBuffers()                # show output buffers

    print "------------"
    print len(args),'test file(s)'
