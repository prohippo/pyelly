#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PyElly - scripting tool for analyzing natural language
#
# ellyCharInputStream.py : 08oct2013 CPM
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
a general text stream with filtering for single-char Elly text input with putback
"""

import sys
import ellyChar
import ellyConfiguration

SP = u' '         # space char
NL = u'\n'        # new line has special significance
CR = u'\r'        # carriage return
UN = ellyChar.Lim # undefined Elly char
END  = u''        # end of input
NBSP = u'\u00A0'  # Unicode no-break space

class EllyCharInputStream(object):

    """
    supports single-char reading of input text with automatic reformatting

    attributes:
        inp    - input utf-8 text stream with readline() method
        buf    - char list as buffer

        _lc    - last raw char seen
        _in    - indentation count for list line
        _eof   - end of file flag
        _prmpt - turn on or off prompting for input
    """

    def __init__ ( self , inp ):

        """
        initialization

        arguments:
            self  -
            inp   - utf-8 char input with readline()
        """

        self.inp = inp
        self.buf = [ ]
        self._lc = UN
        self._in = 0
        self._eof   = False
        self._prmpt = False

#       print 'init inp=' , inp
        if inp == sys.stdin:
            self._prmpt = sys.stdin.isatty()

    def read ( self ):

        """
        get next char from input stream with filtering

        arguments:
            self

        returns:
            single Unicode char on success, null string otherwise
        """

#       print 'reading'

        while True:

            if not self._reload():       # check if buffer empty and reload if needed
                return END               # return EOF if no more chars available

#           print 'buf=' , self.buf

            c = self.buf.pop(0)          # next raw char in buffer

            if not ellyChar.isText(c):   # not ASCII or Latin-1?
#               print 'unknown c=' , ord(c)
                if   c == u'\u2018' or c == u'\u2019': # left or right double quote?
                    c = "'"                            # if so, tramslate
                elif c == u'\u201c' or c == u'\u201d': # left or right single quote?
                    c = '"'                            # if so, translate
                else:
                    c = NBSP             # if so, replace with no-break space

            lc = self._lc                # copy saved last char
#           print 'lc=' , ord(lc)
            self._lc = c                 # set new last char

#           if c == "'":
#               print 'apostrophe' , self.buf

            if not ellyChar.isWhiteSpace(c):
                break
            elif c == CR:                # always ignore
                continue
            elif c == NL:                # special handling of \n
#               print 'got NL'
                nc = self.peek()         # look at next char

                while nc == CR:
                    self.buf.pop(0)      # skip over CR's
                    nc = self.peek()
#               print "lc= '" + lc + "'"
                if lc != NL and nc == NL:
                    self.buf.pop(0)      # special case when NL can be returned
                    break

                if nc == NL:             # NL followed NL?
                    while nc == NL or nc == CR:
                        self.buf.pop(0)  # ignore subsequent new line chars
                        nc = self.peek()
                elif nc == END or ellyChar.isWhiteSpace(nc):
                    continue             # NL followed by space is ignored
                elif nc == u'.' or nc == u'-':
                    pass
                else:
#                   print 'NL to SP, lc=' , ord(lc)
                    c = SP               # convert NL to SP if not before another NL
            else:
#               print 'lc=' , ord(lc) , 'c=' , ord(c)
                c = SP                   # otherwise, convert white space to plain space

            if not ellyChar.isWhiteSpace(lc): # preceding char was not white space?
#               print 'return SP'
                break                    # if so, keep space in stream

        return c                         # next filtered char

    def unread ( self , ch , lc=UN ):

        """
        put a specified char back into input stream

        arguments:
            self  -
            ch    - what to put back
            lc    - how to reset last char
        """

        if ch == END or ch >= UN:
            return
        self.buf.insert(0,ch)
        self._lc = lc

    def peek ( self ):

        """
        look at next input char without removing it from input stream

        arguments:
            self

        returns:
            char on success, END otherwise
        """

#       print 'peek'
        if not self._reload():
#           print 'END'
            return END
        else:
#           print 'peek=' , "'" + self.buf[0] + "'"
            return self.buf[0]

    def skip ( self ):

        """
        remove char from input stream

        arguments:
            self
        """

        if self._reload():
            self.buf.pop(0)

    def getBufferCount ( self ):

        """
        get number of chars in current buffer

        arguments:
            self

        returns:
            char count
        """

        return len(self.buf)

    def indentation ( self ):

        """
        get indentation of last line

        arguments:
            self

        returns:
            indentation count
        """

        return self._in

    def _reload ( self ):

        """
        refill input line buffer and compute indentation

        arguments:
            self

        returns:
            True on success if buffer has at least one char, False otherwise
        """

#       print '_reload'
        if len(self.buf) > 0:
            return True                  # no refilling needed

        if self._eof:
            return False                 # must return immediately on previous EOF

        while len(self.buf) == 0:

#           print 'get more text'

            try:
                if self._prmpt: sys.stdout.write('>> ')
                s = self.inp.readline()  # new text line to add
                if len(s) == 0:
#                   print '**EOF'
                    self._eof = True
                    return False         # EOF
                s = s.decode('utf8')     # to tell Python how to interpret input string
#               print 'raw s=' , s
            except IOError:
                print >> sys.stderr , '** char stream ERROR'
                return False             # treat read failure as empty line

            k = 0
            while k < len(s):            # count leading white space chars
                if s[k] == NL: break     # but stop at end of line
                if not ellyChar.isWhiteSpace(s[k]): break
                k += 1
            self._in = k                 # save indentation level
            s = s[k:]
            self.buf = list(s)           # put unindented text into buffer
#           print 'k=' , k , ', s=' , '"' + s + '"'
#           print self.buf
            if k > 0 and ellyConfiguration.noteIndentation:
                self.buf.insert(0,NL)    # if noted, indentation will break sentence

#           print 'len=' , len(self.buf)
            if len(self.buf) > 0:        # if no usable input, stop
                return True

        return False

#
# unit test
#

if __name__ == '__main__':

    class EllyRawInput(object):
        """
        handle data as if file input
        attributes:
            data - input data
        """
        def __init__ ( self , data ):
            """
            initialization
            arguments:
                self  -
                data  - lists of lists of chars
            """
            self.data = data

        def readline ( self ):
            """
            get one record
            arguments:
                self
            """
            if len(data) > 0:
                return data.pop(0)
            else:
                return [ ]

    data = [
      'abcd\n',
      'éèêë\n',
      'ef gh    ijk   \n',
      'lm	o  	p\n',
      '\n',
      '\n',
      '    \n',
      "qrst",
      "uv's\n",
      'xx\r\n',
      'yy\t\tzz',
      '  wxyz'
    ]

    def hex ( c ):
        return '{:02x}'.format(ord(c))

    if len(sys.argv) == 1:
        inp = EllyRawInput(data)         # test input from list of 'sentences'
    elif sys.argv[1] == '-':
        inp = sys.stdin                  #            from standard input
        print 'reading from sys.stdin'
    else:
        inp = open(sys.argv[1],'r')      #            from text file
    chs = EllyCharInputStream(inp) 
    cs = chs.peek()                      # check peek()
    if cs == END:
        sys.exit(1)
    bf = [ ]
    while True:                          # collect all chars from stream
#       print 'main loop'
        c = chs.read()
        if c == END:
            break
        elif c == '\n':
            bf.append('\\n0a')           # represent \n as string
        else:
            bf.append(c + u' ' + hex(c))
    K = 16                               # how many chars to show per line
    k = 0                                # output char count
    sys.stdout.write('full output=\n')
    for bc in bf:
        sys.stdout.write('<' + bc + '>') # dump all collected stream chars
        k += 1
        if k%K == 0: print ''
    print ''
    print '---------'                    # check unread()
    print 'input start:' , '<' + cs + ' ' + hex(cs) + '>'
    chs.unread('?')
    chs.unread('!')
    c = chs.read()
    d = chs.read()
    print 'checking putback:' , '<' + c + ' ' + hex(c) + '><' + d + ' ' + hex(d) + '>'
