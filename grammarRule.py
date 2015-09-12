#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# grammarRule.py : 12sep2015 CPM
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
classes for syntax rules with associated semantics
"""

import featureSpecification
import ellyBits

_dfrs = ellyBits.EllyBits()
_dfrs.complement()

class BasicRule(object):

    """
    basic rule structure

    attributes:
        cogs  - cognitive  semantics
        gens  - generative semantics
        styp  - syntactic type produced by rule
        sfet  - syntactic features to set
        sftr  -                    to reset
        bias  - for rule ordering in ambiguity handling
        nmrg  - to indicate degree of merging by rule (1 or 2)
        seqn  - unique ID for rule
    """

    _index = 0  # for assigning unique ID number to rule

    def __init__ ( self , typ , fet ):

        """
        initialization

        arguments:
            self  -
            typ   - syntactic type
            fet   - syntactic features set
        """

        self.cogs = None
        self.gens = None
        self.styp = typ
        self.sfet = fet
        self.sftr = _dfrs
        self.bias = 0
        self.seqn = BasicRule._index
        BasicRule._index += 1

    @staticmethod
    def ruleCount ( ):

        """
        get count of rules defined

        returns:
            count as int
        """

        return BasicRule._index

class ExtendingRule(BasicRule):

    """
    syntax rule of form X->Y

    attributes:
        utfet  - mask for testing features of possible subconstituent
    """

    def __init__ ( self , typ , fet , frs=_dfrs ):

        """
        initialization

        arguments:
            self  -
            typ   - syntactic type
            fet   - syntactic features to set
            frs   -                    to reset
        """

        super(ExtendingRule,self).__init__(typ,fet)
        self.utfet = featureSpecification.FeatureSpecification(None)
        self.sftr  = frs
        self.nmrg  = 1
#       print 'xtd fet=' , fet , 'frs=' , frs

    def __unicode__ ( self ):

        """
        show contents for diagnostic code

        arguments:
            self

        returns:
            partial representation as string
        """

        bhx = self.sfet.hexadecimal(False) + '-' + self.sftr.hexadecimal(False)
        syn = unicode(self.styp) + '[' + bhx + ']'
        msk = unicode(self.utfet)
        cgs = ' cgs:' + str(self.cogs != None)
        return unicode(self.seqn) + ': ' + syn + '->' + '-- ' + msk + cgs

class SplittingRule(BasicRule):

    """
    syntax rule of form X->Y Z

    attributes:
        ltfet  - mask for testing features of possible left  subconstituent
        rtfet  - mask for testing features of possible right subconstituent
        rtyp   = syntactic type of right subconstituent
    """

    def __init__ ( self , typ , fet , frs=_dfrs ):

        """
        initialization

        arguments:
            self  -
            typ   - syntactic type
            fet   - syntactic features to set
            frs   -                    to reset
        """

        super(SplittingRule,self).__init__(typ,fet)
        self.ltfet = featureSpecification.FeatureSpecification(None)
        self.rtfet = featureSpecification.FeatureSpecification(None)
        self.sftr  = frs
        self.rtyp  = -1
        self.nmrg  = 2
#       print 'spl fet=' , fet , 'frs=' , frs

    def __unicode__ ( self ):

        """
        show contents for diagnostic code

        arguments:
            self

        returns:
            partial representation as string
        """

        lms = str(self.ltfet)
        rms = str(self.rtfet)
        ryn = unicode(self.rtyp) + ' ' + rms
        bhx = self.sfet.hexadecimal(False) + '-' + self.sftr.hexadecimal(False)
        syn = unicode(self.styp) + '[' + bhx + ']'
        cgs = ' cgs:' + str(self.cogs != None)
        return unicode(self.seqn) + ': ' + syn + '->' + '-- ' + lms + '  ' + ryn + cgs

###########################################################################
# Note that the Y type of a syntax rule is not saved as an attribute of it.
# This information is redundant because every rule will be listed under its
# respective Y type. The parsing algorithm implemented for Elly parse trees
# will have all the information it needs.
###########################################################################

#
# unit test
#

if __name__ == '__main__':

    import symbolTable

    sym = symbolTable.SymbolTable()

    fs = featureSpecification.FeatureSpecification(sym,'[:f0,f1,-f2]')
    pf = fs.positive
    nf = fs.negative
    nf.complement()
    print 'features=' , pf , nf

    r = [ ]

    for i in range(4):
        ru = ExtendingRule(0,pf,nf)
        r.append(ru)
    for i in range(4):
        ru = SplittingRule(0,pf,nf)
        r.append(ru)
    rr = ExtendingRule(0,pf)
    r.append(rr)
    for ru in r:
        print type(ru) , unicode(ru)
    print 'count=' , BasicRule.ruleCount()
