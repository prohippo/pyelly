#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# parseTree.py : 03nov2014 CPM
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
encapsulated table-driven syntax analysis of single sentences from basic parse
tree extended for efficient bottomup parsing

designed to work with context-free grammars plus a special nonterminal type
supporting type-0 grammar rules

the three-phase analysis of the context-free part here is taken from Vaughn
Pratt's bottomup algorithm in his LINGOL system
"""

import ellyBits
import parseTreeBottomUp

class ParseTree(parseTreeBottomUp.ParseTreeBottomUp):

    """
    create parser with grammar, syntax type patterns, and macros

    attributes:
        ctx  - interpretive context for cognitive semantics
    """

    def __init__ ( self , stb , gtb , ptb , ctx ):

        """
        initialization

        arguments:
            self -
            stb  - symbol table
            gtb  - grammar table
            ptb  - patterns for syntax categorization
            ctx  - interpretive context
        """

        super(ParseTree,self).__init__(stb,gtb,ptb)
        self.ctx = ctx

    def _score ( self , phr ):

        """
        compute plausibility score for phrase

        arguments:
            self  -
            phr   - phrase to score
        """

        cs = phr.rule.cogs                # get cognitive semantics
#       print >> sys.stderr , 'rule bias=' , phr.rule.bias
        lb = rb = 0
        phb = cs.score(self.ctx,phr)      # set bias to plausibility score
        phr.bias = phb
#       print >> sys.stderr , 'after scoring' , phr
        if phr.lftd != None:
            lb = phr.lftd.bias
            phr.bias += lb                # add in bias of left descendant
        if phr.rhtd != None:
            rb = phr.rhtd.bias
            phr.bias += rb                #         and of right
        phr.bias += phr.rule.bias         # add in delta bias of rule
#       print >> sys.stderr , 'ld=' , phr.lftd , '   rd=' , phr.rhtd
#       print >> sys.stderr , "\n         : cg+ls+rs+ru"
#       fm = "bias= {0:2d} : {1:2d}+{2:2d}+{3:2d}+{4:2d}"
#       print >> sys.stderr , fm.format(phr.bias , phb , lb , rb , phr.rule.bias)

    def initializeBias ( self , phr ):

        """
        set initial bias of a new literal phrase, overriding method in superclass

        arguments:
            self  -
            phr   - phrase to be scored
        """

        if phr.rule.cogs == None:
            print >> sys.stderr , 'bad phr=' , phr , 'rule=' , phr.rule.seqn
        phr.bias = phr.rule.cogs.score(self.ctx,phr)
#       print >> sys.stderr , 'initialize bias' , phr 

    def digest ( self ):

        """
        insert queued phrases to parse tree, possibly also adding to queue

        arguments:
            self
        """

        while True:
            ph = self.dequeue()     # get next phrase from queue
            if ph == None: break    # until empty
            if ph.rule == None:
                print >> sys.stderr , 'no rule for phrase' , ph.seqn
#*          print 'digest' , ph , 'rule=' , ph.rule.seqn , 'wordno=' , self.wordno
            self.getConsequence(ph) # ramify, adding to parse tree and possibly to queue

        self.wordno += 1            # move to next parse position
#*      print 'now at' , self.wordno

    def getConsequence ( self , phr ):

        """
        ramify for given phrase by
         (1) creating new phrases from goals
         (2)                      from extensions
         (3) and setting new goals

        arguments:
            self  -
            phr   - phrase to process
        """

        fbs = phr.synf.compound()
#       print 'fbs=' , fbs , '[' + str(phr.synf.data) + ']'

#*      print 'consequences: phrase=' , phr.seqn , 'usen=' , phr.usen
        if phr.usen <= 0:         # do goal satisfaction?
            self._phase1(phr,fbs)
            if phr.usen != 0:     # do extensions and set goals for current phrase?
                return
            self._phase2(phr,fbs) # do extensions
        self._phase3(phr,fbs)     # set goals

    ################ private methods only after this ################
    
    def _phase1 ( self , phr , fbs ):

        """
        check for goals at current position for current phrase type
        and create new phrase for each match

        arguments:
            self  -
            phr   - current phrase
            fbs   - its compounded feature bits
        """
    
        po = phr.posn
        gls = self.goal[po]
#*      print '> PHASE 1 at' , po , '=' , len(gls) , 'goals'
        for g in gls:
#*          print 'goal of' , g.cat
            if phr.typx == g.cat:
                r = g.rul
                if ellyBits.check(fbs,r.rtfet):
                    phx = g.lph                        # phrase that generated pertinent goal
                    phn = self.makePhrase(phx.posn,r)  # new phrase to satisfy goal
                    if phn == None:
                        break
                    phn.lftd = phx                     # goal phrase is left part of new one
                    phn.rhtd = phr                     # current phrase is right part
                    self._score(phn)                   # compute bias score
                    if phn.synf.test(0):               # inherit features from current phrase?
                        phn.synf.combine(phr.synf)
                    if phn.synf.test(1):               # inherit features from previous phrase?
                        phn.synf.combine(phx.synf)
#                   print 'phr=' , phr , 'phn=' , phn
#                   if phr.typx == phn.typx and phr.synf.match(phn.synf):
#                       phn.usen = 1                   # special right-recursion rule applies
                                                       # set goals only in digesting new phrase
                    self.enqueue(phn)                  # save new phrase for ramification
    
    def _phase2 ( self , phr , fbs ):

        """
        create phrase for each 1-branch syntax rule going to
        the type of the current phrase

        arguments:
            self  -
            phr   - current phrase
            fbs   - its compounded feature bits
        """

        po = phr.posn
        gb = self.gbits[po]
        rls = self.gtb.extens[phr.typx]
#*      print '> PHASE 2 at' , po , '=' , len(rls) , 'rules, gb=' , gb.hexadecimal()
        for r in rls:
            nt = r.styp
#           print 'type=' , nt , 'dm=' , self.gtb.mat.dm[nt].hexadecimal()
            if self.gtb.mat.derivable(nt,gb):          # rule applicable at current position?
                if ellyBits.check(fbs,r.utfet):        # phrase has required features for rule?
                    phn = self.makePhrase(po,r)        # make new phrase if checks succeed
                    if phn == None:
                        break
                    phn.lftd = phr                     # current phrase is part of new one
                    self._score(phn)                   # compute bias score
                    if phn.synf.test(0):               # inherit features from current phrase?
                        phn.synf.combine(phr.synf)
                    self.enqueue(phn)                  # save new phrase for ramification

    def _phase3 ( self , phr , fbs ):

        """
        create a goal at next position for the right branch of each
        2-branch splitting syntax rule having a left branch going to
        the type of the current phrase

        arguments:
            self  -
            phr   - current phrase
            fbs   - its compounded feature bits
        """

        rls = self.gtb.splits[phr.typx]
        po = phr.posn
        if po < 0 : po = 0                       # position check needed for ... phrase type
        gb = self.gbits[po]
        np = self.wordno + 1
#*      print '> PHASE 3 at' , po , '=' , len(rls) , 'rules, gb=' , gb.hexadecimal()
        for r in rls:
            nt = r.styp
#           print 'type=' , nt , 'dm=' , self.gtb.mat.dm[nt].hexadecimal()
            if self.gtb.mat.derivable(nt,gb):    # rule is applicable at current position?
#               print 'left test=' , r.ltfet
                if ellyBits.check(fbs,r.ltfet):  # phrase has required features for rule?
                    g = self.makeGoal(r,phr)     # allocate new goal
#*                  print 'at ' + str(np) + ',' , g
                    if np == len(self.goal):     # check for end of goal array
                        self.addGoalPositions()  # add new positions when needed
                    self.goal[np].append(g)      # add it to next position
                    self.gbits[np].set(g.cat)    # and set bit for type of goal
#                   print 'goal bits=' , self.gbits[np].hexadecimal()

    ###########################################################################
    #### special methods for handling ... syntax type in bottom-up parsing ####
    ###########################################################################

    def startUpX ( self ):

        """
        for handling ... syntax type everywhere in sentence except at end

        arguments:
            self  -
        """

#       print 'startUpX'
        ph = None
        rv = self.gtb.splits[self.gtb.XXX]
        if len(rv) > 0:      # any ... splitting rules defined?
                             # if so, create a empty phrase at current position for it
            ph = self.makePhrase(self.wordno,self.gtb.arbr) 
            if ph == None:   # error check
                return
            ph.synf.set(1)   # must do this to avoid ambiguity problem with ...
            ph.bias = -2     # disfavor
            self.enqueue(ph)
            self.wordno -= 1 # so that goals will be at CURRENT position
            self.digest()    # will increment wordno at end
#       print 'startUpX:' , ph

    def finishUpX ( self ):

        """
        for handling ... syntax type at end of sentence

        arguments:
            self  -
        """

#       print 'finishUp'
        for g in self.goal[self.wordno]:    # look for any ... goal at end of sentence
            if g.cat == self.gtb.XXX:
#               print '...' , g
                break                       # found it
        else:
#           print '... goal not found'
            return                          # done with parsing

        self.newph[self.wordno] = None                  # initialize just in case
        ph = self.makePhrase(self.wordno,self.gtb.arbr) # empty phrase to satisfy ... goals
#       print 'finishUpX:' , ph
        if ph == None: return                           # error check

        ph.usen = -4                        # want only to realize goals for empty phrase
        ph.synf.set(2)                      # must be different from ... for startUpX

        self.enqueue(ph)                    # save phrase for ramifying
        self.wordno -= 1                    # so that any new goals go into right position
        self.digest()                       # one final round of digestion
#       print 'finishUpX @' , self.wordno

#
# unit test
#

import sys

if __name__ == '__main__':

    # test just initialization

    class G(object):
        """ dummy grammar class
        """
        def __init__ (self):
            """ initialization
            """
            self.START = 0
            self.END   = 1
            self.UNKN  = 2
            self.XXX   = 3
            self.splits = [ [ ] , [ ] , [ ] , [ ] ]

    class S(object):
        """ dummy symbol table class
        """
        def __init__ ( self , num=4 ):
            """ initialization
            """
            self.count = num
        def getSyntaxTypeCount ( self ):
            """ dummy method
            """
            return self.count

    tree = ParseTree(S(),G(),None,None)
    print tree
    print dir(tree)
