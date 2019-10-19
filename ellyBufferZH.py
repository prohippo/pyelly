#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBufferZH.py : 15oct2019 CPM
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
framework for simple Chinese tokenization
"""

import sys
import ellyBuffer
import ellyChar
import ellyToken
import ellyStemmer
import ellyException
import ellyConfiguration

class EllyBufferZH(ellyBuffer.EllyBuffer):

    """
    input text buffer with methods for getting successive tokens

    attributes:
    """

    def __init__ ( self ):

        """
        constructor to set up buffer

        arguments:
            self  -
        """

#       print 'init' , super(EllyBufferZH,self)
        super(EllyBufferZH,self).__init__()

    def normalize ( self , s ):

        """
        overrides method in parent class to convert all letters to _
        and to eliminate any white space

        arguments:
            self -
            s    - Unicode string or char list to operate on
        returns:
            normalized sequence
        """

#       print 'ZH normalize'
        n = len(s)
        ns = [ ]
        for i in range(n):
            x = s[i]
#           print '     x=' , x
            if ellyChar.isLetter(x):
                x = '_'
            elif ellyChar.isWhiteSpace(x):
                continue
#           print 'norm x=' , x
            ns.append(x)
#       print 'norm=' , ns
        return ns

    def getNext ( self ):

        """
        get single Chinese character

        arguments:
            self

        returns:
            a token or None if buffer is empty

        exceptions:
            StemmingError
        """

#       print super(EllyBufferZH,self) , 'ZH getNext'
        ln = len(self.buffer)
        if ln == 0:
            return None

#       print 'buffer=' , self.buffer
        n = 1
        if ellyChar.isDigit(self.buffer[0]):
            while n < ln and ellyChar.isDigit(self.buffer[n]):
                n += 1

        w = ellyToken.EllyToken(self.extract(n))
#       print 'return token=' , w
#       print 'ZH extracted'
#       print 'buffer=' , self.buffer
        return w

#
# unit test
#

if __name__ == "__main__":

    buf = EllyBufferZH()
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
        except ellyException.StemmingError:
            print >> sys.stderr , 'stemming error'
            continue
        print "------------"
    sys.stdout.write("\n")
