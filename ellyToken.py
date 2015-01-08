#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyToken.py : 07jan2015 CPM
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
encapsulation of a token string and results of its analysis
"""

import unicodedata

class EllyToken:

    """
    lexical token for morphological analysis
        
    attributes:
        orig - original word
        root - root from analysis
        pres - prefix list
        sufs - suffix list
        capn - capitalization flag
    """

    def __init__ ( self , x=None ):

        """
        construct token from string

        arguments:
            self  -
            x     - Unicode input string
        """

        if x != None:
            self.set(x)
        else:
            self.set()

    def __unicode__ ( self ):

        """
        how to show token for debugging

        arguments:
            self

        returns:
            Unicode string representation
        """

        p =  '[' + u' '.join(self.pres) + ']+' if len(self.pres) > 0 else ''
        s = '-[' + u' '.join(self.sufs) + ']'  if len(self.sufs) > 0 else ''
        return u'EllyToken: ' + p + str(self.root) + s + u' (orig= ' + self.orig + u')'

    def __str__ ( self ):

        """
        ASCII string representation

        arguments:
            self

        returns:
            string representation
        """

        return unicodedata.normalize('NFKD',unicode(self)).encode('ascii','ignore')

    def set ( self , x='' ):

        """
        set token to specified string

        arguments:
            self  -
            x     - Unicode input string or list
        """

        if not isinstance(x,basestring):
            x = u''.join(x)
        if len(x) > 0:
            self.capn = x[0].isupper()
        else:
            self.capn = False
        self.orig = x
        self.pres = [ ]
        self.sufs = [ ]
        self.root = list(x.lower())

    def store ( self , s ):

        """
        store sequence in token

        arguments:
            self  -
            s     - sequence of Unicode chars
        """

        self.set(u''.join(s))

    def getOrig ( self ):

        """
        get original token string

        arguments:
            self
        returns:
            Unicode string
        """

        return self.orig
    
    def getRoot ( self ):

        """
        get root for token

        arguments:
            self
        returns:
            list of chars
        """

        return self.root

    def getPrefixes ( self ):

        """
        get merged suffixes for token

        arguments:
            self
        returns:
            list of strings
        """

        return self.pres

    def getSuffixes ( self ):

        """
        get merged suffixes for token

        arguments:
            self
        returns:
            list of strings
        """

        return self.sufs

    def chopPrefix ( self , n ):

        """
        add prefix to list for token

        arguments:
            self
            n     - length of prefix
        """

        if n > len(self.root):
            x = u''.join(self.root[:n])
            self.root = self.root[n:]
            self.pres.append(x)

    def chopSuffix (self , n ):

        """
        add suffix to list for token

        arguments:
            self
            n     - length of suffix
        """

        if n > len(self.root):
            x = u''.join(self.root[-n:])
            self.root = self.root[:-n]
            self.sufs.insert(0,x)

    def addSuffix ( self , x ):

        """
        add suffix to list for token

        arguments:
            self
            x     - suffix string
        """

        self.sufs.insert(0,x)

    def addPrefix ( self , x ):

        """
        add prefix to list for token

        arguments:
            self
            x     - prefix string
        """

        self.pres.append(x)

    def getLength ( self ):

        """
        get char count in token less suffixes

        arguments:
            self

        returns:
            length
        """

        return len(self.root)

    def shortenBy ( self , n , both=False ):

        """
        drop chars from token

        arguments:
            self  -
            n     - char count
            both  - shorten both root and orig
        """

        m = len(self.root)
        if both and m != len(self.orig):
            return
        if m < n:
            return
        nm = m - n
        self.root = self.root[:nm]
        if both:
            self.orig = self.orig[:nm]

    def isSplit ( self ):

        """
        check if suffixes have been removed from token

        arguments:
            self

        returns:
            True if suffixes removed, otherwise False
        """

        return (len(self.sufs) > 0 or len(self.pres) > 0)

    def isAffix ( self ):

        """
        check if token is itself an affix

        arguments:
            self

        returns:
            True if affix, False otherwise
        """

        return self.root[0] == '-' or self.root[-1] == '+'

    def charAt ( self , n ):

        """
        get nth character in token

        arguments:
            self  -
            n     - index of character in token

        returns:
            indexed character
        """

        if n >= len(self.root): return ''

        return self.root[n]

    def toString ( self ):

        """
        get ASCII string representation of token root

        arguments:
            self

        returns:
            ASCII token string
        """

        return self.toUnicode().encode('ascii','ignore').lower()

    def toUnicode ( self ):

        """
        get Unicode string representation of token root

        arguments:
            self

        returns:
            Unicode token string
        """

        return unicodedata.normalize('NFKD',u''.join(self.root))

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        ux = u'Taxed'
    else:
        ux = sys.argv[1]
        print len(ux) , type(ux) , ux
        if type(ux) != 'unicode':
            ux = ux.decode('utf8')
        print type(ux)

    t = EllyToken(ux)

    t.addSuffix(u'xxx')
    t.addSuffix(u'yy')
    t.addSuffix(u'z')

    print 1 , t
    print "capn=", t.capn
    print "suffixes=" , map(lambda x: '-'+x , t.getSuffixes())

    t.shortenBy(1,both=True)

    print 2 , t

    t.shortenBy(1)

    print 3 , t

    print type(t.orig) , type(t.root)

    print 'ascii=  ' , str(t)
    print 'unicode=' , unicode(t)
