#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PyElly - scripting tool for analyzing natural language
#
# punctuationRecognizer.py : 27jul2015 CPM
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
builtin single-char punctuation recognition for PyElly grammars

provided as a convenience so that these marks do not have to be listed in an
internal dictionary or an external table for every grammar definition

multiple-char punctuation MUST be in an internal or external dictionary!
"""

import ellyBits
import featureSpecification

# NOTE: category and feature names here must be in lower case!
#

category = 'punc' # must be used in grammars for punctuation syntax type!
pID      = '|'    # must be used for punctuation syntactic feature ID

defns = [                                      # syntactic significance of punctuation
    [ u'[' , '[' + pID + '*l]' ] ,             # replacing D: rules in *.g.elly
    [ u']' , '[' + pID + '*r]' ] ,             #
    [ u'(' , '[' + pID + '*l]' ] ,             # you may override with punctuation rules
    [ u')' , '[' + pID + '*r]' ] ,             # but must set higher plausibility for them
    [ u'“' , '[' + pID + '*l,quo,start]' ] ,
    [ u'”' , '[' + pID + '*r,quo]' ] ,
    [ u'"' , '[' + pID + '*l,*r,quo,start]' ] ,
    [ u'‘' , '[' + pID + '*l,quo,start]' ] ,
    [ u'’' , '[' + pID + '*r,quo]' ] ,
    [ u'`' , '[' + pID + '*l,quo,start]' ] ,
    [ u"'" , '[' + pID + '*l,*r,quo,start]' ] ,
    [ u',' , '[' + pID + 'com]' ] ,
    [ u'.' , '[' + pID + 'stop,emb]' ] ,
    [ u'!' , '[' + pID + 'stop,emb]' ] ,
    [ u'?' , '[' + pID + 'stop,emb]' ] ,
    [ u':' , '[' + pID + 'stop,emb]' ] ,
    [ u';' , '[' + pID + 'stop]' ] ,
    [ u'\u2013' ] ,  # en dash
    [ u'\u2014' ] ,  # em dash
    [ u'\u002d' ] ,  # hyphen-minus
    [ u'…' ]         # ellipsis
]

def _FS ( symbls , featrs ):
    """
    get ellyBits encoding of syntactic features
    arguments:
        syms   - symbol table for feature names
        featrs - feature string
    returns:
        ellyBits object on success
    exceptions:
        FormatFailure on error
    """
    return featureSpecification.FeatureSpecification(symbls,featrs).positive

#
## end static definitions
#

class PunctuationRecognizer(object):

    """
    recognizer to support parsing

    attributes:
        catg     - syntactic category for recognized punctuation
        synf     - syntactic features
        hpnc     - hash lookup for punctuation chars
    """

    def __init__ ( self , syms ):

        """
        initialization

        arguments:
            self  -
            syms  - Elly symbol table

        exceptions:
            FormatFailure on error
        """

        zero = ellyBits.EllyBits()
        self.catg = syms.getSyntaxTypeIndexNumber(category)
        self.synf = None
        self.hpnc = { }
        for defn in defns:
            if len(defn) > 1:
                self.hpnc[defn[0]] = _FS(syms,defn[1])
            else:
                self.hpnc[defn[0]] = zero

    def match ( self , s ):

        """
        check whether list of chars corresponds to punctuation

        arguments:
            self  -
            s     - list or string of chars to check (usually an EllyToken root)

        returns:
            True if listed punctuation, False otherwise
        """

        if len(s) != 1:          # only single-char punctuation expected here!
            return False

        schr = s[0]              # possible punctuation char
        if not schr in self.hpnc:
            return False
        else:
            self.synf = self.hpnc[schr] # for later reference along with synf.catg
            return True

#
# unit test
#

if __name__ == '__main__':

    import symbolTable

    ups = u'.?!ab,;:+cd$%&\'\"ef-—“”…hg`i'

    symb = symbolTable.SymbolTable()
    punc = PunctuationRecognizer(symb)

    ft = symb.sxindx[pID]
    del ft['*left']
    del ft['*right']
    print 'punc [| ]:' , ft

    for chu in ups:
        print '[' , chu , ']' ,
        if punc.match(chu):
            print ' is PUNC' , punc.synf.hexadecimal()
        else:
            print ' not PUNC'
