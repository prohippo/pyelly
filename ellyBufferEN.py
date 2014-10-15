#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBufferEN.py : 14oct2014 CPM
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
framework for integrating English inflectional stemming into basic tokenization
"""

import ellyBuffer
import ellyChar
import ellyStemmer
import ellyException
import ellyConfiguration
import inflectionStemmerEN

APO = ellyChar.APO                # literal apostrophe
ESS = u's'                        # literal S
MIN = u'-'                        # hyphen

class EllyBufferEN(ellyBuffer.EllyBuffer):

    """
    input text buffer with methods for getting successive tokens
 
    attributes:
        stemmer - inflectional stemmer
    """

    def __init__ ( self ):

        """
        constructor to set up buffer

        arguments:
            self  -
        """

        super(EllyBufferEN,self).__init__()
        if ellyConfiguration.inflectionalStemming:  # English inflectional stemmer?
            try:                                    # of so, try to load
                self.stemmer = inflectionStemmerEN.InflectionStemmerEN()
            except ellyException.TableFailure:
                self.stemmer = ellyStemmer()        # null stemmer
        else:
            self.stemmer = ellyStemmer()            # null stemmer

    def getNext ( self ):

        """
        get next token from buffer and automatically apply inflectional stemming
        overriding EllyBuffer method

        arguments:
            self

        returns:
            a token or None if buffer is empty

        exceptions:
            RealtimeError on stemming error
        """

        w = super(EllyBufferEN,self).getNext() # use getNext() without inflectional stemmer
        if w == None: return None
        if not w.isSplit():                    # check for stemming
            self.divide(w)                     # if not, do inflectional stemming
        return w

    def divide ( self , word ):

        """
        apply inflectional analysis, including for -'s and -'

        arguments:
            self  -
            word  - ellyToken

        except RealtimeError:
            RealtimeError on stemming error
        """

#       print "divide",word.root
        wl = word.getLength()       # if so, is word long enought to be divided
        if wl < 3:
            return                  # if not, done

        if word.isAffix():          # if term is already product of division, stop
            return

        x = word.charAt(wl-1)       # get last two chars of word
        y = word.charAt(wl-2)
#       print 'ending:' , y , x

        if x == u's' and y == APO:  # check for -S'
            word.addSuffix(APO+ESS)
            word.shortenBy(2)
#           print 'word=' , word
            return

        elif x == APO and y == ESS: # check for implied -'S
            word.addSuffix(APO+ESS)
            word.shortenBy(1)
#           print 'word=' , word
            return

        if ellyChar.isLetter(word.charAt(0)):
            self.stemmer.apply(word)  # apply any stemmer
            if word.isSplit():
                sufs = word.getSuffixes()
                while len(sufs) > 0:
                    if self.atToken(): self.prepend(ellyChar.SPC)
                    self.prepend(MIN + sufs.pop())

#
# unit test
#

if __name__ == "__main__":

    import sys

    buf = EllyBufferEN()
    while True:
        try:
            sys.stdout.write("> ")
            l = sys.stdin.readline()
        except KeyboardInterrupt:
            break
        l = l.strip()
        if len(l) == 0: break
        buf.clear()
        buf.append(list(l))
        print buf.buffer
        while True:
            print "len=" , len(buf.buffer)
            t = buf.getNext()
            if t == None: break
            print ">>>> 0=" , t
        print "------------"
    sys.stdout.write("\n")
