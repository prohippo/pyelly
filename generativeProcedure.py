#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# generativeProcedure.py : 15mar2014 CPM
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

BAD = -11111  # bias for phrase with failed generative semantics
  
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

        self.logic = generativeDefiner.convertDefinition(syms,defs)

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

        if phrs.alnk != None:        # if ambiguity here, adjust biases for phrase rules
            if phs.rule.bias == 0:   # if zero bias for selected rule,
                phs.rule.bias = -1   #   mark it to be less favored next time
            else:
                phr = phrs           # selected rule had negative bias
                while True:
                    phr = phr.alnk   # scan all ambiguous phrases
                    if phr == None:
                        break
                    if phr.rule.bias < 0:     # look only at negative rule biases
                        if phr != phs:        # leave selected rule with negative bias,
                            phr.rule.bias = 0 #   but reset all others to zero bias
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
#               print "split",cntx.printStatus()
            elif op == semanticCommand.Gback:  # go back to previous buffer
                cntx.backBuffer()
#               print "back",cntx.printStatus()
            elif op == semanticCommand.Gmrge:  # merge buffers into current one
                cntx.mergeBuffers()
#               print "merge",cntx.printStatus()
            elif op == semanticCommand.Gchng:  # merge with substitution
                ts = code.next()
                ss = code.next()
                cntx.mergeBuffersWithReplacement(ts,ss)
            elif ( op == semanticCommand.Gchck or
                   op == semanticCommand.Gchkf or
                   op == semanticCommand.Gnchk or
                   op == semanticCommand.Gnchf ):
                opn = op - semanticCommand.Gchck
                kind, mode = divmod(opn,2)     # what kind of test?
#               print opn,kind,mode
                sens = (mode == 0)
                if kind == 0:                  # compare output buffer with local variable
                    ids = code.next()
                    ref = code.next()
                    val = cntx.getLocalVariable(ids)
#                   print "chk",ids,"[",ref,"]","[",val,"]"
#                   print (val in ref),sens
                    if (val in ref) == sens:
#                       print "match"
                        code.next()
                        continue
#                   print "no match"
                else:                          # compare phrase semantic feature set
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
                var = code.next()              # set a local variable from string
                if op == semanticCommand.Gset:
                    val = code.next()          #                      from buffer chars
                else:
                    val = cntx.extractCharsFromBuffer(code.next(),op%2)
                cntx.setLocalVariable(var,val)
            elif ( op == semanticCommand.Ginsr or
                   op == semanticCommand.Ginsn ):
                var = code.next()              # insert value local variable into buffer
                s = cntx.getLocalVariable(var)
                if s != '':
                    cntx.insertCharsIntoBuffer(s,op%2)
            elif op == semanticCommand.Gshft:  # shift text between buffers
                cntx.moveCharsBufferToBuffer(code.next())
            elif op == semanticCommand.Gdele:  # delete text from buffers
                cntx.deleteCharsFromBuffer(code.next())
            elif op == semanticCommand.Gdelt:  # delete to subsequence
                cntx.deleteCharsInBufferTo(code.next())
            elif op == semanticCommand.Gstor:  # save deletion to variable
                var = code.next()              # set a local variable from string
                val = ctx.getDeletion()        # last deleted sequence
                cntx.setLocalVariable(var,val) # set variable
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
            elif op == semanticCommand.Gobtn:  # obtain string for current parse position
                tok = cntx.getNthTokenInListing(phrs.posn)
#               print 'obtain: ' , tok.toUnicode()
                cntx.insertCharsIntoBuffer(tok.toUnicode())
            elif op == semanticCommand.Gcapt:  # capitalize first char in buffer
                c = cntx.extractCharsFromBuffer()
                if c != '':
                    cntx.insertCharsIntoBuffer(c.upper(),1)
            elif op == semanticCommand.Gtrce:  # print phrase information to trace execution
                cat = cntx.syms.getSyntaxTypeName(phrs.typx)
                brn = "1" if type(phrs.rule) == grammarRule.ExtendingRule else "2"
            	print >> sys.stderr, "TRACE @" + str(phrs.posn) + " type=" + cat ,
                print >> sys.stderr, "rule=" + str(phrs.rule.seqn) ,
            	print >> sys.stderr, " (" + brn + "-br)" ,
            	cntx.printStatus()
            elif op == semanticCommand.Gproc:  # semantic subprocedure
                proc = cntx.getProcedure(code.next())
                proc.run(cntx,phrs)
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

    for src in args:
        ctx.clearLocalStack()
        ctx.clearBuffers()
        print "------------" , src
        inp = ellyDefinitionReader.EllyDefinitionReader(src)
        if inp == None:
            print >> sys.stderr, "cannot read procedure definition" , src
            continue
        for ln in inp.buffer:
            print ln
        print ''

        gp = GenerativeProcedure(stb,inp)
        print '*CODE*'
        showCode(gp.logic)
        if gp.logic == None:
            print 'null logic'
            continue
        res = gp.doRun(ctx,phr)

        print '----'
        print 'run status=' , res
        print frame.showBuffers()

    print "------------"
    print len(args),'test file(s)'
