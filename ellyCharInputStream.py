#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PyElly - scripting tool for analyzing natural language
#
# ellyCharInputStream.py: 17jul2018 CPM
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
HYPH = u'-'       # hyphen
SHYP = u'\u00AD'  # soft hyphen
DASH = u'\u2013'  # n-dash
NBSP = u'\u00A0'  # Unicode no-break space
ELLP = u'\u2026'  # Unicode horizontal ellipsis

RSQm = ellyChar.RSQm
RDQm = ellyChar.RDQm

PLM = 3           # maximum char count for preview
NLM = 80          # limit of look-ahead

def spc ( c ):

    """
    special space check
    arguments:
        c  - single char
    returns:
        True if white space or null, False otherwise
    """
    return c == '' or ellyChar.isWhiteSpace(c)

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
        _cap   - capitalization flag
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
        self._cap   = False

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

#       print 'reading: buf=' , self.buf

        while True:

            if not self._reload():       # check if buffer empty and reload if needed
                return END               # return EOF if no more chars available

#           print 'buf=' , self.buf

            c = self.buf.pop(0)          # next raw char in buffer

            if c == SHYP:                # ignore soft hyphen
                if len(self.buf) > 0:
                    if self.buf[0] == SP:
                        c = self.buf.pop(0)
                continue

            if not ellyChar.isText(c):   # unrecognizable Elly char?
#               print 'c=' , '{0:04x}'.format(ord(c))
                if ellyChar.isCJK(c):
                    c = '_'              # special handling for Chinese
                else:
#                   print 'replace' , c , 'with NBSP'
                    c = NBSP             # by default, replace with no-break space

            lc = self._lc                # copy saved last char
#           print 'lc=' , ord(lc)
            self._lc = c                 # set new last char

#           if c == "'":
#               print 'apostrophe' , self.buf

#           print 'c=' , '<' + c + '>'

            if c == HYPH:                # special treatment for isolated hyphens
                if spc(lc) and spc(self.peek()):
                    c = DASH
                break
            elif c == '.':               # check for ellipsis
                bb = self.buf
                bl = len(bb)
#               print 'bl=' , bl , 'bb=' , bb
                if bl >= 2 and bb[0] == '.' and bb[1] == '.':
                    self.buf = bb[2:]
                    c = ELLP
                elif bl >= 4 and bb[0] == ' ' and bb[1] == '.' and bb[2] == ' ' and bb[3] == '.':
                    self.buf = bb[4:]
                    c = ELLP
                break
            elif c == RSQm:              # check for single quote
#               print 'at single quote'
                nc = self.peek()         # look at next char
