#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# parseTest.py : 09nov2013 CPM
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
support for unit testing only
"""

import ellyBits
import ellyBuffer
import grammarTable
import symbolTable

class Phrase(object):          # dummy Elly phrase node for testing
    def __init__ ( self ):
        self.catg = 0
        self.synf = ellyBits.EllyBits(grammarTable.FMAX)
        self.lens = 0
    def __str__ ( self ):
       return ( 'phrase catg=' + str(self.catg) +
                      ' synf=' + self.synf.hexadecimal() +
                      ' lens=' + str(self.lens) )

class Tree(object):            # dummy Elly parse tree for testing
    def __init__ ( self ):
        print 'tree with stub methods'
        self.lastph = Phrase()
    def addLiteralPhrase(self,typ,fts):
        print 'add phrase: typ=' , typ
        self.lastph.catg = typ
        self.lastph.synf = fts
        return True

class Context(object):         # dummy Elly interpretive context for testing
    def __init__ ( self ):
        print 'context with empty symbol table'
        syms = symbolTable.SymbolTable()
        syms.getSyntaxTypeIndexNumber('sent') # seed with syntactic types for test
        syms.getSyntaxTypeIndexNumber('end')  #
        syms.getSyntaxTypeIndexNumber('noun') #
        syms.getSyntaxTypeIndexNumber('verb') #
        syms.getSyntaxTypeIndexNumber('unkn') #
        syms.getSyntaxTypeIndexNumber('num')  #
        syms.getSyntaxTypeIndexNumber('ssn')  #
        self.syms = syms
