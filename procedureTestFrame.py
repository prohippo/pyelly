#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# procedureTestFrame.py : 13feb2016 CPM
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
dummy phrase with left and right descendants for support of testing
"""

import ellyBits
import ellyToken
import ellyDefinitionReader
import parseTreeBase
import symbolTable
import grammarRule
import generativeProcedure
import cognitiveProcedure
import interpretiveContext
import conceptualHierarchy

class ProcedureTestFrame(object):

    """
    set up data structures for semantic procedure unit tests

    attributes:
        context  - interpretive context
        phrase   - dummy phrase node
        toknL    - left  token for phrase
        toknR    - right token
    """

    def __init__ ( self ):

        """
        create environment for testing semantic procedure

        arguments:
            self
        """

        stb = symbolTable.SymbolTable()                 # empty
        hry = conceptualHierarchy.ConceptualHierarchy() # empty
        ctx = interpretiveContext.InterpretiveContext(stb,{ },{ },hry)
        self.context = ctx                              # make available

        ptb = parseTreeBase.ParseTreeBase()             # just for generating phrases

        self.toknL = ellyToken.EllyToken('uvwxxyz')     # insert dummy data that might
        self.toknR = ellyToken.EllyToken('abcdefg')     # be replaced from outside

        ctx.addTokenToListing(self.toknL)               # put a token in first position
        ctx.addTokenToListing(self.toknR)               # and a token in second

        x = ctx.syms.getSyntaxTypeIndexNumber('x')      # for consistency, define two
        y = ctx.syms.getSyntaxTypeIndexNumber('y')      # syntactic categories for rules

        fbs = ellyBits.EllyBits(symbolTable.FMAX)       # zero feature bits

        exL = grammarRule.ExtendingRule(x,fbs)  # dummy rules as a place for
        exR = grammarRule.ExtendingRule(x,fbs)  # attaching semantic procedures
        spl = grammarRule.SplittingRule(y,fbs)  # for testing

                                                # dummy semantic procedures
        gX = [ "left" , "right" ]               # generative
        gL = [ "obtain" ]                       #
        gR = [ "obtain" ]                       #

        gP = [ "append did it!" ]               # for standalone generative subprocedure

        cX = [ ]                                # cognitive
        cL = [ ">> +1" ]                        #
        cR = [ ">> -1" ]                        #

        ctx.pushStack()                         # needed for local variables usable in testing
        ctx.setLocalVariable("vl","LLLL")       # make two variables available to work with
        ctx.setLocalVariable("vr","RRRR")       #

        ctx.setProcedure('do',self._genp(gP))   # define procedure 'do'

        exL.gens = self._genp(gL)          # assign semantic procedures to rules
        exL.cogs = self._cogp(cL)          #

        exR.gens = self._genp(gR)          #
        exR.cogs = self._cogp(cR)          #

        spl.gens = self._genp(gX)          #
        spl.cogs = self._cogp(cX)          #

        phr = ptb.makePhrase(0,spl)        # make phrase for splitting plus
        phr.krnl.lftd = ptb.makePhrase(0,exL)   # left and right descendants
        phr.krnl.rhtd = ptb.makePhrase(1,exR)   # defined by left and right
                                           # extending rules from above
        phr.ntok = 1

        stb.getFeatureSet('!one,two',True) # define semantic feature
        print stb.smindx
        smx = stb.smindx['!']              #
        ix = smx['one']                    #
        print 'ix=' , ix
        phr.krnl.semf.set(ix)              # turn on feature for phrase
        ix = smx['two']                    #
        print 'ix=' , ix
        phr.krnl.semf.set(ix)              # turn on feature for phrase
        print 'semf=' , phr.krnl.semf

        self.phrase = phr                  # make phrase available

    def _genp ( self , ls ):

        """
        create a generative procedure

        arguments:
            self  -
            ls    - list of command strings

        returns:
            GenerativeProcedure
        """

        din = ellyDefinitionReader.EllyDefinitionReader(ls)
        return generativeProcedure.GenerativeProcedure(self.context.syms,din)

    def _cogp ( self , ls ):

        """
        create a cognitive procedure

        arguments:
            self  -
            ls    - list of command strings

        returns:
            CognitiveProcedure
        """

        din = ellyDefinitionReader.EllyDefinitionReader(ls)
        return cognitiveProcedure.CognitiveProcedure(self.context.syms,din)

    def showBuffers ( self ):

        """
        show current contents of output buffers in self.context

        arguments:
            self
        """

        K = 44 # line count limit
        bs = self.context.getBufferContents()
        print ' ' , len(bs) , 'buffer' , '' if len(bs) == 1 else 's'
        for b in bs:
            print type(b) , len(b) , 'chars' ,
            k = 0
            for bc in b:
                if k%K == 0: print ''
                k += 1
                print ' ' + bc ,
            print ''
