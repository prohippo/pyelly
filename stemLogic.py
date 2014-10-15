#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# stemLogic.py : 15oct2014 CPM
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
for implementing stemming logic rules as a table object
"""

import sys
import ellyChar
import ellyException
import ellyDefinitionReader

directory = './' # directory for stemming logic files

class Reader(ellyDefinitionReader.EllyDefinitionReader):

    """
    text input subclass with special reformatting for stem logic

    attributes:
        up - super object
    """

    def __init__ ( self , source ):

        """
        constructor

        arguments:
            self   -
            source - where to get input from
        """

        self.up = super(Reader,self)
        super(Reader,self).__init__(directory + source)

    def readline ( self ):

        """
        input with reformatting to make parsing easier

        arguments:
            self

        returns:
            string with single spaces and { } separated
        """

#       print "readline()"

        line = self.up.readline()           # get next line from source
#       print "[", line, "]"
        if line == "": return ""            # EOF check
        a = list(unicode(line.lower()))     # get list of chars in line as Unicode
#       print a
        ns = True                           # flag for last char being a space
        out = [ ]                           # output buffer for reformatted line
        for c in a:                         # iterate on input chars
            if c == u'{' or c == u'}':      # found '{' or '}'?
                if not ns: out.append(u' ') #
                out.extend([c , u' '])      # put spaces on each side of '{' or '}'
                ns = True                   # last char is now space
            elif c == u' ':                 # found space ?
                if not ns:                  #
                    out.append(c)           # insert only if last char was not space
                    ns = True               # mark last char as space
            else:                           #
                out.append(c)               # put nonspace into output buffer
                ns = False                  # last char was not space

        if out[-1] == u' ': out.pop()       # remove any trailing space
        return ''.join(out)                 # return reformatted line

# status codes returned by apply() method of StemLogic class

isNOTM =  0  # no match
isMTCH =  1  # match
doMORE =  2  # match and do more

# operation code ranges

Nlen = 20     # checks of original length should be less than this

# specific operation codes for stemming logic

YE = -2 # success  # have to allow for {SU -1 xx}
NO =  0 # failure
IF =  1 # check for letter sequence
IS =  8 # is in specified set
LT = 16 #        < for original token length
GT = 17 #        >
EQ = 18 # length =
NE = 19 #       !=
VO = 40 # basic code for vowel check to restore -E
MO = 50 # continuation to another logic table

class StemLogic(object):

    """
    stemming logic

    attributes:
        table  - encoded logic
        input  - save line for error reporting
        error  - total count in processing definition input
        source - definition input
    """

    def __init__ ( self , source=None ):

        """
        constructor

        arguments:
            self   -
            source - logic definition from file or array

        exceptions:
            FormatFailure on error
        """

        self.table = [ ]   # for stemming logic, initially empty
        self.input = ''
        self.error = 0

        if source != None and not self.define(source):
            print >> sys.stderr , '** unable to load' , source
            raise ellyException.FormatFailure

    def _err ( self , s ):

        """
        report error and count up

        arguments:
            self  -
            s     - error message
        """

        print >> sys.stderr , '** stem logic error:' , s ,
        print >> sys.stderr , ('' if self.error > 0 else 'in ' + self.source)
        if self.input != '':
            print >> sys.stderr , '*  at [' , self.input , ']'
        self.error += 1
 
    def define ( self , source ):

        """
        set up logic block for stemming from text input

        arguments:
            self   -
            source - logic definition

        returns:
            True for success, False otherwise
        """

        self.source = source
        self.table  = [ ]        # empty table at start

        stk = [ ] # stack to save place for skip count in logic block

        ins = Reader(source)     # reformatted input
        if ins.error != None:
            print >> sys.stderr , '**' , ins.error
            return False         # cannot read any logic

#       print ":", source

        blocking    = False      # no blocking yet
        defaulting  = False      # no defaulting yet

        while True:
            line = ins.readline()
            self.input = line    # for any error reporting

#           print "::", line

            if len(line) == 0: break

            lp = line.split(' ') # get components of line
#           print ">> " , lp
            op = lp.pop(0)       # opcod is first component
#           print "op=" , op
            ln = len(lp)         # how many tokens following

            if op == 'block':
                if len(self.table) > 0:
                    self._err('unexpected restart of logic')
                    continue
                if ln == 0:
                    self.table.append("")       # no necessary condition for logic match
                else:
                    seq = lp.pop(0)[::-1]       # reverse chars for easier matching
#                   print seq, "<->", seq[::-1]
                    self.table.append(seq)      # save
                blocking = True
                continue

            elif op == 'if':
#               print "ln=", ln
                if ln == 0:
                    self._err('no IF char sequence to check')
                    continue
                seq = lp.pop(0)                 # get match condition
#               print "seq=", seq
                self.table.append(IF)           # insert opcode for conditional sequence match
                stk.append(len(self.table))     # where to put branch skip
                self.table.append(-1)           # mark branch skip as unset
                self.table.append(seq)          # letter sequence to check
                if ln == 1: continue            # if no immediate action specified
#               print "!!!!"

            elif op == 'end':
                if ln == 0:                     # any action code code?
                    if len(stk) == 0:
                        self._err('END with no logic for it')
                        continue
                    k = stk.pop()               # where to fill in skip branch
                    self.table[k] = len(self.table) - k
                    continue

            elif op == 'is':
                if ln < 1:
                    self._err('no arguments for IS')
                    continue
                self.table.append(IS)           # insert opcode to check for letter in set
                stk.append(len(self.table))     # where to put branch skip
                self.table.append(-1)           # mark branch skip as unset
                self.table.append(lp.pop(0))    # letter set to check
                if ln == 1: continue

            elif op == 'len':
                if ln < 2:
                    self._err('incomplete LEN')
                    continue
                cm = lp.pop(0)                  # which comparison?
                if cm == '=':                   # equality
                    self.table.append(EQ)
                elif cm == '<':                 # less than
                    self.table.append(LT)
                elif cm == '>':                 # greater than
                    self.table.append(GT)
                elif cm == '!=':                # inequality
                    self.table.append(NE)
                else:                           # anything else is an error
                    self._err('unrecognized LEN comparison')
                    continue
                stk.append(len(self.table))     # where to put branch skip
                self.table.append(-1)           # mark branch skip as unset
                try:
                    k = int(lp.pop(0))          # comparison length
                except ValueError:
                    self._err('bad LEN comparison')
                    continue
                self.table.append(k)            # insert comparison length
                if ln == 2: continue

            elif op == 'default':               # default action for entire logic block
                if len(stk) > 0:
                    self._err('missing END(s) at end of logic')
                    break                       # stop further error checking
                if defaulting:
                    self._err('multiple DEFAULT')
                    break
                defaulting = True

            else:                               # any other opcode is an error
                self._err('unknown logic operation')
                continue

#
#           process any action code
#

#           print 'lp=' , lp

            if len(lp) < 3 or lp[0] != '{' or lp[-1] != '}':
                self._err('bad action code')
                continue

            lp.pop(0)                         # drop {
            lp.pop()                          # and  }
            act = lp.pop(0)                   # action code operation

#           print "act= ", act

            if act == 'su':                   # drop suffix with possible extra changes
                if len(lp) == 0:
                    self.table.append(YE)     # insert success opcode
                    self.table.append("")     # no additions
                else:
                    try:
                        drop = int(lp.pop(0)) # how more chars to drop
                    except ValueError:
                        self._err('bad SU drop count')
                        continue
#                   print "drop ", drop
                    dy = YE - drop
                    if dy > 0:
                        self._err('bad SU restoration')
                        continue
                    self.table.append(dy)     # insert success modified opcode
                                              # opcodes here may be -1, -2, -3, ...
                                              # -1 means to restore last char dropped
                                              # -2          drop no chars
                                              # -3          drop 1 char
                                              #    and so forth
                    if len(lp) == 0:
                        self.table.append("") # no additions to stemmed results
                    else:
                        add = lp.pop(0)       # additions after stemming
                        self.table.append(add)# save

            elif act == 'fa':                 # make no stemming changes
                self.table.append(NO)         # insert failure opcode

            elif act == 'do':                 # special action
#               print "do ",lp
                if len(lp) == 0:
                    self._err('must specify what to DO')
                    continue
                cs = lp.pop(0)

                if cs == 'vowel':             # vowel check?
                    self.table.append(VO)     # insert vowel check opcode

                elif cs == 'more':            # go to next logic table?
                    self.table.append(MO)

                else:                         # bad DO action
                    self._err('nothing recognizable to DO')
                    continue

            else:                             # error on action
                self._err('unknown action')
                continue

#           print "stk@", len(stk)
            if len(stk) > 0:
                k = stk.pop()                 # where to fill in skip branch
                self.table[k] = len(self.table) - k

        if not blocking or not defaulting:
            self._err('logic must start with BLOCK and end with DEFAULT')

        return (self.error == 0)

    def apply ( self , token , extra=None ):

        """
        apply inflectional stemming logic against token

        arguments:
            self  -
            token - input token
            extra - extra token char for any restoration
        returns:
            status code
        exceptions:
            StemmingError
        """

        last = None             # save last popped letter

        if len(self.table) < 2: # check for empty table
            return isNOTM       # if so, no match
#       print 'at' , self.table[0] , extra
        it = 0                  # stemming logic index
        word = token.root       # list of letters in token word
        m  = len(word)          # end of word
        seq = self.table[it]    # suffix to match
        it += 1                 #
        n  = len(seq)           # ending length to match
        if n >= m:              # 
            return isNOTM       # word not long enough for ending
        msh = m - n

        # check that table is right one for word ending

        ew = m                  # just past end of token word

#       print "suffix length= ", n, ", word length= ", m
        if n > 0:
            for ix in range(n):
                ew -= 1
#               print word[ew], " cmp ", seq[ix]
                if word[ew] != seq[ix]:
                    return isNOTM
            ew -= 1
#           print "first char before suffix=" ,
#           print '[' +  ( word[ew] if ew >= 0 else None ) + ']'
        
        # interpret table logic

        last = seq[-1] if n > 0 else extra
        word = word[:msh]                # copy of word up to removed suffix
#       print 'word=' , word

        while True:                      # advance through logic until success or failure

            opcode = self.table[it]      # next operation code to interpret
            it += 1                      #
#           print "opcode=", opcode

            if opcode < 0:               # YE(S) on match with possible modifications

                # word satisfies conditions for ending removal

                word = token.root[:msh]             # word without ending
#               print 'word=', word
#               print 'add or drop extra chars'
                nm = YE - opcode                    # get removal count from opcode
#               print 'nm=', nm
                if nm < 0:                          # any special restoration?
                    if last == None:
                        print >> sys.stderr , 'FATAL stemming logic error'
                        sys.stdout.flush()
                        sys.exit(1)
#                   print 'restore' , '[' + last + ']'
                    word.append(last)               # negative count restores last removed letter
                else:
#                   print 'drop' , nm , 'from [' , word , ']'
                    while nm > 0:                   # otherwise drop additional letters
                        if len(word) == 0:
                            print >> sys.stderr , 'FATAL stemming logic error'
                            sys.stdout.flush()
                            sys.exit(1)
                        last = word.pop()
                        nm -= 1

#               print 'extend=' , self.table[it]    # append more chars
                word.extend(self.table[it])

                token.root = word        # replace token with stemmed result
#               print 'word=' , word
#               print 'root=' , token.root
                        
                return isMTCH            # success flag

            elif opcode == NO:           # no match

#               print "fail!"
                return isNOTM

            elif opcode == IF:

                # enter logic block if a char sequence matches

                seq = self.table[it+1]
#               print 'seq=' , seq , 'ew=' , ew , 'word=' , word[:ew]
                sln = len(seq)
                if sln > len(word):           # enough chars to match?
                    it += self.table[it]      # if not, skip over block of logic
                else:
                    k = 0
#                   j = -1
#                   print 'at' , j , word[]
                    while k < sln and word[-k-1] == seq[k]:
#                       print 'word[' + str(k) + ']=' , word[j]
                        k += 1
#                       j -= 1
#                   print 'k=' , k
                    if k < sln:               # any characters unmatched?
#                       print 'IF no match'
                        it  += self.table[it] # if so, skip over block of logic
                    else:
#                       print 'IF match'
                        it += 2               # otherwise, enter logic block
                        word = word[:-sln]    # update index in word
                        
            elif opcode == IS:

                # check whether next character is in a specified set

                if len(word) <= 0:            # any letters left in word?
                    it += self.table[it]      # if not, skip over block
                    continue
                chs = self.table[it+1]        # get character set
                c = word[-1]
#               print c, ':', chs
                if chs.find(c) < 0:           # word character in set?

                    it += self.table[it]      # if not, skip block
                else:
                    it += 2                   # if so, enter block

            elif opcode < Nlen:

                # check length of word

                k = self.table[it+1]          # comparison length
#               print "k= ", k, " : m= ", m , 'opcode=' , opcode
                if   opcode == LT:            # set match flag for type of comparison
                    match = (m <  k)          #
                elif opcode == GT:            #
                    match = (m >  k)          #
                elif opcode == EQ:            #
                    match = (m == k)          #
                elif opcode == NE:            #
                    match = (m != k)          #
                else:
                    return isNOTM

#               print "match= ", match

                if not match:                 # if no match, skip block
                    it += self.table[it]
                else:                         # otherwise, go into logic of block
                    it += 2                   #

            elif opcode == MO:                # continue to another logic table

                token.root = token.root[:msh]
#               print 'for more, set root=' , token.root
                return doMORE                 # let other table figure out what to do

            elif opcode == VO:                # look for CVC pattern at end of stemming
                                              # and possibly restore -E

                word = token.root[:msh]       # strip ending from end of word
#               print 'vowel check for' , word

                me = len(word) - 2            # at possible vowel in stemming result
                                              # last char assumed to be consonant

#               print 'me=' , me
                if me < 0 or ellyChar.isStrongConsonant(word[me]):
                    token.root = word
                    return isMTCH

                me -= 1                       # vowel found; now check for consonant
#               print 'me=' , me

                if me < 0 or ellyChar.isStrictVowel(word[me]):
                    return isMTCH
                if me <= 0 or word[me] != u'u' or word[me - 1] == u'q':
                    word.append(u'e')         # put back -E
                token.root = word
#               print 'final word=' , word
                return isMTCH

            else:

                return isNOTM

        raise ellyException.StemmingError

#
# unit test
#

if __name__ == "__main__":

    import stemTest

    if len(sys.argv) < 2:
        print "usage: X stem_logic_file_name"
        sys.exit(0)

    log = StemLogic()

    print 'reading' , sys.argv[1]

    if not log.define(sys.argv[1]):
        print "logic definition failed"
        sys.exit(1)

    tab = log.table
    siz = len(tab)
    print " logic size= ", siz
    if siz == 0:
        print >> sys.stderr , "NULL table"
        sys.exit(1)
    M = 16
    for i in range(siz):
        if i%M == 0: print ""
        print tab[i],
    print ""

    stemTest.stemTest(log,tab[0][::-1])
