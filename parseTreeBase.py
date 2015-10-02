#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# parseTreeBase.py : 30sep2015 CPM
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
        swapped - flag for node swap
    """

    class Kernel(object):

        """
        phrase kernel info - swapped parts of phrase

        attributes:
            rule  - generating rule
            posn  - starting token position in sentence
            typx  - syntax category
            usen  - usage flag for parser
            synf  - syntax features
            semf  - semantic features
            cncp  - semantic concept
            ctxc  - conceptual context
            bias  - plausibility scoring for ambiguity ranking
            seqn  - sequence ID for debugging
            lftd  - descendant phrase
            rhtd  - descendant phrase
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
            self.reset()

        def __unicode__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                summary Unicode string
            """
            cn = '' if self.cncp == conceptualHierarchy.NOname else '/cnc=' + self.cncp

            return ( 'phrase ' + unicode(self.seqn) + ' @' + unicode(self.posn)
                     + ': typ=' + u'{:2d}'.format(self.typx)
                     + ' syn[' + self.synf.hexadecimal() + ']'
                     + ' sem[' + self.semf.hexadecimal() + '] : bia='
                     + unicode(self.bias) + cn +' use=' + unicode(self.usen) )

        def __str__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                summary ASCII string
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
            self.typx = -1
            self.usen = 0
            self.synf.clear()
            self.semf.clear()
            self.cncp = conceptualHierarchy.NOname
            self.ctxc = conceptualHierarchy.NOname
            self.bias = 0
            self.lftd = None
            self.rhtd = None

    class Phrase(object):

        """
        phrase node in a parse tree

        attributes:
            krnl  - kernel info
            llnk  - listing link
            alnk  - ambiguity link
            lens  - token length
            dump  - flag for tree dumping
            tree  - overall parse tree
        """

        def __init__ ( self ):
            """
            initialize node to defaults
            arguments:
                self
            """
            self.krnl = ParseTreeBase.Kernel()
            self.tree = None
            self._reset()

        def __unicode__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                unicode summary string
            """
            return unicode(self.krnl)

        def __str__ ( self ):
            """
            get information summary to support testing
            arguments:
                self
            returns:
                ASCII summary string
            """
            return str(self.krnl)

        def reset ( self ):
            """
            reintialize
            arguments:
                self
            """
            self.krnl.reset()
            self._reset()

        def _reset ( self ):
            """
            reinitialize
            arguments:
                self
            """
            self.llnk = None
            self.alnk = None
            self.dump = True
            self.lens = 0

        def order ( self ):
            """
            bring most plausible phrase to front of ambiguity list
            arguments:
                self  -
            """
            if self.alnk == None:
                return
#           print 'order for phrase' , self
            best = None                   # phrase with best bias so far
            bias = -10000                 # its bias value
            phn = self
            while phn != None:
                if  bias < phn.krnl.bias: # check bias against best far
                    bias = phn.krnl.bias  # update best bias
                    best = phn            # and associated phrase
                phn = phn.alnk

            if best == None:
                return              # no need to order

#           print 'best=' , best

            if self != best:        # need to swap phrases to get best at start
                self.swap(best)
#           print 'self=' , self

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
            oldn = self.krnl.seqn
            newn = othr.krnl.seqn

            delb = self.krnl.bias - othr.krnl.bias   # bias change after swap
            if   delb == 0:                          # done if bias unchanged
                return
            elif delb > 0:
                strt = othr
            else:
                strt = self
                delb = -delb                         # always want positive difference
#           print '  delb=' , delb , 'oldn=' , oldn , 'newn=' , newn

            self.krnl, othr.krnl = othr.krnl, self.krnl
            if self.krnl.lftd == self: self.krnl.lftd = None
#           print '  after swap'
#           print '  self=' , self
#           print '  othr=' , othr

            if self.tree.lowswp > oldn: self.tree.lowswp = oldn
            if self.tree.lowswp > newn: self.tree.lowswp = newn

            cur = None                     # nodes updated this round
            nxt = [ strt ]                 # starting nodes for next round
            while len(nxt) > 0:            # continue until no more rounds
                cur = nxt
                nxt = [ ]
#               print 'propagate up bias change'
                n = self.tree.lowswp + 1   # need to update biases
                while n < self.tree.phlim: # higher up in parse tree
                    phrn = self.tree.phrases[n]
                    n += 1
#                   print ' at' , phrn
                    if phrn.krnl.lftd in cur or phrn.krnl.rhtd in cur:
                        phrn.krnl.bias += delb  # increase bias
#                       print 'new bias=' , phrn.krnl.bias
                        nxt.append(phrn)        # have to continue updating
                                                # up parse tree

            self.tree.swapped = True       # indicate followup is needed
                                           # to update ambiguity resolutions

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
            return ( 'goal ' + unicode(self.seq) + ': typ=' + u'{:2d}'.format(self.cat)
                   + ' for [' + unicode(self.lph) + ']' + ' rul=' + str(n) )

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
        self.lastph = None
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
        self.lastph.krnl.seqn = self.phlim        # set phrase index
        self.lastph.krnl.posn = po                # parse position
        self.lastph.krnl.rule = ru                # grammar rule defining phrase
        self.lastph.krnl.typx = ru.styp           # set syntactic type     from rule
        self.lastph.krnl.synf.combine(ru.sfet)    # set syntactic features from rule
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
    uph.krnl.cncp = 'xccx'
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
    phr3.krnl.bias = 3
    phr4.krnl.bias = 4
    print 'phr3=' , phr3
    print 'phr4=' , phr4
    phr4.swap(phr3)
    print 'phr3=' , phr3
    print 'phr4=' , phr4
