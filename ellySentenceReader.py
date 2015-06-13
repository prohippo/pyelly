#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellySentenceReader.py : 13jun2015 CPM
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
successively extract sentences from buffered text input
"""

import ellyConfiguration
import ellyCharInputStream
import ellyChar
import exoticPunctuation

HT  = u'\t'     # horizontal tab
CR  = u'\r'     # carriage return
NL  = u'\n'     # new line = linefeed
SP  = u' '      # space
END = u''       # EOF indicator is null char

LBs = [ u'(' , u'[' , u'{' ]   # left bracketing
RBs = [ u')' , u']' , u'}' ]   # right
SLs = [ u'\\', u'/' , u'|' ]   # slashes
BRs = LBs + SLs

Stops = [ u'.' , u'!' , u'?' , u':' , u';' ] # should end sentence

QUOs = [ unichr(34) , unichr(39) , # ASCII double and single quote
         u'\u201d'  ,              # right double quote
         u'\u2019'                 # right single quote
       ]

class EllySentenceReader(object):

    """
    to divide input text into separate sentences for processing

    attributes:
        inp  - saved text stream source
        stpx - stop exception matcher
        drop - flag for removing stop punctuation exceptions
        last - last char encountered in buffering input lines
    """

    def __init__ ( self , inpts , stpx , drop=False ):

        """
        initialize sentence buffering of input text

        arguments:
            self  -
            inpts - utf-8 text stream (e.g. sys.stdin)
            stpx  - stop punctuation exceptions
            drop  - what to do with stop punctuation exception
        """

        self.inp = ellyCharInputStream.EllyCharInputStream(inpts)
        self.stpx = stpx
        self.drop = drop
        self.last = END

    def getNext ( self ):

        """
        extract next sentence for Elly translation from input stream

        arguments:
            self

        returns:
            list of chars for next sentence on success, None on empty stream
        """

#       print 'getNext'

        sent = [ ]         # list buffer to fill

        parenstop = False  # initially, parentheses will NOT stop sentence

        c = self.inp.read()
        if c == SP:
            c = self.inp.read()

        if c == END:       # EOF check
            return None

#       print 'c=' , ord(c)
        self.inp.unread(c,SP)
#       print '0  <<" , self.inp.buf

        # fill sentence buffer up to next stop punctuation

        nAN = 0            # alphanumeric count in sentence

        while True:

            x = self.inp.read()     # next input char

            if x == END:            # handle any EOF
                break

#           print 'x=' , '<' + x + '>'
#           print 'sent=' , sent

            # check for table delimiters in text

            if len(sent) == 0:
#               print 'table'
#               print '1  <<' , self.inp.buf

                if x == u'.' or x == u'-':      # look for multiple '.' or '-'
                    while True:                 # scan up to end of current buffering
                        y = self.inp.read()     #
                        if y != x and y != SP:  # no more delimiter chars or spaces?
                            self.inp.unread(y)  # if so, done
                            break               #
                    continue                    # ignore everything seen so far

            #########################################
            # accumulate chars and count alphanumeric
            #########################################

            c = x
            sent.append(c)
            if ellyChar.isLetterOrDigit(c):
                nAN += 1
                continue                        # if alphanumeric, just add to sentence

            if c == SP:
                continue                        # if space, just add to sentence

            # NL will break a sentence

            if c == NL:
                sent.pop()                      # remove from sentence chars
                break

            # char was not alphanumeric or space
            # look for stop punctuation exception

            z = self.inp.peek()  # for context of match call
#           print 'peek z=' , z

#           print '0  <<' , self.inp.buf

#           print 'sent=' , sent[:-1]
#           print 'punc=' , '<' + c + '>'
#           print 'next=' , '<' + z + '>'
            if self.stpx.match(sent[:-1],c,z):
#               print 'exception MATCH'
                if self.drop:
                    sent.pop()   # remove punctuation char from sentence
                continue

#           print '1  <<' , self.inp.buf

#           print 'no exception MATCH'

            # handle any nonstandard punctuation

            exoticPunctuation.normalize(c,self.inp)

#           print '2  <<' , self.inp.buf

            # handle parentheses as possible stop

            if nAN == 0 and self.stpx.inBracketing():
                parenstop = True
            elif parenstop and not self.stpx.inBracketing():
                break            # treat as stop

#           print '3  <<' , self.inp.buf

            # check for dash

            if c == u'-':
                d = self.inp.read()
                if d == u'-':
#                   print 'dash'
                    while True:
                        d = self.inp.read()
                        if d != u'-': break
                    sent.append(c)
                self.inp.unread(d)
                continue

            # check for sentence break on punctuation

            if not c in Stops:
                continue

            else:
#               print 'stopping possible!'
                d = self.inp.read()
#               print '4  <<' , self.inp.buf

                if d == None: d = u'!!'
#               print 'stop=' , '<' + c + '> <' + d + '>'

#               print 'ellipsis check'
                if c == u'.' and c == d:
                    if self.inp.peek() != c:
                        self.inp.unread(c)
                    else:
                        self.inp.skip() # drop last char from input
                        sent.append(d)  # finish ellipsis in sentence buffer
                        sent.append(d)  #
                        sent.append('!')
                    continue

                # special check for multiple stops

#               print 'Stops d=' , d , ord(d) if d != '' else 'NONE'
                if d in Stops:
                    while True:
                        d = self.inp.read()
                        if d in Stops: break
                    self.inp.unread(d)
                    if not ellyChar.isWhiteSpace(d):
                        d = u' '

                # break sentence except when in parentheses

                elif d in RBs:
#                   print 'followed by' , '<' + d + '>'
                    if not self.stpx.inBracketing():
                        break
                    else:
                        if self.drop:
                            sent.pop()
                        self.inp.unread(d)
                        continue

                # special check for single or double quotes, which should
                # be included with current sentence after stop punctuation

                elif d in QUOs:
#                   print 'QUO d=' , d , ord(d)
                    x = self.inp.peek()
                    if x == END or ellyChar.isWhiteSpace(x):
                        sent.append(d)
                        break
                    else:
                        self.inp.unread(SP)
                        continue

                # special check for blank or null after stops

                elif d != END and not ellyChar.isWhiteSpace(d):
                    sent.append(d)
                    continue

                # if no match for lookahead, put back

                elif d != '':
#                   print 'unread d=' , d
                    self.inp.unread(d)

                # final check: is sentence long enough?

#               print '5  <<' , self.inp.buf
                cx = self.inp.peek()
                if cx == None: cx = u'!!'
#               print 'sentence break: next=' , '<' + cx + '>' , len(cx) , sent
                if nAN > 1:
                    break

        if len(sent) > 0 or self.last != END:
            return sent
        else:
            return None

#
# unit test
#

if __name__ == '__main__':

    import sys
    import ellyDefinitionReader
    import stopExceptions

    base = ellyConfiguration.baseSource
    dfs = base + (sys.argv[2] if len(sys.argv) > 2 else 'default') + '.sx.elly'
    print 'exception file:' , dfs
    inp = ellyDefinitionReader.EllyDefinitionReader(dfs)
    if inp.error != None:
        print >> sys.stderr, 'cannot read stop exceptions'
        print >> sys.stderr, inp.error
        sys.exit(1)

    stpxs = stopExceptions.StopExceptions(inp)

    tst = sys.argv[1] if len(sys.argv) > 1 else 'sentenceTestData.txt'
    ins = open(tst,'r')
    rdr = EllySentenceReader(ins,stpxs)

    while True:
        sents = rdr.getNext()
        if sents == None or len(sents) == 0: break
        s = u''.join(sents)
        print '\n>>>>' , '[' + s + ']'

    ins.close()
