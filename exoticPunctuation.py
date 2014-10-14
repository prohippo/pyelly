#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# exoticPunctuation.py : 05jun2013 CPM
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
ad hoc methods for nonstandard punctuation in
just a few of the many imaginable permutations
"""

base  = u'!?#*@$%'  # elements of nonstandard punctuation
space = u' '        # literal space

def recognized ( char ):

        """
        check whether punctuation is covered by this class

        arguments:
            char  - candidate punctuation

        returns:
            True if recognized, False otherwise
        """
    
        return (base.find(char) >= 0)

def normalize ( char , inp ):

    """
    convert various kinds of unorthodox punctuation to single char

    arguments:
        char  - next char to process
        inp   - EllyCharInputStream

    returns:
        True if any conversion done, False otherwise
    """
    
    if not recognized(char):
        return False

    spaced = False  # have seen a space possibly to put back
    status = False  # if any chars have been dropped

    while True:
        d = inp.read()      # get next char
        if d == '':         # quit on end of input
            break
        elif d == space:    # note space, but do nothing yet
            spaced = True
        elif recognized(d): # part of unorthodox punctuation?
            status = True   # if so, ignore
            spaced = False
        else:
            inp.unread(d)   # otherwise, put char back
            break

    if spaced:
        inp.unread(space)

    return status
