#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# generativeProcedure.py : 18aug2014 CPM
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
generative semantic procedure with run() method
"""

import sys
import ellyChar
import semanticCommand
import generativeDefiner
import conceptualHierarchy
import grammarRule

class Code(object):

    """
    iteration on list of commands defining a semantic procedure with jumps

    attributes:
        list  - the list
        index - keeping track of where we are
    """

    def __init__ ( self , list ):

        """
        initialize

        arguments:
            self  -
            list  - to iterate on
        """

        self.list = list
        self.index = 0

    def next ( self ):

        """
        get next list element

        arguments:
            self

        returns:
            next element on success, semanticCommand.Gretn  otherwise
        """

        if self.index >= len(self.list):
            return semanticCommand.Gretn 
        else:
            x = self.list[self.index]
            self.index += 1
            return x

    def skip ( self ):

        """
        set index to new list position from contents of current list element

        arguments:
            self  -
        """

        self.index = self.list[self.index]

BAD  = -11111  # bias for phrase with failed generative semantics
LSTJ = ','     # substring for joining substrings in list value
  
class GenerativeProcedure(object):

    """
    define and execute generative semantics

    attributes:
        logic  - compiled procedure
    """
 
    _error = "??????" # default output on error

    def __init__ ( self , syms , defs ):

        """
        initialize from text definition

        arguments:
            self  -
            syms  - symbol table for interpreting procedure definition
            defs  - ellyDefinitionReader
        """

        self.logic = generativeDefiner.compileDefinition(syms,defs)

    def doRun ( self , cntx , phrs ):

        """
        manage execution of generative semantics

        arguments:
            self  -
            cntx  - interpretive context
            phrs  - phrase to which procedure is attached

        returns:
            True on success, False otherwise
        """

        phs = phrs
        while True:
            if self.run(cntx,phs):   # try running generative procedure for phrase
                break                # if success, all done here
            phs.bias = BAD           # mark as implausible
            phs.order()              # get next most plausible phrase
            if phs.bias == BAD:      # if out of alternatives,
                return False         #   fail

#       print >> sys.stderr , 'running' , phs, 'ctxc=' , phs.ctxc

        if phs.ctxc != conceptualHierarchy.NOname: cntx.cncp = phs.ctxc

        if phs.alnk != None:         # on ambiguity, adjust biases for phrase rules
#           print >> sys.stderr , 'adjust rule bias' , phrs
            phi = phs
            rls = [ ]                # for list of unique rules for ambiguities
            while phi != None:
                if not phi.rule in rls: rls.append(phi.rule)
                phi = phi.alnk
            ru = rls[0]              # first rule is the one chosen for phrase analysis
            rls = rls[1:]            # remaining unique rules
            if len(rls) == 0:
                pass                 # if only a single rule involved, no bias adjustment
            elif ru.bias == 0:       # if zero bias for chosen rule,
                ru.bias = -1         #   mark it to be less favored next time
            else:
                for ru in rls: 
                    if ru.bias < 0:  # reset all negative rule biases
                        ru.bias = 0  #   to zero
        return True

    def run ( self , cntx , phrs ):

        """
        execute a generative procedure in context

        arguments:
            self  -
            cntx  - interpretive context
            phrs  - phrase to which procedure is attached

        returns:
            True on success, False otherwise
        """

        if self.logic == None:
            return True         # trivial success
        if phrs == None:
            print >> sys.stderr , 'null phrase:' , self
            return False

#       print 'run semantics for phr' , phrs.seqn , 'rule=' , phrs.rule.seqn

        cntx.pushStack()        # ready for any local variables
        code = Code(self.logic) # get code of procedure to run

#       generativeDefiner.showCode(self.logic)

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
                if phrs.lftd == None:
                    print >> sys.stderr , 'no left descendant for:' , phrs
                    status = False
                else:
#                   print 'to left descendant'
                    status = phrs.lftd.rule.gens.doRun(cntx,phrs.lftd)
            elif op == semanticCommand.Grght:  # go to procedure for right descendant
                if phrs.rhtd == None:
                    print >> sys.stderr , 'no right descendant for:' , phrs
                    status = False
                else:
#                   print 'to right descendant'
                    status = phrs.rhtd.rule.gens.doRun(cntx,phrs.rhtd)
            elif op == semanticCommand.Gblnk:  # insert space into output buffer
                cntx.insertCharsIntoBuffer(u' ')
            elif op == semanticCommand.Glnfd:  # insert linefeed into output buffer
                cntx.insertCharsIntoBuffer(u'\r\n')
            elif op == semanticCommand.Gsplt:  # split off new buffer for output
                cntx.splitBuffer()
#               print "split",
#               cntx.printStatus()
            elif op == semanticCommand.Gback:  # go back to previous buffer
                cntx.backBuffer()
#               print "back",
#               cntx.printStatus()
            elif op == semanticCommand.Gmrge:  # merge buffers into current one
                cntx.mergeBuffers()
#               print "merge",
#               cntx.printStatus()
            elif op == semanticCommand.Gchng:  # merge with substitution
                ts = code.next()
                ss = code.next()
                cntx.mergeBuffersWithReplacement(ts,ss)
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
                if phrs.semf.match(refr) == sens:
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
                val = cntx.peekIntoBuffer(next=sns)
                cntx.setLocalVariable(var,val)
            elif ( op == semanticCommand.Gset  or
                   op == semanticCommand.Gextl or
                   op == semanticCommand.Gextr ):
                var = code.next()              # set a local variable
                if op == semanticCommand.Gset:
                    val = code.next()                                # from string
                elif op == semanticCommand.Gextl:
                    val = cntx.extractCharsFromBuffer(code.next(),1) # from buffer chars
                else:
                    val = cntx.extractCharsFromBuffer(code.next(),0) # from buffer chars
#               print 'val=' , val
                cntx.setLocalVariable(var,val)
            elif ( op == semanticCommand.Ginsr or
                   op == semanticCommand.Ginsn ):
                var = code.next()              # insert value local variable into buffer
                s = cntx.getLocalVariable(var)
                if s != '':
                    if op == semanticCommand.Ginsn:
                        cntx.insertCharsIntoBuffer(s,1)
                    else:
                        cntx.insertCharsIntoBuffer(s,0)
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
                sv = ''.join(val)              # convert to string
                cntx.setLocalVariable(var,sv)  # set variable
            elif op == semanticCommand.Gfnd:   # find sequence in buffer
                cntx.findCharsInBuffer(code.next())
            elif op == semanticCommand.Gpick:  # use local variable to select text
                var = code.next()              #   to insert into buffer
                s = cntx.getLocalVariable(var)
#               print "pick with",s
                dct = code.next()
#               print "in",dct
                if not s in dct:
                    if '' in dct:
                        s = ''
                    else:
                        continue
                cntx.insertCharsIntoBuffer(dct[s])
            elif op == semanticCommand.Gappd:  # append explicit text to buffer
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
                tok = cntx.getNthTokenInListing(phrs.posn)
#               print 'obtain: ' , tok.toUnicode()
                cntx.insertCharsIntoBuffer(tok.toUnicode())
            elif op == semanticCommand.Gcapt:  # capitalize first char in buffer
                c = cntx.extractCharsFromBuffer()
                if c != '':
                    cntx.insertCharsIntoBuffer(c.upper(),1)
            elif op == semanticCommand.Gucpt:  # capitalize first char in buffer
                c = cntx.extractCharsFromBuffer()
                if c != '':
                    cntx.insertCharsIntoBuffer(c.lower(),1)
            elif op == semanticCommand.Gtrce:  # show phrase information to trace execution
                cat = cntx.syms.getSyntaxTypeName(phrs.typx)
                brn = "1" if type(phrs.rule) == grammarRule.ExtendingRule else "2"
                print >> sys.stderr, "TRACE @" + str(phrs.posn) + " type=" + cat ,
                print >> sys.stderr, "rule=" + str(phrs.rule.seqn) ,
                print >> sys.stderr, " (" + brn + "-br)" ,
                cntx.printStatus()
            elif op == semanticCommand.Gshow:   # show local variable
                vr = code.next()
                ms = code.next()
                st = cntx.getLocalVariable(vr)
                print >> sys.stderr, 'SHOW @phr' , phrs.seqn, ': ' + ms
                print >> sys.stderr, "VAR " + vr + '= [' + st + ']'
            elif op == semanticCommand.Gproc:  # semantic subprocedure
                name = code.next()
                if name == '': continue        # null procedure is no operation`
                proc = cntx.getProcedure(name)
                if proc == None:
                    print >> sys.stderr , 'unknown subprocedure name' , name
                    status = False
                else:
                    status = proc.run(cntx,phrs)
            else:
                print >> sys.stderr , GenerativeProcedure._error , 'op=' , op
                status = False

        cntx.popStack()  # undefine local variables for procedure
        return status

"""
unit testing from file input
""" 
    
if __name__ == "__main__":

    import ellyDefinitionReader
    import procedureTestFrame
    from generativeDefiner import showCode
        
    frame = procedureTestFrame.ProcedureTestFrame()
    phr = frame.phrase
    ctx = frame.context
    stb = ctx.syms

    args = sys.argv[1:] if len(sys.argv) > 1 else [ 'testProcedure.0.txt' ]

    for src in args:                       # test all specified input files
        ctx.clearLocalStack()              # reset context
        ctx.clearBuffers()
        print "------------" , src
        inp = ellyDefinitionReader.EllyDefinitionReader(src)
        if inp == None:                    # check if input readable
            print >> sys.stderr, "cannot read procedure definition" , src
            continue
        for ln in inp.buffer:              # echo input file
            print ln
        print ''

        gp = GenerativeProcedure(stb,inp)  # compile procedure
        print '*CODE*'
        if gp.logic != None:
            showCode(gp.logic)             # dump procedure logic
        else:
            print 'null logic'
            continue
        res = gp.doRun(ctx,phr)            # run the procedure

        print '----'
        print 'run status=' , res          # show status
        print '----'
        frame.showBuffers()                # show output buffers

    print "------------"
    print len(args),'test file(s)'