#               print 'next=' , nc
                if nc == RSQm:           # doubling of single quote?
                    self.buf.pop(0)      # if so, combine two single quotes
                    c = RDQm             # into one double quote
            elif not ellyChar.isWhiteSpace(c):
                if ellyChar.isWhiteSpace(lc):
                    self._cap = ellyChar.isUpperCaseLetter(c)
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

            self._cap = False

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

        if ch == END:
            return
        self.buf.insert(0,ch)
        self._lc = lc

    def preview ( self ):

        """
       get list of up to the next three chars in input

        arguments:
            self

        returns:
            list char chars, possibly empty
        """

        if not self._reload():
            return [ ]
        bk = len(self.buf)
        if bk > PLM: bk = PLM
        return self.buf[:bk]

    def peek ( self ):

        """
        look at next raw input char without removing it from input stream

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

    def getBufferCharCount ( self ):

        """
        get number of chars in current buffer

        arguments:
            self

        returns:
            char count
        """

        return len(self.buf)

    def findClose ( self , opn , cls ):

        """
        look ahead for closing bracket in input stream buffer

        arguments:
            self  -
            opn   - opening bracket
            cls   - closing bracket to look for

        returns:
            offset in stream if found, -1 otherwise
        """

        skp = 0    # skip count
        nos = 0    # offset in buffer
        nlm = len(self.buf)
        if nlm > NLM: nlm = NLM  # set lookahead limit
        while nos < nlm:
            if   self.buf[nos] == opn:  # another opening bracket means
                skp += 1                # to skip a closing one
            elif self.buf[nos] == cls:
                if skp > 0:             # check for skip
                    skp -= 1
                elif nos + 1 == nlm or ellyChar.isWhiteSpace(self.buf[nos+1]):
                    return nos          # offset for closure
            nos += 1
        return -1

    def indentation ( self ):

        """
        get indentation of last line

        arguments:
            self

        returns:
            indentation count
        """

        return self._in

    def capitalization ( self ):

        """
        get capitalization

        arguments:
            self

        returns:
            capitalization flag
        """

        return self._cap

    def _reload ( self ):

        """
        refill input line buffer and compute indentation

        arguments:
            self

        returns:
            True on success if buffer has at least one char, False otherwise
        """

#       print '_reload'
        bex = ''                         # save space char at end of buffer
        bcn = len(self.buf)
        if bcn > 1:
            return True                  # no refilling needed
        elif bcn == 1:
            if ellyChar.isWhiteSpace(self.buf[0]):
                bex = self.buf[0]        # special case when only space char left
                self.buf = [ ]           # refill to get chars after that space
            else:
                return True              # no refilling yet

        if self._eof:
            return False                 # must return immediately on previous EOF

        while len(self.buf) == 0:

#           print 'get more text'

            try:                         # read in UTF8 line from input stream
                if self._prmpt: sys.stdout.write('>> ')
                s = self.inp.readline()  # new text line to add
#               print 's=' , s
                if len(s) == 0:
#                   print '**EOF'
                    self._eof = True
                    return False         # EOF
                s = s.decode('utf8')     # convert UTF8 to Unicode string
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
            if len(self.buf) > 0:        # if usable input, stop filling
                if bex != '':            # but restore any saved space char from buffer
                    self.buf.insert(0,bex)
                return True

        return False                     # cannot refill, ignore trailing space char

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
            if len(self.data) > 0:
                return self.data.pop(0)
            else:
                return [ ]

    datd = [  # test input text as UTF-8!
        'abcd\n',
        'éèêë\n',
        'ef gh    ijk   \n',
        'lm	o  	p\n',
        '\n',
        '\n',
        '    \n',
        '“gene”',
        "qrst",
        "uv's\n",
        'xx\r\n',
        'yy\t\tzz',
        '  wxyz',
        ' - ' ,
        '桂林' ,
        '(1. ) x\n' ,
        'run' ,
        ''.join([chr(0xc2) , chr(0xad)]) ,
        '\nning\n' ,
        'X . . . Y\n' ,
        'Aaa' ,
        'B♭ maj' ,
        '’’ '
    ]

    def hexd ( c ):
        """ simple hexadecimal conversion
        """
        return '{:04x}'.format(ord(c))

####

    if len(sys.argv) == 1:                # no input file for testing?
        inpu = EllyRawInput(datd)         # if so, use test input defined above
        print 'reading from data array'
    elif sys.argv[1] == '-':
        inpu = sys.stdin                  #            from standard input
        print 'reading from sys.stdin'
    else:
        inpu = open(sys.argv[1],'r')      #            from text file
        print 'reading from file:' , sys.argv[1]
    chs = EllyCharInputStream(inpu)
    print 'preview=' , chs.preview()
    cs = chs.peek()                       # check peek()
    if cs == END:
        sys.exit(1)
    bf = [ ]
    while True:                           # collect each char from stream
#       print 'main loop'
        chu = chs.read()
        if chu == END:
            break
        elif chu == '\n':
            bf.append('\\n 000a')         # represent \n as string
            print 'buffer char count after reading <\\n>=' , chs.getBufferCharCount() ,
            print 'output=' , len(bf)
        else:
            bf.append(u'{:3s}'.format(chu) + hexd(chu))
    Kn = 10                               # how many chars to show per line
    kn = 0                                # output char count
    sys.stdout.write('full output is\n')
    for bc in bf:
        sys.stdout.write('<' + bc + '> ') # dump all collected stream chars
        kn += 1
        if kn%Kn == 0: sys.stdout.write('\n')
    print ''
    print 'capitalization=' , chs.capitalization()
    print ''
    print '---------'                     # check unread()
    print 'input start:' , '<' + cs + ' ' + hexd(cs) + '>'
    chs.unread(')')
    chs.unread(')')
    chs.unread('(')
    chs.unread('?')
    chs.unread('!')
    print 'lookahead: found ) at' , chs.findClose('(',')')
    cu = chs.read()
    du = chs.read()
    print 'checking putback:' , '<' + cu + ' ' + hexd(cu) + '>' ,
    print                       '<' + du + ' ' + hexd(du) + '>'
