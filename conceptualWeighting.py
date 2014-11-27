#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# conceptualWeighting.py : 04nov2014 CPM
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
compute closeness of concept pairs relative to a given conceptual hierarchy
or a single concept relative to a statistical profile of the most important
concepts seen in current discourse
"""

import conceptualHierarchy

NNC = 12  # nominal number of concepts to list in context profile

class ConceptualWeighting(object):

    """
    for conceptual context

    attributes:
        hiery  - saved conceptual hierarchy
        totln  - total count of concept references
        minmm  - minimum count for concept to be considered
        maxmm  - maximum count for all concepts
        index  - keep track of all concepts referenced
        topcs  - current top concepts (=topics)
    """

    def __init__ ( self , hier ):

        """
        initialize from conceptual hierarchy

        arguments:
            self  -
            hier  - predefined hierarchy
        """

        self.hiery = hier
        self.totln = 0
        self.minmm = 1
        self.maxmm = 0
        self.index = { }
        self.topcs = [ ]

    def recanvass ( self ):

        """
        select currently most important concepts

        arguments:
            self
        """

        kys = self.index.keys()         # all concepts being tracked
        if len(self.topcs) > NNC and self.minmm < self.maxmm:
            self.minmm += 1             # be more selective
        topcs = [ ]
        for ky in kys:
            n = self.index[ky]          # count for next concept
            if n < self.minmm: continue # if too small, just disregard
            k = len(topcs) - 1
            while k >= 0:               # selection sort loop
                r = topcs[k]            # get concepts and counts already selected
                if r[1] >= n: break     # compare previous selected concept with lowest count
                topcs[k+1] = r          # make room for insertion
                k -= 1                  # move up in selection listing
            topcs[k+1] = [ ky , n ]     # insert concept and count into listing
            if self.maxmm < n: self.maxmm = n # update maximum count if needed
        self.topcs = topcs              # replace topics

    def interpretConcept ( self , cn ):

        """
        compute semantic importance score of specified concept

        arguments:
            self  -
            cn    - concept as name string

        returns:
            integer importance score
        """

        if cn == conceptualHierarchy.NOname: return 0
#       print 'importance ' + cn + ':'
        mink = 10000000
        minc = conceptualHierarchy.NOname
        for c in self.topcs:
            k = self.hiery.isA(cn,c)
            if mink > k and k > 0:
                mink = k
                minc = c
        if minc == conceptualHierarchy.NOname: return 0
        self.noteConcept(minc)
        return self.index[minc] - self.minmm

    def relateConceptPair ( self , cna , cnb ):

        """
        compute relatedness score for two specified concepts

        arguments:
            self  -
            cna   - first concept as name string
            cnb   - second

        returns integer relatedness score
        """
        
        if cna == conceptualHierarchy.NOname or cnb == conceptualHierarchy.NOname: return 0
#       print 'relatedness ' + cna + ':' + cnb
        rel = self.hiery.relatedness(cna,cnb)
#       print '=' , rel
        inx = self.hiery.intersection()
#       print 'intersect at' , inx
        if inx != '^':
            self.noteConcept(inx)
        return rel

    def getIntersection ( self ):

        """
        get intersection for last relatedness

        arguments:
            self  -

        returns:
            concept name as string
        """

        inx = self.hiery.intersection()
#       print 'get intersection' , inx
        return conceptualHierarchy.NOname if inx == None else inx.name

    def noteConcept ( self , cn ):

        """
        keep statistics on specified concepts

        arguments:
            self  -
            cn    - specified concept as name string
        """

        if cn == None or cn == conceptualHierarchy.TOP:
            return
        elif not cn in self.index:
            self.index[cn] = 0
        self.index[cn] += 1

#
# unit test
#

if __name__ == '__main__':

    import sys
    import ellyDefinitionReader

    data = [
      "^ > cXXXX" ,
      "cXXXX > cYYYY0" ,
      "cXXXX > cYYYY1" ,
      "cXXXX > cYYYY2" ,
      "cYYYY1> cZZZZ1" ,
      "cYYYY2> cZZZZ2" ,
      "cZZZZ1> cAAAA"  ,
      "cZZZZ1> cBBBB"
    ]

    src = sys.argv[1] if len(sys.argv) > 1 else data

    inp = ellyDefinitionReader.EllyDefinitionReader(src)

    if inp.error != None:
        print >> sys.stderr, inp.error
        sys.exit(1)

    hy = conceptualHierarchy.ConceptualHierarchy(inp)
    wt = ConceptualWeighting(hy)

    si = sys.stdin
    so = sys.stdout

    so.write('> ')

    while True:

        line = si.readline()
        l = line.decode('utf8')
        if len(l) == 0 or l[0] == '\n': break
        ki = 0
        while l[ki] == ' ': ki += 1
        while l[ki] != ' ': ki += 1
        a = l[:ki].strip().upper()
        b = l[ki:].strip().upper()
        arb = wt.relateConceptPair(a,b)
        so.write(a + ":" + b + ", relatedness=" + str(arb) +
                 ' @' + str(wt.getIntersection()) + "\n")
        so.write('> ')
