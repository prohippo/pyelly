#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# featureSpecification.py : 03sep2015 CPM
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
import ellyChar
import ellyException
import symbolTable

def scan ( strg ):

    """
    check for extent of feature specification

    arguments:
        strg  - string of chars to scan

    returns:
        char count > 0 on finding possible feature specification, 0 otherwise
    """

    if strg[0] != '[':
        return 0
    n = strg.find(']')
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
            semantic - flag for semantic features

        exceptions:
            FormatFailure on error
        """

        if syms == None or fets == None:  # special case generating zero feature set
            self.positive = ellyBits.EllyBits(symbolTable.FMAX)
            self.negative = ellyBits.EllyBits(symbolTable.FMAX)
            return

        segm = fets.lower()
#       print "features=",segm,"semantic=",semantic
        if segm == None or len(segm) < 3 or segm[0] != '[' or segm[-1] != ']':
            raise ellyException.FormatFailure
        elif segm[1] == ' ' or ellyChar.isLetterOrDigit(segm[1]) or segm[1] == '*':
            raise ellyException.FormatFailure
        else:
            self.id = segm[1]
#           print "id=",self.id
            fs = syms.getFeatureSet(segm[1:-1] , semantic)
            if fs == None:
                raise ellyException.FormatFailure
            self.positive , self.negative = fs

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

    stb = symbolTable.SymbolTable()
    try:
        w = s = "[!a,-b,c,+d,-e]"
        fes = FeatureSpecification(stb,s)       # syntactic features
        print 'fes=' , fes , 'for' , s , 'syntactic'
        fes = FeatureSpecification(stb,s,True)  # semantic  features
        print 'fes=' , fes , 'for' , s , 'semantic'
        w = t = "[:x,y]"
        fet = FeatureSpecification(stb,t,True)  # semantic  features
        print 'fet=' , fet , 'for' , t , 'semantic'
        fet = FeatureSpecification(stb,t,False) # syntactic features
        print 'fet=' , fet , 'for' , t , 'syntactic'
        w = u = ''
        feu = FeatureSpecification(None)        # empty features
        print 'feu=' , feu , 'for' , "''"
        w = v = '[:*l,*r,*unique]'
        fev = FeatureSpecification(stb,v)       # special syntactic features
        print 'fev=' , fev , 'for' , v , 'syntactic'
        w = "[:x"
        few = FeatureSpecification(stb,w)       # bad syntactic features
        print "should never get here!"
    except ellyException.FormatFailure:
        print 'exception: bad format= <<' , w , '>>'
    print '----'
    idns = stb.sxindx.keys()
    print '--' , len(idns) , 'syntactic feature sets'
    for idn in idns:
        print idn , '=' , stb.sxindx[idn]
    idns = stb.smindx.keys()
    print '--' , len(idns) , 'semantic  feature sets'
    for idn in idns:
        print idn , '=' , stb.smindx[idn]
    print '----'
    sts = '[^ab,cd,ef] , xxx'
    num = scan(sts)
    print num , 'feature chars in <<' + sts + '>> with <<' + sts[num:] + '>> left over'
