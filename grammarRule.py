#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# grammarRule.py : 16dec2013 CPM
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

class BasicRule(object):

    """
    basic rule structure

    attributes:
        cogs  - cognitive  semantics
        gens  - generative semantics
        styp  - syntactic type produced by rule
        sfet  - syntactic features
        bias  - for rule ordering in ambiguity handling
        seqn  - ID for rule
    """

    _index = 0  # for assigning unique index number to rule 
 
    def __init__ ( self , typ , fet ):

        """
        initialization

        arguments:
            self  -
            typ   - syntactic type
            fet   - syntactic features
        """

        self.cogs = None
        self.gens = None
        self.styp = typ
        self.sfet = fet
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

    def __init__ ( self , typ, fet ):

        """
        initialization

        arguments:
            self  -
            typ   - syntactic type
            fet   - syntactic features
        """

        super(ExtendingRule,self).__init__(typ,fet)
        self.utfet = featureSpecification.FeatureSpecification(None)

    def __unicode__ ( self ):

        """
        show contents for diagnostic code

        arguments:
            self

        returns:
            partial representation as string
        """

        return unicode(self.seqn) + ': ' + unicode(self.styp) + '->' + '--'

class SplittingRule(BasicRule):

    """
    syntax rule of form X->Y Z

    attributes:
        ltfet  - mask for testing features of possible left  subconstituent
        rtfet  - mask for testing features of possible right subconstituent
        rtyp   = syntactic type of right subconstituent
    """

    def __init__ ( self , typ, fet ):

        """
        initialization
        
        arguments:
            self  -
            typ   - syntactic type
            fet   - syntactic features
        """

        super(SplittingRule,self).__init__(typ,fet)
        self.ltfet = featureSpecification.FeatureSpecification(None)
        self.rtfet = featureSpecification.FeatureSpecification(None)
        self.rtyp  = -1
 
    def __unicode__ ( self ):

        """
        show contents for diagnostic code

        arguments:
            self

        returns:
            partial representation as string
        """

        return unicode(self.seqn) + ': ' + unicode(self.styp) + '->' + '-- ' + unicode(self.rtyp)

#########################################################################
# Note that the Y type of a rule is not saved as an attribute of a rule.
# This information is redundant because every rule will be listed under
# its respective Y type. The parsing algorithm implemented for Elly parse
# trees has all the information it needs.
#########################################################################

#
# unit test
#

if __name__ == '__main__':

    import symbolTable

    sym = symbolTable.SymbolTable()

    fs = featureSpecification.FeatureSpecification(sym,'[:f0,f1]')

    r = [ ]

    for i in range(4):
        ru = ExtendingRule(0,fs)
        r.append(ru)
    for i in range(4):
        ru = SplittingRule(0,fs)
        r.append(ru)
    rr = ExtendingRule(0,fs)
    r.append(rr)
    for ru in r:
        print type(ru) , unicode(ru)
    print 'count=' , BasicRule.ruleCount()
