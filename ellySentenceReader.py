#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellySentenceReader.py : 26mar2017 CPM
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

LSQm = ellyChar.LSQm
RSQm = ellyChar.RSQm
LDQm = ellyChar.LDQm
RDQm = ellyChar.RDQm

SQuo = "'"
DQuo = '"'

RBs   = [ u')' , u']' , u'}' ]               # right bracketing

Stops = [ u'.' , u'!' , u'?' , u':' , u';' ] # should end sentence

QUOs = [ unichr(34) , unichr(39) , # ASCII double and single quote
         RDQm ,                    # right Unicode double quote
         RSQm                      # right Unicode single quote
       ]

LS   = 4                           # limit on special bracketing lookahead

class EllySentenceReader(object):

    """
    to divide input text into separate sentences for processing

    attributes:
        inp  - saved text stream source
        stpx - stop exception matcher
        drop - flag for removing stop punctuation exceptions
        last - last char encountered in buffering input lines

        _cr - complementary brackets
        _cl - bracketing level
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

        self._cr = { u'(' : u')' , u'[' : u']' , LDQm : RDQm , LSQm : RSQm , '{' : '}' }
        self._cl = { u')' : 0 , u']' : 0 , RDQm : 0 , RSQm : 0 , '}' : 0 }

    def checkBracketing ( self , c ):

        """
        check for bracketing within sentence being accumulated

        arguments:
            self  -
            c     - bracketing char to take account of

        returns:
            True if c is bracketed, False otherwise
        """

#       print 'check c=<' , c , '>'
        if c in self._cr:            # check for known bracketing
            cr = self._cr[c]         # get complementary bracket
#           print 'c=' , c , 'cr=' , cr
            if self._cl[cr] == 0:    # check if no prior brackets
                if self.inp.findClose(c,cr):
                    self._cl[cr] = 1 # note brackets only if short range
            else:
                self._cl[cr] += 1    # just increase bracketing level
        elif c in self._cl and self._cl[c] > 0:
            self._cl[c] -= 1         # decrease bracketing level

        return self._cl[')'] + self._cl[']'] + self._cl[RDQm] + self._cl['}'] > 0


    def resetBracketing ( self ):

        """
        reset bracketing levels

        arguments:
            self
        """

        self._cl[')']  = 0
        self._cl[']']  = 0
        self._cl['}']  = 0
        self._cl[RDQm] = 0

    def shortBracketing ( self , sent , d ):

        """
        look for short bracketed segment

        arguments:
            self  -
            sent  - accumulated sentence
            d     - next char

        returns:
            True if bracketed segment found, False otherwise
        """

        if d in [ '[' , '(' ]:
            sg = [ ]
            ls = 0
            while ls < LS:
                nd = self.inp.read()
                if nd in [ ']' , ')' ]: break
                sg.append(nd)
                ls += 1
            if ls < LS:
                sent.append(d)
                sent.extend(sg)
                sent.append(nd)
                return True
            return False

    def getNext ( self ):

        """
        extract next sentence for Elly translation from input stream

        arguments:
            self

        returns:
            list of chars for next sentence on success, None on empty stream
        """

#       print 'getNext'

        self.resetBracketing()
        inBrkt = False

        nspc = 0           # set space count

        sent = [ ]         # list buffer to fill

        x  = self.inp.read()
        if x == SP:
            x = self.inp.read()

        if x == END:       # EOF check
            return None

        c  = END           # reset
        lc = END

#       print 'x=' , '<' + x + '>' , ord(x)
        self.inp.unread(x,SP)       # put first char back to restore input
#       print '0  <<" , self.inp.buf

        # fill sentence buffer up to next stop punctuation in input

        nAN = 0                     # alphanumeric count in sentence

        while True:

            x = self.inp.read()     # next input char

            if x == END:            # handle any EOF
                break

#           print 'x=' , '<' + x + '>' , 'c=' , '<' + c + '>'
#           print 'sent=' , sent , 'nspc=' , nspc

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

            ####################################################
            # accumulate chars and count alphanumeric and spaces
            ####################################################

            lc = c
            c  = x
            nc = self.inp.peek()
            if ellyChar.isWhiteSpace(nc): nc = SP

#           print 'lc=' , '<' + lc + '>, nc=' , '<' + nc + '>'
            if lc == SP or lc == END: # normalize chars for proper bracketing
                if x == SQuo:         #
                    x = LSQm          # a SQuo preceded by a space becomes LSQm
                elif x == DQuo:       #
                    x = LDQm          # a DQuo preceded by a space becomes LDQm
            if nc == SP or nc == END: #
                if x == SQuo:         # a SQuo followed by a space becomes RSQm
                    x = RSQm          #
                elif x == DQuo:       # a DQuo followed by a space becomes RDQm
                    x = RDQm          #
            elif not ellyChar.isLetterOrDigit(nc):
                if x == SQuo:         # a SQuo followed by nonalphanumeric becomes RSQm
                    x = RSQm          #
                elif x == DQuo:       # a DQuo followed by nonalphanumeric becomes RDQm
                    x = RDQm          #
            elif ellyChar.isWhiteSpace(c) and inBrkt:
                nspc += 1

            svBrkt = inBrkt
            inBrkt = self.checkBracketing(x)    # do bracket checking with modified chars
            if svBrkt and not inBrkt: nspc = 0

#           print 'lc=' , '<' + lc + '>' , 'bracketing x=' , '<' + x + '>' , inBrkt

            sent.append(c)                      # but buffer original chars
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

            cx = self.inp.preview()  # for context of match call

#           print '0  <<' , self.inp.buf

#           print 'sent=' , sent[:-1]
#           print 'punc=' , '<' + c + '>'
#           print 'next=' , cx
            if c in Stops and self.stpx.match(sent[:-1],c,cx):
#               print 'stop exception MATCH'
                if self.drop:
                    sent.pop()   # remove punctuation char from sentence
                    lc = SP
                continue

#           print 'no stop exception MATCH for' , c

#           print '@1  <<' , self.inp.buf

            # handle any nonstandard punctuation

            exoticPunctuation.normalize(c,self.inp)

#           print '@2  <<' , self.inp.buf

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

#           print '@3  c=' , c

            if c in QUOs or c in RBs:

                # special check for single or double quotes or
                # bracketing, which can immediately follow stop
                # punctuation for current sentence

#               print 'bracketing c=' , c , ord(c) , inBrkt , 'at' , len(sent)

                if not inBrkt:
#                   print sent , 'so far'
                    z = self.inp.read()
                    if self.shortBracketing(sent,z):
                        break
                    self.inp.unread(z)
#                   print 'z=' , '[' + z + ']' , 'lc=' , '[' + lc + ']'
                    if z == END or ellyChar.isWhiteSpace(z) and lc in Stops:
                        if nAN > 1:
                            break
                continue

            elif not c in Stops:
                continue

            else:
#               print 'check stopping!'
                d = self.inp.read()
#               print '@3  <<' , self.inp.buf

                if d == None: d = u'!'
#               print 'stop=' , '<' + c + '> <' + d + '>'

#               print 'ellipsis check'
                if c == u'.' and c == d:
                    if self.inp.peek() != c: # look for third '.' in ellipsis
                        self.inp.unread(c)   # if none, keep only first '.'
                    else:
                        self.inp.skip()      # found ellipsis
                        sent.append(d)       # complete it in sentence buffer
                        sent.append(d)       #
                        x = self.inp.peek()  # look at char after ellipsis
                        if ellyChar.isCombining(x):
                            sent.append(SP)  # if part of token, put in space as separator
                    continue

                # special check for multiple stops

#               print 'next char d=' , d , ord(d) if d != END else 'NONE'
                if d in Stops:
                    while True:
                        d = self.inp.read()
                        if not d in Stops: break
                    self.inp.unread(d)
                    if not ellyChar.isWhiteSpace(d):
                        d = SP               # make rightside context for stop

                # special check for blank or null after stops

                elif d != END and not ellyChar.isWhiteSpace(d):
                    if self.shortBracketing(sent,d): break
                    if d in self._cl and self._cl[d] == 1:
                        dn = self.inp.peek()
                        if ellyChar.isWhiteSpace(dn):
                            sent.append(d)
                            break
                    self.inp.unread(d)
#                   print 'no space after punc'
                    continue

                # if no match for lookahead, put back

                elif d != END:
#                   print 'unread d=' , d
                    self.inp.unread(d)

#               print 'possible stop'

                # final check: is sentence long enough?

                if inBrkt:
#                   print 'c=' , '<' + c + '>' , 'd=' , '<' + d + '>' , 'preview=' , self.inp.preview()
#                   print 'nspc=' , nspc
                    if c in [ ':' , ';' ] or nspc < 3:
                        sent.append(d)
#                       print 'add' , '<' + d + '> to sentence'
#                       print 'sent=' , sent
                        self.inp.skip()
                        nspc -= 1
                        continue

#               print '@4  <<' , self.inp.buf
                cx = self.inp.peek()
                if cx == None: cx = u'!!'
#               print 'sentence break: next=' , '<' + cx + '>' , len(cx) , sent
#               print 'nAN=' , nAN , 'inBrkt=' , inBrkt
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
    print 'reading exceptions from:' , dfs
    inp = ellyDefinitionReader.EllyDefinitionReader(dfs)
    if inp.error != None:
        print >> sys.stderr, 'cannot read stop exceptions'
        print >> sys.stderr, inp.error
        sys.exit(1)

    stpxs = stopExceptions.StopExceptions(inp)

    tst = sys.argv[1] if len(sys.argv) > 1 else 'sentenceTestData.txt'
    ins = open(tst,'r')
    rdr = EllySentenceReader(ins,stpxs)

    print ""
    while True:
        sents = rdr.getNext()
        if sents == None or len(sents) == 0: break
        s = u''.join(sents)
        print '>>>>' , u'\u27ea' + s + u'\u27eb'

    ins.close()
