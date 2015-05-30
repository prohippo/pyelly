#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# parseTreeBase.py : 28may2015 CPM
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
support for syntax analysis with preallocated, extensible arrays of data elements
"""

import symbolTable
import conceptualHierarchy
import ellyConfiguration
import ellyException
import ellyBits
import sys

NOMINAL = 256 # default starting allocation for phrases and goals

class ParseTreeBase(object):

    """
    data structures for implementing an Elly parse tree

    attributes:
        phrases - preallocated phrase nodes
        goals   - preallocated gaals
        phlim   - phrase allocation limit
        glim    - goal   allocation limit
        lastph  - last phrase allocated
        lowswp  - lowest swapped sequence number
        hghswp  - highest
        swapped - flag for node swap
    """

    class Phrase(object):

        """
        phrase node in a parse tree

        attributes:
            rule  - generating rule
            posn  - starting token position in sentence
            lftd  - descendant phrase
            rhtd  - descendant phrase
            typx  - syntax category
            usen  - usage flag for parser
            synf  - syntax features
            semf  - semantic features
            cncp  - semantic concept
            ctxc  - conceptual context
            llnk  - listing link
            alnk  - ambiguity link
            bias  - plausibility scoring for ambiguity ranking
            lens  - token length
            seqn  - sequence ID for debugging
            dump  - flag for tree dumping
            tree  - overall parse tree
        """

        def __init__ ( self ):
            """
            initialize node to defaults
            arguments:
                self
            """

            self.synf = ellyBits.EllyBits(symbolTable.FMAX)
            self.semf = ellyBits.EllyBits(symbolTable.FMAX)
            self.seqn = -1
            self.tree = None
            self.reset()

        def __unicode__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                summary string
            """

            cn = '' if self.cncp == conceptualHierarchy.NOname else '/' + self.cncp

            return ( 'phrase ' + unicode(self.seqn) + ' @' + unicode(self.posn)
                     + ': type=' + unicode(self.typx) + ' [' + self.synf.hexadecimal() + ']'
                     + ' [' + self.semf.hexadecimal() + '] : '
                     + unicode(self.bias) + cn + ' use=' + str(self.usen) )

        def __str__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                summary string
            """

            return unicode(self).encode('utf8')

        def reset ( self ):
            """
            reintialize
            arguments:
                self
            """

            self.rule = None
            self.posn = -1
            self.lftd = None
            self.rhtd = None
            self.typx = -1
            self.usen = 0
            self.synf.clear()
            self.semf.clear()
            self.cncp = conceptualHierarchy.NOname
            self.ctxc = conceptualHierarchy.NOname
            self.llnk = None
            self.alnk = None
            self.bias = 0
            self.lens = 0
            self.dump = True

        def order ( self ):
            """
            bring most plausible phrase to front of ambiguity list
            arguments:
                self  -
            """

            if self.alnk == None:
                return
#*          print 'ordering ambiguities for phrase' , self
            best = None             # phrase with best bias so far
            bias = -10000           # its bias value
            phn = self
            while phn != None:
                if bias < phn.bias: # check bias against best far
                    bias = phn.bias # update best bias
                    best = phn      # and associated phrase
                phn = phn.alnk

            if best == None:
                return              # no need to order

#           print 'best bias=' , bias

            if self != best:        # need to swap phrases to get best at start
                self.swap(best)

        def swap ( self , othr ):

            """
            exchange basic contents of two phrase nodes

            arguments:
                self  -
                othr  - phrase to swap with
            """

#           print '  swap phrase node contents'
#           print '  self=' , self
#           print '  othr=' , othr
            oldn = self.seqn
            newn = othr.seqn
            delb = self.bias - othr.bias
#           print '  delb=' , delb
            self.rule, othr.rule = othr.rule, self.rule
            self.lftd, othr.lftd = othr.lftd, self.lftd
            self.rhtd, othr.rhtd = othr.rhtd, self.rhtd
            self.bias, othr.bias = othr.bias, self.bias
            self.cncp, othr.cncp = othr.cncp, self.cncp
            self.ctxc, othr.ctxc = othr.ctxc, self.ctxc
            self.seqn = newn
            othr.seqn = oldn
            if self.lftd == self: self.lftd = None

#           print '  result'
#           print '  self=' , self
#           print '  othr=' , othr
            if self.tree.lowswp > oldn: self.tree.lowswp = oldn
            if self.tree.lowswp > newn: self.tree.lowswp = newn
            if self.tree.hghswp < oldn: self.tree.hghswp = oldn
            if self.tree.hghswp < newn: self.tree.hghswp = newn

#           print '  delb=' , delb , 'oldn=' , oldn , 'newn=' , newn
            if delb == 0: return           # should never return
            iteration = range(self.tree.lowswp,self.tree.hghswp + 1)
#           print 'iteration=' , iteration

            cur = [ ]                      # nodes updated this round
            nxt = [ othr ]                 # starting nodes for next round
            while len(nxt) > 0:            # continue until all nodes updated
                cur = nxt
                nxt = [ ]
#               print 'iterating'
                for n in iteration:        # only these nodes might be updated
                    phrn = self.tree.phrases[n]
#                   if phrn.seqn <= oldn: continue
#                   print ' at' , phrn
                    if phrn.lftd in cur or phrn.rhtd in cur:
                        phrn.bias += delb
#                       print ' >> ' , phrn.bias
                        nxt.append(phrn)

            self.tree.swapped = True       # indicate followup is needed

    class Goal(object):

        """
        goal for generating phrase to complete 2-branch rule

        attributes:
            cat   - syntax category
            lph   - phrase already found
            rul   - rule to be completed for phrase
            seq   - sequence ID for debugging
        """

        _sqn = 0

        def __init__ ( self ):
            """
            initialize attributes to defaults
            arguments:
                self
            """
            self.cat = 0
            self.lph = None
            self.rul = None
            self.seq = -1

        def __unicode__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                summary string
            """

            n = self.rul.seqn
            return ( 'goal ' + unicode(self.seq) + ': type=' + unicode(self.cat)
                    + ' for [' + unicode(self.lph) + ']' + ' [rule= ' + str(n) + ']' )

        def __str__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                summary string
            """

            return unicode(self).encode('utf8')

    def __init__ ( self ):

        """
        initialize attributes, including preallocated nodes for parsing

        arguments:
            self
        """

#       print "at ParseTreeBase.__init__()"
        self.phrases = [ ]
        self.goals   = [ ]
        npre = ellyConfiguration.phraseLimit
        if npre > NOMINAL: npre = NOMINAL
        for i in range(npre):           # preallocate phrases and goals
            phrase = self.Phrase()      # get phrase
            phrase.tree = self          # associate with tree
            self.phrases.append(phrase)
            goal = self.Goal()          # get goal
            goal.seq = i                # assign ID
            self.goals.append(goal)
        self.reset()
#       print "leaving ParseTreeBase.__init__()"

    def reset ( self ):

        """
        reset parse tree for new input

        arguments:
            self
        """

#       print "ParseTreeBase.reset()"
        self.phlim = 0
        self.glim  = 0
        self.lastph = None
        self.lowswp = 1000000
        self.hghswp = 0
        self.swapped = False

    def _limitCheck ( self ):

        """
        exit if too many phrase nodes allocated

        arguments:
            self

        returns:
            True if limit reached, False otherwise
        """

        if self.phlim == ellyConfiguration.phraseLimit:
            print >> sys.stderr , '\n'
            print >> sys.stderr , '** nominal phrase limit of' , ellyConfiguration.phraseLimit , 'reached!'
            print >> sys.stderr , '** either increase ellyConfiguration.phraseLimit or reduce ambiguous rules'
            return True
        else:
            return False

    def makePhrase ( self , po , ru ):

        """
        allocate a phrase node for a sentence position with a syntax rule

        arguments:
            po   - position
            ru   - rule (can be extending or splitting)

        returns:
            new phrase node

        exceptions:
            ParseOverflow
        """

        if self.phlim >= len(self.phrases):       # do we have to allocate more phrases?
            if self._limitCheck():                # if so, first check for runaway analysis
                raise ellyException.ParseOverflow # on reaching limit, signal overflow
            phrase = self.Phrase()                # otherwise, continue with allocation
            phrase.tree = self                    # identify where phrase belongs
            self.phrases.append(phrase)
        self.lastph = self.phrases[self.phlim]    # get next available phrase
        self.lastph.reset()                       #
        self.lastph.seqn = self.phlim             # set phrase index
        self.lastph.posn = po                     # parse position
        self.lastph.rule = ru                     # grammar rule defining phrase
        self.lastph.typx = ru.styp                #
        self.lastph.synf.combine(ru.sfet)         # set syntactic features from rule
        self.phlim += 1
#       print 'make' , self.lastph
        return self.lastph

    def makeGoal ( self , ru , ph ):

        """
        allocate a goal node for a phrase and a splitting syntax rule

        arguments:
            self  -
            ru    - splitting rule
            ph    - phrase

        returns:
            goal node if successful
        """

        if self.glim >= len(self.goals):
            goal = self.Goal()
            self.goals.append(goal)
        g = self.goals[self.glim]
        g.cat = ru.rtyp
        g.lph = ph
        g.rul = ru
        g.seq = self.glim
        self.glim += 1
        return g

#
# unit test
#

if __name__ == '__main__':

    class R(object):
        """
        fake grammar rule class
        """
        def __init__ (self , m , n=0):
            self.styp = m
            self.sfet = ellyBits.EllyBits()
            self.rtyp = n
            self.seqn = 10000

    tree = ParseTreeBase()
    print tree
    print dir(tree)
    print ""

    print '** CHECK PHRASE AND GOAL ALLOCATION'
    phs = [ ]

    phs.append(tree.makePhrase(0,R(100,10)))
    phs.append(tree.makePhrase(1,R(101,11)))
    phs.append(tree.makePhrase(2,R(102,12)))

    for phr in phs:
        print ' =' , phr
    print 'phlim =' , tree.phlim
    print 'lastph=' , tree.lastph

    tree.reset()
    print '** RESET'
    print 'phlim=' , tree.phlim

    r = R(103,13)

    print '** MAKE NEW PHRASE'
    uph = tree.makePhrase(2,R(104,14))
    uph.cncp = 'xccx'
    print 'new phrase=' , uph
    print 'phlim=' , tree.phlim
    print 'glim =' , tree.glim
    print 'lastph=' , tree.lastph

    print '** MAKE NEW GOAL'
    ug = tree.makeGoal(r,uph)
    print 'new goal=' , ug
    print 'glim =' , tree.glim

    print '** RESET'
    tree.reset()
    print 'glim =' , tree.glim

    print '** SWAP'
    phr3 = tree.makePhrase(1,R(103,11))
    phr4 = tree.makePhrase(1,R(104,11))
    print 'phr3=' , phr3
    print 'phr4=' , phr4
    phr3.bias = 3
    phr4.bias = 4
    print 'phr3=' , phr3
    print 'phr4=' , phr4
    phr3.swap(phr4)
    print 'phr3=' , phr3
    print 'phr4=' , phr4
