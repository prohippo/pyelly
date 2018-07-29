#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# compoundTable.py : 23jul2018 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2018, Clinton Prentiss Mah
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
for defining and employing templates for compound multi-word expressions
"""

import sys
import ellyChar
import ellyException
import syntaxSpecification
import featureSpecification
import deinflectedMatching

Catg = 0xE100         # private use Unicode for special template symbols

dCat = unichr(Catg)   # digit substring
cCat = unichr(Catg+1) # capitalized alphabetic substring
uCat = unichr(Catg+2) # uncapitalized
bCat = unichr(Catg+3) # irregular form of TO BE
pCat = unichr(Catg+4) # particle or preposition

Tdel = [ '.' , ' ' , '-' ] # delimiters for template elements
#
# predefined classes of template elements
# (these are specific to English!)
#

preClass = {
  bCat : ['is','am','are','was','were','be','being','been'] ,
}

def numrc ( s ):
    """
    check that all chars are digits
    arguments:
        s  - string
    returns:
        True if string is all digits, False otherwise
    """
    if len(s) == 0: return False
    for c in s:
        if c < '0' or c > '1': return False
    return True

def alphc ( s , cap=False ):
    """
    check that all chars are letters with indicated capitalization
    arguments:
        s   - string
        cap - capitalization flag
    returns:
        True if string is all digits, False otherwise
    """
    if len(s) == 0: return False
    if cap and not s[0].isupper(): return False
    for c in s:
        if ellyChar.isLetter(c): return False
    return True


class Template(object) :

    """
    a template to be matched by words in an input stream

    attributes:

        listing   - elements to be matched
        syntax    - syntax specification

    """

    def __init__ ( self , elems , syns , sym ):

        """
        initialization

        arguments:
            self  -
            elems - template elements as comma-separated string
            syns  - syntax specification for a template match

        exceptions:
            FormatFailure on error
        """

        pass

class CompoundTable(deinflectedMatching.DeinflectedMatching):

    """
    templates for recognizing compound multi-word expressions

    attributes:
        tmpl      - an indexed list of templates
        ucls      - list of user element classes

        _errcount - running input error count
     """

    def __init__ ( self , syms , dfls ):

        """
        initialization

        arguments:
            self  -
            syms  - Elly grammatical symbol table
            dfls  - definition elements in list

        exceptions:
            FormatFailure on error
        """

        super(CompoundTable,self).__init__()

        self.tmpl = { }
        self.ucls = { }

#...    hk = preClass.keys()
#...    for ky in hk:
#...        cx = preClass[ky]
#...        self.tmpl[ky] = (lambda x : x in cx)

#...    self.tmpl[dCat] = (lambda x: numrc(x))
#...    self.tmpl[cCat] = (lambda x: alphc(x,True))
#...    self.tmpl[uCat] = (lambda x: alphc(x,False))

#
# unit test
#

if __name__ == '__main__':

    print '*** this is still only a stub'
