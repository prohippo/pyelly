#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# conceptualHierarchy.py : 04nov2014 CPM
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
modeling hierarchical relationships between semantic concepts used for
disambiguation, mostly IS_A links
"""

import sys
import ellyChar
import ellyException

NOname = '--' # name for None concept

FRAC = 20     # fraction of descendant nodes for important concept
TOP  = '^'    # mandatory name of top concept in hierarchy

class Concept:

    """
    individual concept node in hierarchy

    attributes:
        name     - unique concept name
        level    - 0 for top of hierarchy and increasing by 1 for each step down
        parent   - next higher node in hierarchy
        children - inverse for parent
        split    - child count
        total    - of all descendants
        alias    - alternate names
        unseen   - flag for algorithm to get total
    """

    def __init__ ( self , name ):
        """
        initialization

        arguments:
            self  -
            name  - unique concept identifier
        """
        self.name = name
        self.level = -1     # initially undefined
        self.parent = None  #
        self.children = [ ] #
        self.split = 0
        self.total = 0
        self.alias = [ ]
        self.unseen = True

    def __str__ ( self ):
        """
        string representation

        arguments:
            self  -
        returns:
            short string representation
        """
        pname  = NOname if self.parent == None else self.parent.name
        if self.split == 0:
            chs = ''
        else:
            label  = ' child' if self.split == 1 else ' children'
            chs = ': with ' + str(self.split) + label
        return self.name + '(' + str(self.total) + ')<' + pname + chs

class ConceptualHierarchy:

    """
    hierarchy of concepts after the approach of WordNet 

    attributes:
        index     - dictionary of concepts
        inters    - any computed conceptual intersection

        _errcount - how many errors found in input
    """

    def getConcept ( self , name ):

        """
        get concept, creating if necessary in index under name

        arguments:
            self  -
            name  - of concept

        returns:
            concept for name other than NOname, otherwise None
        """

        name = name.strip().upper()
        if name == NOname: return None
        elif name == TOP: return self.index[TOP]
        elif len(name) == 0 or not ellyChar.isLetterOrDigit(name[0]): return None
        elif name in self.index: return self.index[name]
        for x in name:
            if not ellyChar.isLetterOrDigit(x): return None
        c = Concept(name)
        self.index[name] = c
        return c

    def __init__ ( self , defn=None ):

        """
        initialization

        arguments:
            self  -
            defn  - ellyDefinitionReader for defining a hierarchy

        exceptions:
            TableFailure on error
        """

        self._errcount = 0

        top = Concept(TOP)           # define the top of hierarchy
        top.level = -1               #
        self.index = { TOP : top }   #

        self.inters = None           # no intersection yet

        eqv = [ ]                    # for equivalences

        if defn == None: return      # make empty tree on no definition

#       print "READING HIERARCHY INPUT"

        while True:
            l = defn.readline()      # read in hierarchy definition, link by link
            if len(l) == 0: break
            if l[0] == '=':
                sl = l               # save for error reporting
                l = l[1:].lstrip().upper()
                k = l.find(' ')
                if k < 0:
                    self._err('incomplete equivalence',sl)
                    continue
                s = l[:k]
                l = l[k:].lstrip()
                eqv.append([ s , l ])
                continue
            ls = l.split('>')        # get pair of concepts in link
#           print 'ls=' , ls
            if len(ls) > 2:
                self._err('malformed link',l)
                continue
            elif len(ls) < 2 or len(ls[0]) == 0 or len(ls[1]) == 0:
                self._err('incomplete link',l)
                continue
            cPA = self.getConcept(ls[0]) # parent in link
            cCH = self.getConcept(ls[1]) # child
            if cPA == None or cCH == None:
                self._err('bad concept name',l)
                continue
            if cCH.parent != None:
                self._err('child has two parents' , l)
                continue
            else:
                cPA.split += 1
                cCH.parent = cPA         # save upward link
                cPA.children.append(cCH) # save downward link
#               print >> sys.stderr , 'parent=' , str(cPA) ,
#               print >> sys.stderr , ','.join(map( lambda x: x.name , cPA.children ))

#       print "DEFINING EQUIVALENCES

        for p in eqv:
#           print 'p=' , p
            if not p[0] in self.index:
                self._err('bad alias:' , p[1])
                continue
            c = self.index[p[0]]     # known concept
            self.index[p[1]] = c     # define alias for that concept
            p1l = p[1].lower()       #
            c.alias.append(p1l)      # add to list of aliases

#       print "CHECKING HIERARCHY COMPLETENESS"

        cnls = self.index.keys()
        for cn in cnls:              # check that every concept except top has parent
            if cn != TOP:
                c = self.index[cn]
                if c.parent == None:
                    print >> sys.stderr , '** missing parent for' , cn
                    self._errcount += 1

#       print "CHECKING POPULATION AND CONNECTION"

        if len(top.children) == 0 and len(cnls) > 1:
            self._err('no connection to top of hierarchy')

        if self._errcount > 0:
            print >> sys.stderr , '**' , self._errcount , 'concept errors in all'
            print >> sys.stderr , 'conceptual hierarchy compilation FAILed'
            raise ellyException.TableFailure

#       print "GETTING TOTALS FOR CONCEPTS"

        for c in cnls:
            cn = self.index[c]
            if cn.split == 0 and cn.unseen: # get leaf nodes not yet seen
#               print 'at' , cn
                cn.unseen = False
                n = 0                       # accumulated count going up tree
                while cn != top:
                    cn.total += n           # increment concept descendant total
                    cn = cn.parent
                    n += 1
#               print 'n=' , n
                cn.total += n               # this should be for top concept

#       print "ASSIGNING HIERARCHY LEVELS"

        stk = [ ]                    # for depth-first hierarchy tree traversal

        stk.append([top])            # start at top

        while len(stk) > 0:          
            cs = stk[-1]             # list of nodes left to traverse at current level
            if len(cs) == 0:
                stk.pop()            # if empty, go back up one level
#               print >> sys.stderr , 'pop:' , len(stk)
            else:
#               print >> sys.stderr , 'next node:' , len(cs) , c
                c = cs.pop()         # get next concept node at current level
                if c.level >= 0:     # visited already?
                    self._err('bad tree' , str(c) , c.level , len(stk) )
                    break            # error because of loop in tree
                c.level = len(stk)-1 # assign next concept a level number
                stk.append(c.children)  # go down a level

#       print "HIERARCHY DONE"

        if self._errcount > 0:
            print >> sys.stderr , 'conceptual hierarchy generation FAILed'
            raise ellyException.TableFailure

        print len(cnls),"concepts in full index"

    def intersection ( self ):

        """
        get intersection of last hierarchical operation

        arguments:
            self

        returns:
            saved concept intersection (not string!)
        """

        return self.inters

    def _err ( self , s , l='' , lvl=None , dep=None ):

        """
        for error handling

        arguments:
            self  -
            s     - error message
            l     - problem line
            lvl   - level in tree
            dep   - depth in traversal stack
        """

        self._errcount += 1
        print >> sys.stderr , '** concept error:' , s
        if l != '':
            print >> sys.stderr , '*  with [' , l , ']' ,
            if lvl == None:
                print >> sys.stderr , ''
            else:
                print >> sys.stderr , str(lvl) + '/' + str(dep)

    def isEmpty ( self ):

        """
        check contents of hierarchy

        arguments:
            self

        returns:
            True if empty, False otherwise
        """

        return (len(self.index) <= 1)

    def generalize ( self , an ):

        """
        get nontrivial generalization of concept

        arguments:
            self  -
            an    - concept name

        returns:
            concept name on success, -- otherwise
        """

        n = int(len(self.index)/FRAC) # set threshold for nontriviality
#       print "generalization threshold=" , n , "an=" , an
        if an == TOP:                 # if name is TOP, done
            return TOP
        elif not an in self.index:    # check if name in hierarcy
            return NOname
        else:                         # otherwise, try going up in inverted tree
            a = ab = self.index[an]
            while a != None and a.total <= n and a.level > 4:
#               print 'concept=' , a
                ab = a
                a = a.parent
#           print 'generalized concept=' , a
            return ab.name

    def isA ( self , an , bn ):

        """
        test whether a concept is subsumed by another concept

        arguments:
            self  -
            an    - name of first concept
            bn    - name of second

        returns:
            level difference >= 0 on subsumation, -1 otherwise
        """

        self.inters = None               # reset saved intersection
        if not an in self.index or not bn in self.index: return -1
        a = self.index[an]
        b = self.index[bn]
        if a.level < b.level: return -1  # b cannot subsume a?
        c = a
        while c.level > b.level:         # get c at same level of b, c subsuming a
            c = c.parent
        if b == c:                       # is c the same as b?
            self.inters = c              # if so, b subsumes a
            return a.level - b.level     #
        else:
            return -1                    # otherwise, a and b are independent

    def relatedness ( self , an , bn ):

        """
        compute relatedness score between two concepts

        arguments:
            self  -
            an    - name of first concept
            bn    - name of second

        returns:
            length of hierarchical path between known concepts, otherwise -1
        """

#       print >> sys.stderr , "relating:" , an , bn
        if not an in self.index or not bn in self.index: return -1
        a = self.index[an]
        b = self.index[bn]
#       print >> sys.stderr , a , b
        while a.level < b.level:  # get a and b at same level
            b = b.parent          #
        while a.level > b.level:  #
            a = a.parent          #
        while a != b:             # keep going up in tree until paths converge
            a = a.parent          # (this has to happen at top concept)
            b = b.parent          #
        self.inters = a
        return a.level

#
# unit test
#

if __name__ == "__main__":

    import ellyDefinitionReader

    data = [
        "=A1 otherA1",
        "^>A1","^>B1","^>C1",
        "A1>A1X2","A1>A1Y2",
        "B1>B1X2","B1>B1Y2",
        "=B1 otherB1",
        "C1>C1X2","C1>C1Y2",
        "A1X2>A1X2R3","A1X2>A1X2S3",
        "A1X2S3>A1X2S3T3","A1X2S3>A1X2S3T4",
        "^>K0","K0>K1","K1>K2","K2>K3","K3>K4","K4>K5"
    ]

    def tisA ( tre , a , b ):
        """ test isA
        """
        k = tre.isA(a.upper(),b.upper())
        x = tre.intersection().name if k >= 0 else NOname
        print "isA(" + a + "," + b + ")=" ,
        print k , "superconcept=" , x

    def trelatedness ( tre , a , b ):
        """ test relateness
        """
        k = tre.relatedness(a.upper(),b.upper())
        x = tre.intersection().name if k >= 0 else NOname
        print "relatedness(" + a + "," + b + ")=" ,
        print k , "intersection=" , x

    def tdump ( tre ):
        """ show hierarchy tree
        """
        kyl = tre.index.keys()
        for ky in kyl:
            if ky == '^': continue
            r = tre.index[ky]
            print ky , '(' , r.name , ')' , 'lvl=' , r.level , '<' , r.parent.name

    filn = sys.argv[1] + '.h.elly' if len(sys.argv) > 1 else data
    inp = ellyDefinitionReader.EllyDefinitionReader(filn)
    if inp.error != None:
        print >> sys.stderr , inp.error
        sys.exit(1)
    elif filn != data:
        print >> sys.stderr , 'reading from file=' , filn
    print inp.linecount(),"lines read"

    try:
        ctre = ConceptualHierarchy(inp)
    except ellyException.TableFailure:
        print >> sys.stderr , 'could not load hierarchy'
        sys.exit(1)

    if ctre.isEmpty():
        print "tree building failed"
    elif filn == data:
        print "-------- concepts and aliases"
        tdump(ctre)
        print "-------- connections"
        tisA(ctre,'C1X2','C1X2')
        tisA(ctre,'A1X2S3T4','A1X2S3T4')
        tisA(ctre,'A1X2S3T4','A1')
        tisA(ctre,'A1','A1X2S3T4')
        trelatedness(ctre,'C1Y2','C1Y2')
        trelatedness(ctre,'A1','A1X2')
        trelatedness(ctre,'A1X2','A1')
        trelatedness(ctre,'B1X2','A1X2S3')
        trelatedness(ctre,'A1X2S3','B1X2')
        trelatedness(ctre,'OA1','OB1')
        trelatedness(ctre,'X1','X1')
        print "-------- lookup"
        print ctre.index['A1X2S3T4']
        print ctre.index['K3']
        print "-------- generalization"
        print ctre.generalize('A1X2S3T4')
    else:
        print "-------- concepts and aliases"
        tdump(ctre)
