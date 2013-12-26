#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# definitionLine.py : 07apr2013 CPM
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
parsing support for Elly table definition X->A B C D...
"""

spc = u' '  # space char
lbr = u'['  # left  bracket
rbr = u']'  # right

def normalize ( str ):

    """
    drop extra spaces in line

    arguments:
        str   - string string

    returns:
        input without extra spaces
    """

    s = [ spc ]               # start with a space for context

    f = False                 # in-brackets flag

    k = 0
    ln = len(str)
    while k < ln:             # check each input char in succession
        c = str[k]            # 
        k += 1
        if c == spc:
            if f or s[-1] == spc:
                continue      # keep only single spaces and only outside of [ ]
        elif c == lbr:
            f = True
            if s[-1] == spc:
                s.pop()       # a space preceding a left bracket is dropped
        elif c == rbr:
            f = False
        s.append(c)

    return u''.join(s).strip() # trimmed string

class DefinitionLine(object):

    """
    line object with built-in parsing

    attributes:
        left  - part left  of -> or <- (treated as single component)
        tail  - part right of -> or <-
    """

    def __init__ ( self , line ):

        """
        initialize from input string

        arguments:
            self  -
            line  - input string
        """

        self.left = None    # default
        self.tail = None    #

        if line == None or len(line) == 0:
            return

        k = line.find('->') # split on '->'
        if k < 0:
            k = line.find('<-') # split on '<-'
            if k < 0:
                return

#       print "k=" , k , "in" , len(line)
        self.left = normalize(line[:k])   # store splitoff substrings
        self.tail = normalize(line[k+2:]) #

    def nextInTail ( self ):

        """
        extract part of tail up to next separator space

        arguments:
            self

        returns
            substring up to space
        """

        if len(self.tail) == 0:
            return None
        k = self.tail.find(spc)         # find end of next tail element
        if k < 0:
            t = self.tail               # if none, take the entire tail
            self.tail = ''              #
        else:
            t = self.tail[:k]           # take tail up to next space
            self.tail = self.tail[k+1:] #
        return t

    def isEmptyTail ( self ) :

        """
        check if tail of definition is empty

        arguments:
            self

        returns:
            True if so, False otherwise
        """

        return (self.tail == None or len(self.tail) == 0)

    def isEmptyLeft ( self ):

        """
        check if left of definition is empty

        arguments:
            self

        returns:
            True if so, False otherwise
        """

        return (self.left == None or len(self.left) == 0)
