#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# parseTreeBottomUp.py : 01mar2016 CPM
# -----------------------------------------------------------------------------
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
specialization of parse tree for augmented bottom-up context-free parsing
"""

import ellyBits
import ellyDefinitionReader
import ellyConfiguration
import grammarRule
import symbolTable
import cognitiveProcedure
import generativeProcedure
import parseTreeBase

NPOSNS = 128          # nominal minimum number of tree leaf nodes

_error = list('????') # what to show when input cannot be parsed

class ParseTreeBottomUp(parseTreeBase.ParseTreeBase):

    """
    parse tree plus supporting structures for table-driven
    bottom-up  parsing algorithm

    attributes:
        newph  - unique new phrases at each position
        ambig  - accumulate ambiguous phrases for reporting
        queue  - of phrases yet to process

        gtb    - basic syntax and internal dictionary
        ptb    - syntax type patterns
        goal   - goals set at each position
        gbits  - flags for syntax types of goals at each position
        wordno - index of next word in sentence to process
        nul    - splitting rules for ... syntax type?
        litg   - generative semantic procedure for literal rule
        litc   - cognitive
        ntyp   - count of syntax types

        ctx    - interpretive context

        _zbs   - all-zero syntactic features
        _pls   - saved plausibility score from last evaluation
    """

    def __init__ ( self , stb , gtb , ptb ):

        """
        create parse tree generator with grammar and syntax type patterns

        arguments:
            self  -
            stb   - symbol table
            gtb   - grammar
            ptb   - patterns
        """

#       print "at ParseTreeBottomUp"
        inp = ellyDefinitionReader.EllyDefinitionReader([ 'obtain' ])
        self.litg = generativeProcedure.GenerativeProcedure(stb,inp)
        inp = ellyDefinitionReader.EllyDefinitionReader([ ])
        self.litc = cognitiveProcedure.CognitiveProcedure(stb,inp)
        self.ntyp = stb.getSyntaxTypeCount()
        self.gtb = gtb
        self.ptb = ptb
        self.ctx = None   # set by ParseTree, if at all
        super(ParseTreeBottomUp,self).__init__()
#       print "back in ParseTreeBottomUp"
        self.nul  = ( len(gtb.splits[gtb.XXX]) > 0 )
        self._zbs = ellyBits.EllyBits(symbolTable.FMAX)
        self._pls = 0

    def addGoalPositions ( self , n=10 ):

        """
        extend goal lists and goal bits

        arguments:
            self  -
            n     - how many new positions to add
        """

#       print 'add goals, ntyp=' , self.ntyp
        for _ in range(n):
            self.goal.append([ ])
            self.gbits.append(ellyBits.EllyBits(self.ntyp))

    def reset ( self ):

        """
        empty out parse tree for new input
        overrides reset() for ParseTreeBase

        arguments:
            self
        """

#       print "ParseTreeBottomUp.reset()"
        super(ParseTreeBottomUp,self).reset()
        self.newph = [ ]                   # clear out lists for bottomup parsing
        self.queue = [ ]
        self.goal  = [ ]
        self.gbits = [ ]

        self.addGoalPositions(NPOSNS)      # reallocate goals and goal bits
        self.gbits[0].set(self.gtb.START)  # starting goal of SENT at start of input

        self.wordno = 0                    # restart word count for parse
        self.restartQueue()                #

    def _showQ ( self ):

        """
        show parse tree queue for debugging

        arguments:
            self
        """

        q = map(lambda x: str(x.krnl.seqn) , self.queue)
#       print 'queue:' , '<' + ' '.join(q) + '>'

    def restartQueue ( self ):

        """
        prepare for processing next input token

        arguments:
            self
        """

#       self._showQ()
        self.ambig = [ ]             # clear current list of ambiguities
        self.newph.append(None)      # add empty new phrase list at next position
        for i in range(self.wordno): # empty out all new phrase lists in prior positions
            self.newph[i] = None

    def enqueue ( self , phr ):

        """
        check if phrase is ambiguity and enqueue it if not

        arguments:
            self  -
            phr   - phrase to insert
        """

#       print 'enqueue:' , phr , len(self.newph) , 'token positions'
#       self._showQ()
        po = phr.krnl.posn
        pho = self.newph[po]
#       print 'po=' , po , 'pho=' , pho
        while pho != None:

#           print phr.krnl.typx , ':' , pho.krnl.typx
#           print phr.krnl.synf.hexadecimal() , ':' , pho.krnl.synf.hexadecimal()
            if (        phr.krnl.typx == pho.krnl.typx
                and     phr.krnl.synf.equal(pho.krnl.synf)
                and not phr.krnl.synf.test(symbolTable.LAST) # *UNIQUE check
               ):                          # ambiguity?
#               print 'ambiguity:' , phr.krnl.typx , phr.krnl.synf.hexadecimal() , 'for' , phr.krnl.seqn , pho.krnl.seqn
                if pho.alnk == None:       # if so, is ambiguity new?
                    self.ambig.append(pho) # if so, start new ambiguity listing
#*                  print 'new ambiguity'
                phs = pho.alnk             # add new phrase after head of ambiguity list
                pho.alnk = phr             #
                phr.alnk = phs             #
                if phr.krnl.bias > pho.krnl.bias: # make sure most plausible is at front of list
#                   print 'refronting'
                    phr.swap(pho)
                    self.reorder()         # update tree for latest plausibility scores
                return                     # and process no further

            pho = pho.llnk                 # if no match, go to next group of phrases

        phr.llnk = self.newph[po]          # if out of groups, add to linked list at position
        self.newph[po] = phr               #
        self.queue.append(phr)             # enqueue phrase for further processing

    def dequeue ( self ):

        """
        get next phrase from queue

        arguments:
            self

        returns:
            next phrase
        """

#       self._showQ()
        if len(self.queue) == 0:
            return None
        else:
#*          print 'dequeue' , self.queue[0] , 'from' , len(self.queue)
            return self.queue.pop(0)

    def requeue ( self ):

        """
        filter queue to keep phrases with maximum token length
        (this should only run immediately after queueing phrases
        created by lookup of a single token)

        arguments:
            self

        returns:
            count of phrases dropped
        """

#       print 'requeue'
#       self._showQ()
        mx = 0
        for ph in self.queue:
            if mx < ph.lens: mx = ph.lens
        n = 0
        q = [ ]
        for ph in self.queue:
            if ph.lens == mx or ph.lens == 0:
                q.append(ph)
            else:
                n += 1
        self.queue = q
#       print 'requeue'
        return n

    def reorder ( self ):

        """
        update ambiguity lists after swapping of phrase nodes]

        arguments:
            self
        """

        while self.swapped:
            self.swapped = False
            for rep in self.ambig:
                rep.order()

    #################################
    # make leaf nodes in parse tree #
    #################################

    def createPhrasesFromDictionary ( self , word , split , capzn ):

        """
        create phrases from word by internal dictionary lookup

        arguments:
            self  -
            word  - input segment string to look up
            split - was segment already analyzed?
            capzn - first char was capitalized

        returns:
            True if phrases created, False otherwise

        exceptions:
            ParseOverflow
        """

#       print 'internal dictionary: word=',word
        if word == None:
            return False
        ws = u''.join(word) if word is list else word
        if ws not in self.gtb.dctn: return False
#       print 'found' , '[' + ws + ']'
        rules = self.gtb.dctn[ws]     # look up string in internal dictionary
        if rules == None:
            print >> sys.stderr , 'no rules for' , '[' + ws + ']'
            return False
        lw = len(ws)
#       print len(rules) , 'rule(s)' , 'split=' , split
        for r in rules:               # create new phrase for each rule found
            if self._addTerminal(r,split,capzn):
                self.lastph.lens = lw
        return True

    def addLiteralPhrase ( self , cat , fbs , spl=False , cap=False ):

        """
        make a phrase for a literal obtained by various means and enqueue

        arguments:
            self  -
            cat   - syntactic category
            fbs   - feature bits
            spl   - splitting flag
            cap   - capitalization flag

        returns:
            True on success, False otherwise

        exceptions:
            ParseOverflow
        """

#       print 'literal phrase'
        r = self._makeLiteralRule(cat,fbs)
        return self._addTerminal(r,spl,cap)

    def addLiteralPhraseWithSemantics ( self , cat , fbs , sbs , bias , gen=None , spl=False ):

        """
        make a phrase for a literal obtained by various means and enqueue

        arguments:
            self  -
            cat   - syntactic category
            fbs   - syntactic feature bits
            sbs   - semantic  feature bits
            bias  - cognitive bias
            gen   - generative procedure
            spl   - splitting flag

        returns:
            True on success, False otherwise

        exceptions:
            ParseOverflow
        """

#       print 'literal phrase with semantics: cat=' , cat , 'fbs=' , fbs , 'sbs=' , sbs
#       print 'spl=' , spl
#       print 'gen=' , gen
        r = self._makeLiteralRule(cat,fbs,gen)
        if self._addTerminal(r,spl):
            self.lastph.krnl.semf = sbs
            self.lastph.krnl.bias = bias
#           print 'lastph=' , self.lastph
            return True
        else:
            return False

    def createUnknownPhrase ( self , tokn ):

        """
        create a phrase of syntax type UNKN for a token

        arguments:
            self  -
            tokn  -

        returns:
            True on success, False otherwise

        exceptions:
            ParseOverflow
        """

#       print 'unknown phrase'
        r = self._makeLiteralRule(self.gtb.UNKN,self._zbs)
        return self._addTerminal(r,tokn.isSplit(),tokn.isCapitalized())

    ##################################
    # dummy methods to be overridden #
    ##################################

    def dumpTree ( self , phr ):

        """
        show subtree rooted at phrase

        arguments:
            self  -
            phr   - phrase
        """

        pass  # should be overridden in derived class

    def dumpAll ( self ):

        """
        show subtrees for all phrases

        arguments:
            self  -
        """

        pass  # should be overridden in derived class

    def setDepth ( self , dpth ):

        """
        change tree display depth limit

        arguments:
            self  -
            dpth  - new depth
        """

        pass  # should be overridden in derived class

    def initializeBias ( self , phr ):

        """
        set initial bias of a new phrase

        arguments:
            self  -
            phr   - phrase to be scored
        """

        pass  # should be overridden in derived class

    #########################################
    # produce output for results of parsing #
    #########################################

    def evaluate ( self , ctx ):

        """
        run generative semantic procedures for a derived parse tree

        arguments:
            self  -
            ctx   - interpretive context, including output buffer

        returns:
            return True on success, False otherwise
        """

        nt = len(ctx.tokns)
#*      print 'evaluate:' , nt , 'tokens' , 'wordno=' , self.wordno
        gs = self.goal[nt]
#*      print 'at' , nt , 'with' , len(gs) , 'goals'
        topg = None
        tops = -11111
        for g in gs:
            if g.cat == self.gtb.END:        # look for goal expecting END type
                                             # with START generating phrase at start of input
                phr = g.lph
                if phr.krnl.posn == 0 and phr.krnl.typx == self.gtb.START:
                    if tops < phr.krnl.bias: # find the most plausible sentence
                        tops = phr.krnl.bias #
                        topg = g

        if topg != None:                      # any START?
            g = topg                          # if so, get sentence translation to return
            phr = g.lph
            self._pls = phr.krnl.bias         # save plausibility
#*          print 'from' , g
#*          print 'sent=' , phr
            if phr.krnl.rule.gens.doRun(ctx,phr): # run generative semantics
                if ellyConfiguration.longDisplay:
                    self.dumpAll()                # show complete parse tree
                else:
                    self.dumpTree(phr)            # show parse tree only for SENT phrase
                return True

        print >> sys.stderr , ''
        if topg == None:
            print >> sys.stderr , 'parse FAILed!'
        else:
            print >> sys.stderr , 'rewriting FAILed!'

        self.dumpAll()                        # parse failed; show complete dump, if enabled

        if ellyConfiguration.inputEcho:
            ctx.echoTokensToOutput()          # write out original input as translation
        else:
            ctx.insertCharsIntoBuffer(_error) # write out simple error message as translation
        return False

    def getLastPlausibility ( self ):

        """
        get saved plausibility score for last evaluation

        arguments:
            self  -

        returns:
            saved integer score
        """

        return self._pls

    #################################################################
    ################ private methods only after this ################

    def _addTerminal ( self , r , dvdd , capn=False ):

        """
        create a leaf phrase node from a definition for a term
        not put into any dictionary

        arguments:
            self  -
            r     -  basic rule
            dvdd  -  whether segment has been analyzed

        returns:
            True if successful, False otherwise

        exceptions:
            ParseOverflow
        """

#       print '_addTerminal: r=' , unicode(r) , 'dvdd=' , dvdd
        typ = r.styp
        gbs = self.gbits[self.wordno]
#       print 'goal bits=' , gbs.hexadecimal() , 'at' , self.wordno

        if (typ == self.gtb.UNKN or
            self.gtb.mat.derivable(typ,gbs)):               # acceptable syntax type?
            ph = self.makePhrase(self.wordno,r)             # make phrase with rule
            if ph != None:
                ph.ntok = 1                                 # set token count
#               print '_addTerminal ph=' , ph
#               print 'dvdd =' , dvdd
                self.initializeBias(ph)                     # for ranking of ambiguities
                if dvdd and len(self.gtb.splits[typ]) > 0:  # segment analyzed?
#                   print 'limit ramification'
                    ph.krnl.usen = 1
                if capn:                                    # note capitalization?
                    ph.krnl.semf.set(0)
#               print 'ph.lens=' , ph.lens
#               print 'ph=' , ph
                self.enqueue(ph)                            # save phrase to ramify
#               print 'queue of' , len(self.queue)
                return True
#       print 'fail'
        return False

    def _makeLiteralRule ( self , typ , fet , gens=None , cogs=None ):

        """
        create a temporary dictionary rule for a unknown term

        arguments:
            self  -
            typ   - syntactic type
            fet   - syntactic features
            gens  - generative procedure
            cogs  - cognitive

        returns:
            rule for unknown term
        """

#       print 'makeLiteralRule typ=' , typ , 'gens=' , gens
        r = grammarRule.ExtendingRule(typ,fet)
        r.gens = self.litg if gens == None else gens
        r.cogs = self.litc if cogs == None else cogs
        return r

#
# unit test
#

import sys
import ellyToken

if __name__ == '__main__':

    class M(object):  # dummy derivability matrix
        """ dummy class for testing
        """
        def __init__ ( self ):
            """ initialization
            """
            self.xxx = 0
        def derivable (self,n,gbs):
            """ dummy method
            """
            self.xxx += 1
            return gbs.test(n)

    class R(object):  # dummy grammar rule class
        """ dummy class for testing
        """
        def __init__ (self,n):
            """ initialization
            """
            self.styp = n
            self.sfet = ellyBits.EllyBits()
            self.cogs = None

    class G(object):  # dummy grammar table class
        """ dummy class for testing
        """
        def __init__ (self):
            """ initialization
            """
            self.START = 0
            self.END   = 1
            self.UNKN  = 2
            self.XXX   = 3
            self.NUM   = 4
            self.PUNC  = 5
            self.splits = [ [ ] , [ ] , [ ] , [ ] , [ ] , [ ] ] # must define this!
            self.dctn = { 'abc' : [ R(self.START) ] , 'xyz' : [ R(self.UNKN) ] }
            self.mat  = M()

    class S(object):  # dummy symbol table class
        """ dummy class for testing
        """
        def __init__ ( self ):
            """ initialization
            """
            self.xxx = 6
        def getSyntaxTypeCount(self):
            """ dummy method
            """
            return self.xxx  # for START, END, UNKN, XXX, NUM, PUNC

    print "allocating"
    sym = S()
    grm = G()
    tree = ParseTreeBottomUp(sym,grm,None)
    print "allocated"

    print tree
    print dir(tree)

    fbbs = ellyBits.EllyBits(symbolTable.FMAX)
    gbbs = ellyBits.EllyBits(symbolTable.NMAX)
    gbbs.complement()    # all goal bits turned on

    tree.gbits[0] = gbbs # set all goals in first position

    print '----'
    sgm = 'abc'          # test example in dictionary
    sta = tree.createPhrasesFromDictionary(sgm,False,False)
    print sgm , ':' , sta , ', phlim=' , tree.phlim , 'lastph=' , tree.lastph

    print '----'
    sgm = 'abcd'         # test example not in dictionary
    sta = tree.createPhrasesFromDictionary(sgm,False,False)
    print sgm , ':' , sta,', phlim=' , tree.phlim , 'lastph=' , tree.lastph

    print '----'
    sgm = 'xyz'          # test example in dictionary
    sta = tree.createPhrasesFromDictionary(sgm,False,False)
    print sgm , ':' , sta , ', phlim=' , tree.phlim , 'lastph=' , tree.lastph

    print '----'
    sgm = 'pqr'          # test example not in dictionary
    sta = tree.createUnknownPhrase(ellyToken.EllyToken(sgm))
    print sgm , ':' , sta , ', phlim=' , tree.phlim , 'lastph=' , tree.lastph

    print '----'
    sgm = '.'            # test example not in dictionary
    tree.gbits[0].clear()
    sta = tree.addLiteralPhrase(tree.gtb.PUNC,fbbs)
    print sgm , ':' , sta , ', phlim=' , tree.phlim , 'lastph=' , tree.lastph
    tree.gbits[0].set(tree.gtb.PUNC)
    sta = tree.addLiteralPhrase(tree.gtb.PUNC,fbbs)
    print sgm , ':' , sta , ', phlim=' , tree.phlim , 'lastph=' , tree.lastph

    print ''
    print 'ambiguities:'
    for a in tree.ambig:
        while a != None:
            print '' , a
            a = a.alnk
        print ''

    print '----'
    for rno in range(10,15):
        phrs = tree.makePhrase(0,R(rno))
        tree.enqueue(phrs)
    print '----'
    print 'dequeue phrase=' , tree.dequeue()
    print 'dequeue phrase=' , tree.dequeue()
