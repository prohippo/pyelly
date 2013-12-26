#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# conceptualHierarchy.py : 17sep2013 CPM
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
modeling 'IS A' relationships between semantic concepts used for disambiguation
"""

TOP = '^'  # mandatory name of top concept in hierarchy

class Concept:

    """
    individual concept node in hierarchy

    attributes:
        name   - unique concept name
        level  - 0 for top of hierarchy and increasing by 1 for each step down
        parent - next higher node in hierarchy
    """

    def __init__ ( self , name ):
        self.name = name
        self.level = -1    # initially undefined
        self.parent = None #

class ConceptualHierarchy:

    """
    hierarchy of concepts after the approach of WordNet 

    attributes:
        index  - dictionary of concepts
        inters - any computed conceptual intersection
    """

    def getConcept ( self , name ):

        """
        get concept, creating if necessary in index under name

        arguments:
            self  -
            name  - of concept

        returns:
            concept
        """

        if name in self.index: return self.index[name]
        c = Concept(name)
        self.index[name] = c
        return c

    def __init__ ( self , defn=None ):

        """
        initialization

        arguments:
            self  -
            defn  - ellyDefinitionReader for defining a hierarchy
        """

        top = Concept(TOP)           # define the top of hierarchy
        top.level = 0                #
        self.index = { TOP : top }   #

        self.inters = None           # no intersection yet

        if defn == None: return      # make empty tree on no definition

        bkl = { }                    # for saving down links temporarily
        bkl[top] = [ ]               # to allow automatic level assignments

        print "READING INPUT"

        while True:
            l = defn.readline()      # read in hierarchy definition, link by link
            if len(l) == 0: break
            ls = l.split('>')        # get pair of concepts in link
            if len(ls) < 2: continue
            cpa = self.getConcept(ls[0].strip()) # parent in link
            cch = self.getConcept(ls[1].strip()) # child
            cch.parent = cpa         # save upward link
            if not cpa in bkl:       # set up to record down links
                bkl[cpa] = [ ]
            if not cch in bkl:       #
                bkl[cch] = [ ]
            bkl[cpa].append(cch)     # save downward link

        print "CHECKING COMPLETENESS"

        cnls = self.index.keys()
        for cn in cnls:              # check that every concept except top has an up link
            if cn != TOP:
                c = self.index[cn]
                if c.parent == None:
                    self.index = { } # return with no tree if any node lacks an up link
                    return

        print len(self.index),"in index,",len(bkl),"with backlinks"

        print "ASSIGNING LEVELS"

        stk = [ ]                    # for depth-first hierarchy tree traversal

        stk.append([top])            # start at top

        while len(stk) > 0:          
            cs = stk[-1]             # list of nodes left to traverse at current level
            if len(cs) == 0:
                stk.pop()            # if empty, go back up one level
            else:
                c = cs.pop()         # get next concept node at current level
                if c.level >= 0:     # visited already?
                    self.index = { } # if so, error because of loop in tree
                c.level = len(stk)   # assign next concet a level number
                stk.append(bkl[c])   # go down a level

        print "DONE"

    def intersection ( self ):

        """
        get intersection of last hierarchical operation

        arguments:
            self

        returns:
            saved intersection
        """

        return self.inters

    def isEmpty ( self ):

        """
        check contents of hierarchy

        arguments:
            self

        returns:
            True if empty, False otherwise
        """

        return (len(self.index) == 0)

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

        if not an in self.index or not bn in self.index: return -1
        a = self.index[an]
        b = self.index[bn]
        if a.level < b.level: return -1  # b cannot subsume a?
        c = a
        while c.level > b.level:         # get c at same level of b, c subsuming a
             c = c.parent
        if b == c:                       # is c the same as b?
             self.inters = c             # if so, b subsumes a
             return a.level - b.level    #
        else:
             self.inters = None          # otherwise, a and b are independent
             return -1                   #

    def relatedness ( self , an , bn ):

        """
        compute relatedness score between two concepts

        arguments:
            self  -
            an    - name of first concept
            bn    - name of second

        returns:
            length of hierarchical path between concepts
        """

        if not an in self.index or not bn in self.index: return -1
        c = a = self.index[an]
        d = b = self.index[bn]
        while c.level < d.level:  # get c and d at same level
            d = d.parent          #
        while c.level > d.level:  #
            c = c.parent          #
        while c != d:             # keep going up in tree until paths converge
            c = c.parent          # (this has to happen at top concept)
            d = d.parent          #
        self.inters = c
        return c.level

#
# unit testing
#

if __name__ == "__main__":

    import sys
    import ellyDefinitionReader

    data = [
        "^>A1","^>B1","^>C1",
        "A1>A1X2","A1>A1Y2",
        "B1>B1X2","B1>B1Y2",
        "C1>C1X2","C1>C1Y2",
        "A1X2>A1X2R3","A1X2>A1X2S3",
        "A1X2S3>A1X2S3O4"
    ]

    inp = ellyDefinitionReader.EllyDefinitionReader(data)
    if inp.error != None:
        sys.exit(1)
    print inp.linecount(),"lines"
    tre = ConceptualHierarchy(inp)
    if tre.isEmpty():
        print "tree building failed"
    else:
        kyl = tre.index.keys()
        for ky in kyl:
            if ky == '^': continue
            r = tre.index[ky]
            print r.name,r.level,r.parent.name
        print tre.isA('C1X2','C1X2') ,
        print "superconcept=",tre.intersection().name
        print tre.isA('A1X2S3O4','A1X2S3O4') ,
        print "superconcept=",tre.intersection().name
        print tre.isA('A1X2S3O4','A1') ,
        print "superconcept=",tre.intersection().name
        print tre.isA('A1','A1X2S3O4') ,
        print "superconcept=",tre.intersection().name
        print tre.relatedness('C1Y2','C1Y2') ,
        print "intersection=",tre.intersection().name
        print tre.relatedness('A1','A1X2') ,
        print "intersection=",tre.intersection().name
        print tre.relatedness('A1X2','A1') ,
        print "intersection=",tre.intersection().name
        print tre.relatedness('B1X2','A1X2S3') ,
        print "intersection=",tre.intersection().name
        print tre.relatedness('A1X2S3','B1X2') ,
        print "intersection=",tre.intersection().name
