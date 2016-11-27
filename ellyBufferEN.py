#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBufferEN.py : 25nov2016 CPM
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

import sys
import ellyBuffer
import ellyChar
import ellyStemmer
import ellyException
import ellyConfiguration
import inflectionStemmerEN

APO = ellyChar.APO                # literal ASCII apostrophe
APX = u'\u2019'                   # formatted Unicode apostrophe
ESS = u's'                        # literal S
SFX = '-' + APO + ESS             # -'S suffix

class EllyBufferEN(ellyBuffer.EllyBuffer):

    """
    input text buffer with methods for getting successive tokens

    attributes:
        stemmer - inflectional stemmer
        divided - saved flag for next token
    """

    def __init__ ( self ):

        """
        constructor to set up buffer

        arguments:
            self  -
        """

#       print 'init' , super(EllyBufferEN,self)
        super(EllyBufferEN,self).__init__()
        if ellyConfiguration.inflectionalStemming:  # English inflectional stemmer?
            try:                                    # of so, try to load
                self.stemmer = inflectionStemmerEN.InflectionStemmerEN()
            except ellyException.TableFailure:
                self.stemmer = ellyStemmer.EllyStemmer()  # null stemmer
                print >> sys.stderr , 'stemmer failure'
        else:
            self.stemmer = ellyStemmer.EllyStemmer()      # null stemmer
        self.divided = False

    def getNext ( self ):

        """
        override EllyBuffer method to get next token from buffer
        with automatic inflectional stemming

        arguments:
            self

        returns:
            a token or None if buffer is empty

        exceptions:
            StemmingError
        """

#       print super(EllyBufferEN,self) , 'getNext'
        w = super(EllyBufferEN,self).getNext() # use getNext() without inflectional stemmer
        if w == None: return None
#       print 'got unstemmed:' , w , 'divided=' , self.divided
        if self.divided:
            w.dvdd = True
            self.divided = False
        if not w.isSplit():                    # check for stemming
            self.divide(w)                     # if not, do inflectional stemming
#       print 'return token=' , w
        return w

    def putSuffixBack ( self , suffix ):

        """
        return suffix to input buffer

        arguments:
            self   -
            suffix - as a string
        """

#       print 'put back' , suffix
        if self.atToken(): self.prepend(ellyChar.SPC)
        self.prepend(suffix)

    def divide ( self , word ):

        """
        apply inflectional analysis, including for -'s and -s'

        arguments:
            self  -
            word  - ellyToken

        exceptions:
            StemmingError
        """

#       print "divide" , word
        wl = word.getLength()       # if so, is word long enought to be divided
        if wl < 3:
            return                  # if not, done

        if word.isAffix():          # if term is already product of division, stop
            return

#       print 'word suffixes=' , word.sufs , word.dvdd

        x = word.charAt(wl-1)       # get last two chars of word
        y = word.charAt(wl-2)
#       print 'word= ...' , y , x

        if   x == ESS and (
             y == APO or y == APX   # check for -'S
        ):
#           print "-'s ending"
            word.shortenBy(2)
            self.putSuffixBack(SFX)
#           print 'word=' , word , 'without -\'S'
            return

        elif y == ESS and (
             x == APO or x == APX   # check for implied -'S
        ):
#           print "-s' ending"
            word.shortenBy(1)
            self.putSuffixBack(SFX)
#           print 'word=' , word , 'without -\''
            return

        if ellyChar.isLetter(word.charAt(0)):
#           print 'apply stemmer'
            self.stemmer.apply(word)  # apply any inflectional stemmer
#           print 'word= ' , word
            if word.isSplit():
#               print 'is split'
                sufs = word.getSuffixes()
#               print 'pres=' , word.getPrefixes()
#               print 'sufs=' , sufs
                while len(sufs) > 0:
                    self.putSuffixBack(sufs.pop())

#
# unit test
#

if __name__ == "__main__":

    buf = EllyBufferEN()
    print 'enter text lines to get tokens from'
    while True:
        try:
            sys.stdout.write("> ")
            l = sys.stdin.readline().decode('utf8')
        except KeyboardInterrupt:
            break
        l = l.strip()
        if len(l) == 0: break
        buf.clear()
        buf.append(list(l))
        print buf.buffer
        try:
            while True:
                print "len=" , len(buf.buffer)
                t = buf.getNext()
                if t == None: break
                print ">>>> " , unicode(t)
                print ">>>> " , t.pres , t.sufs
        except ellyException.StemmingError:
            print >> sys.stderr , 'stemming error'
            continue
        print "------------"
    sys.stdout.write("\n")
