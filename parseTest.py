#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# parseTest.py : 08may2017 CPM
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
import symbolTable

class Kernel(object):
    """ dummy Elly phrase kernel class for testing
    """
    def __init__ ( self ):
        """ initialization
        """
        self.catg = 0
        self.synf = ellyBits.EllyBits(symbolTable.FMAX)
    def __str__ ( self ):
        """ representation of phrase kernel for printing
        """
        return 'phrase catg=' + str(self.catg) + ' ' + self.synf.hexadecimal(False)

class Phrase(object):
    """ dummy Elly phrase class for testing
    """
    def __init__ ( self ):
        """ initialization
        """
        self.krnl = Kernel()
        self.lens = 0
    def __str__ ( self ):
        """ representation of phrase for printing
        """
        return str(self.krnl) + ' lens=' + str(self.lens)

class Tree(object):
    """ dummy Elly tree class for testing
    """
    def __init__ ( self ):
        """ initialization
        """
        print 'tree with stub methods'
        self.queue = [ ]
        self.lastph = None
    def addLiteralPhrase (self,typ,sxs,dvd=False,cap=False):
        """ dummy method
        """
        print 'add phrase: typ=' , typ , '[' + sxs.hexadecimal() + ']'
        ph = Phrase()
        ph.krnl.catg = typ
        ph.krnl.synf = sxs
        self.queue.append(ph)
        self.lastph = ph
        return True
    def addLiteralPhraseWithSemantics (self,typ,sxs,sms,bia,gen=None,dvd=False,cap=False):
        """ dummy method
        """
        print 'add phrase: typ=' , typ , '[' + sxs.hexadecimal() + ']' , '[' + sms.hexadecimal() + '] =' , bia
        ph = Phrase()
        ph.krnl.catg = typ
        ph.krnl.synf = sxs
        ph.krnl.semf = sms
        ph.krnl.bias = bia
        self.queue.append(ph)
        self.lastph = ph
        return True
    def showQueue (self):
        """ dummy method
        """
        print len(self.queue) , 'queued phrase' +  ('s' if len(self.queue) != 1 else '')
        for ph in self.queue:
            print ph

class Context(object):
    """ dummy Elly interpretive context for testing
    """
    def __init__ ( self ):
        """ initialization
        """
        print 'context with empty symbol table'
        syms = symbolTable.SymbolTable()
        syms.getSyntaxTypeIndexNumber('sent') # seed with syntactic types for test
        syms.getSyntaxTypeIndexNumber('end')  #
        syms.getSyntaxTypeIndexNumber('noun') #
        syms.getSyntaxTypeIndexNumber('verb') #
        syms.getSyntaxTypeIndexNumber('unkn') #
        syms.getSyntaxTypeIndexNumber('num')  #
        syms.getSyntaxTypeIndexNumber('ssn')  #
        self.syms  = syms
        self.wghtg = Weighting()

class Weighting(object):
    """ dummy elly conceptual weighting
    """
    def __init__ ( self ):
        """ initialization
        """
        self.cxc = None
    def relateConceptPair ( self , cna , cnb ):
        """ dummy method
        """
        self.cxc = cna + cnb
        return 0
