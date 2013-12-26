#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# featureSpecification.py : 16dec2013 CPM
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
handling of specifications of both syntactic and semantic features
"""

import ellyBits
import grammarTable

def scan ( str ):

    """
    check for extent of feature specification

    arguments:
        str  - string of chars to scan

    returns:
        char count > 0 on finding possible feature specification, 0 otherwise
    """

    if str[0] != '[':
        return 0
    n = str.find(']')
    return n + 1 if n > 0 else 0

class FeatureSpecification(object):

    """
    encoding of features as bits

    attributes:
        positive  - positive features
        negative  - negative
        id        - which feature set
    """

    def __init__ ( self , syms , fets=None , semantic=False ):

        """
        initialization

        arguments:
            self     -
            syms     - symbol table
            fets     - string representation of feature set
            semantic - flag semantic feature
        """

        segm = fets.lower() if fets != None else '[?]'
#       print "features=",segm
        if segm == None or len(segm) < 4 or segm[0] != '[' or segm[-1] != ']':
            self.id = ''                                         # this is unknown
            self.positive = ellyBits.EllyBits(grammarTable.FMAX) # set to zeros
            self.negative = ellyBits.EllyBits(grammarTable.FMAX) #
        else:
            self.id = segm[1]
#           print "id=",self.id
            if not self.id in syms.fsindx:
                d = { }                  # new dictionary of feature names
                if not semantic:
                    d['*r'] = 0          # always define '*r' as syntactic feature
                    d['*right'] = 0      # equivalent to '*r'
                syms.fsindx[self.id] = d #   and save
            self.positive , self.negative = syms.getFeatureSet(segm[1:-1])

    def __str__ ( self ):

        """
        representation of features

        arguments:
            self

        returns:
            string
        """

        return '+' + self.positive.hexadecimal(False) + '-' + self.negative.hexadecimal(False)

    def getCompoundedFeatures ( self ):

        """
        combine feature bit string with its complement for testing

        arguments:
            self 

        returns:
            joined bit string to be tested
        """

        return self.positive.compound()

    def makeTest ( self ):

        """
        concatenate positive and negative bits of feature set for testing

        arguments:
            self

        returns:
            joined bit string to be applied in testing
        """

        return ellyBits.join(self.positive,self.negative)

#
# unit test
#

if __name__ == '__main__':

    import symbolTable

    stb = symbolTable.SymbolTable()
    s = "[!a,-b,c,+d,-e]"
    fs = FeatureSpecification(stb,s)            # syntactic features
    print 'fs=' , fs , 'for' , s
    t = "[:x,y]"
    ft = FeatureSpecification(stb,t,'semantic') # semantic features
    print 'ft=' , ft , 'for' , t
    ids = stb.fsindx.keys()
    print 'feature sets'
    for id in ids:
        print id , '=' , stb.fsindx[id]
    print '----'
    st = '[^ab,cd,ef] ,'
    n = scan(st)
    print n , '<' + st[:n] + '>'
