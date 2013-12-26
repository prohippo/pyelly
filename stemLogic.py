#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# stemLogic.py : 04jun2013 CPM
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

import ellyChar
import ellyDefinitionReader

directory = './' # directory for stemming logic files

class Reader(ellyDefinitionReader.EllyDefinitionReader):

    """
    subclass with special reformatting for stem logic

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
        self.up.__init__(directory + source)

    def readline ( self ):

        """
        input with reformatting to make parsing easier

        arguments:
            self

        returns:
            string with single spaces and { } separated
        """

#       print "readline()"

        line = '!'
        while line[0] == '!':               # ignore these lines as comments
            line = self.up.readline()       # get next line from source
#           print "( ", line, " )"
            if line == "": return ""        # EOF check
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
            elif ord(c) == 9:               # check for TAB
                if not ns:                  #
                    out.append(u' ')        # replace
                    ns = True               # last char is now space
            else:                           #
                out.append(c)               # put nonspace into output buffer
                ns = False                  # last char was not space

        if out[-1] == u' ': out.pop()       # remove any trailing space
        return ''.join(out)                 # return reformatted line

# function status return codes

isFAIL= -1  # error indication
isNOTM=  0  # no match
isMTCH=  1  # match
doMORE=  2  # match and do more

# operation code ranges

nlen=20     # checks of original length should be less than this

# specific operation codes

YE=-2 # success
NO= 0 # failure
IF= 1 # check for letter sequence
IS= 8 # is in specified set
LT=16 #        < for original token length
GT=17 #        >
EQ=18 # length =
NE=19 #       !=
VO=40 # basic code for vowel check to restore -E
MO=50 # continuation to another logic table

class StemLogic(object):

    """
    stemming logic

    attributes:
        table - encoded logic
    """

    def __init__ ( self , source=None ):

        """
        constructor

        arguments:
            self   -
            source - logic definition
        """

        self.table = [ ]   # for stemming logic, initially empty

        if (not source is None):
            status = self.define(source)
            if status > 0: return None
 
    def define ( self , source ):

        """
        set up logic block for stemming from text input

        arguments:
            self   -
            source - logic definition

        returns:
            success flag: 0 for success, line number on error
        """

        self.table = [ ]         # make sure table is empty

        stk = [ ] # stack to save place for skip count in logic block
        lno = 0   # input line number for error code

        ins = Reader(source)     # formatted input

#       print ":", source

        while True:
            line = ins.readline()

#           print "::", line

            if len(line) == 0: break

            lno += 1             # update line number

            lp = line.split(' ') # get components of line
#           print ">> " , lp
            op = lp.pop(0)       # opcod is first component
#           print "op=" , op
            ln = len(lp)         # how many tokens following

            if op == 'block':
                if len(self.table) > 0: return lno
                if ln == 0:
                    self.table.append("")       # no necessary condition for logic match
                else:
                    seq = lp.pop(0)[::-1]       # reverse chars for easier matching
#                   print seq, "<->", seq[::-1]
                    self.table.append(seq)      # save
                continue

            elif op == 'if':
#               print "ln=", ln
                if ln == 0: return lno          # must have sequence to check
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
                        return lno              # error if stack empty
                    k = stk.pop()               # where to fill in skip branch
                    self.table[k] = len(self.table) - k
                    continue

            elif op == 'is':
                if ln < 1: return lno           # must have argument
                self.table.append(IS)           # insert opcode to check for letter in set
                stk.append(len(self.table))     # where to put branch skip
                self.table.append(-1)           # mark branch skip as unset
                self.table.append(lp.pop(0))    # letter set to check
                if ln == 1: continue

            elif op == 'len':
                if ln < 2: return lno           # must have comparison operator and length
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
                    return lno
                stk.append(len(self.table))     # where to put branch skip
                self.table.append(-1)           # mark branch skip as unset
                k = int(lp.pop(0))              # comparison length
                self.table.append(k)            # insert comparison length
                if ln == 2: continue

            elif op == 'default':               # default action for entire logic block
                if len(stk) > 0: return lno     # stack should be empty now

            else:                               # any other opcode is an error
                return lno

            """
            process action code
            """

#           print lp

            if len(lp) < 3: return lno        # action code must be enclosed in { }

            lp.pop(0)                         # drop {
            lp.pop()                          # and  }
            act = lp.pop(0)                   # action code

#           print "act= ", act

            if act == 'su':                   # drop suffix with possible extra changes
                if len(lp) == 0:
                    self.table.append(YE)     # insert success opcode
                    self.table.append("")     # no additions
                else:
                    drop = int(lp.pop(0))     # how more chars to drop
#                   print "drop ", drop
                    self.table.append(YE-drop)# insert success modified opcode
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
                if len(lp) == 0: return lno   # must have added code for action
                cs = lp.pop(0)
                if cs == 'vowel':             # vowel check?
                    self.table.append(VO)     # insert vowel check opcode

                elif cs == 'more':            # go to next logic table?
                    self.table.append(MO)

                else:                         # bad check
                    return lno

            else:                             # error on action
                return lno

#           print "stk@", len(stk)
            if len(stk) > 0:
                k = stk.pop()                 # where to fill in skip branch
                self.table[k] = len(self.table) - k

        return 0 # code for success

    def apply ( self , token ):

        """
        apply inflectional stemming logic against token

        arguments:
            self  -
            token - input token
        returns:
            status code
        """

        last = u'.'             # to save last popped letter

        if len(self.table) < 2: # check for empty table
            return isNOTM       # 
#       print self.table[0]
        it = 0                  # stemming logic index
        word = token.root       # list of letters in token word
        m  = len(word)          # end of word
        seq = self.table[it]    # suffix to match
        it += 1                 #
        n  = len(seq)           # ending length to match
        if n >= m:              # 
            return isNOTM       # word not long enough for ending

        # check that table is right one for word ending

        ew = m                  # current position in token word

#       print "suffix length= ", n, ", word length= ", m
        if n > 0:
            for i in range(n):
                ew -= 1
#               print word[ew], " cmp ", seq[i]
                if word[ew] != seq[i]:
                    return isNOTM
#           print "out @", word[ew-1]
            if not ellyChar.isLetter(word[ew-1]):
                return isNOTM
        
        # interpret table logic

        while True:                 # advance through logic until success or failure

            opcode = self.table[it] # next operation code to interpret
            it += 1                 #
#           print "opcode= ", opcode

            if opcode < 0:          # YE with possible modifications

                # word satisfies conditions for ending removal

#               print 'm=', m, ', ew= ', ew
                for i in range(n):
                    last = word.pop()        # remove matched ending from word
#               print '=', word
#               print 'drop extra chars'
                nm = YE - opcode         # get removal count from opcode
#               print "nm= ", nm
                if (nm < 0):
                    word.append(last)    # negative count restores last removed letter
                else:
                    while nm > 0:        # otherwise drop additional letters
                        last = word.pop()
                        nm -= 1
                word.extend(self.table[it])
                it += 1
                        
                return isMTCH                # success flag

            elif opcode == NO:

                # no match

#               print "fail!"
                return isNOTM

            elif opcode == IF:

                # enter logic block if a char sequence matches

                seq = self.table[it+1]
                sln = len(seq)
                if (sln > ew):
                    it += self.table[it]      # if not, skip over block of logic
                else:
                    i = 0
                    iw = ew - 1
                    while i < sln and word[iw-i] == seq[i]:
                        i += 1
                    if i < sln:               # any characters unmatched?
                        it  += self.table[it] # if so, skip over block of logic
                    else:
                        it += 2               # otherwise, enter logic block
                        ew -= sln             # update index in word
                        
            elif opcode == IS:

                # check whether next character is in a specified set

                if ew <= 0:               # any letters left in word?
                    it += self.table[it]  # if not, skip over block
                    continue
                set = self.table[it+1]    # get character set
                c = word[ew-1]
#               print c, ':', set
                if set.find(c) < 0:       # word character in set?
                    it += self.table[it] 
                else:
                    it += 2               # if so, enter block

            elif opcode < nlen:

                # check length of word

                k = self.table[it+1]          # comparison length
#               print "k= ", k, " : m= ", m
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
 
                for i in range(n):            # treat as success
                    word.pop()                # remove all of ending
                return doMORE                 # let other table figure out what to do

            elif opcode == VO:                # look for CVC pattern at end of stemming
                                              # and possibly restore -E

                for i in range(n):            # strip ending from end of word
                    last = word.pop()         #

                me = len(word) - 2            # at possible vowel in stemming result
                                              # last char assumed to be consonant

#               print "vowel @", me, word[me]

                if me < 0 or ellyChar.isStrongConsonant(word[me]):
                    return isMTCH

                me -= 1                       # vowel found; now check for consonant

#               print "consonant @", me, word[me]

                if me < 0 or ellyChar.isStrictVowel(word[me]):
                    return isMTCH
                if me <= 0 or word[me] != u'u' or word[me - 1] == u'q':
                    word.append(u'e')         # put back -E

                return isMTCH

            else:

                return isNOTM

        return isFAIL

"""
interactive unit test interface
"""

if __name__ == "__main__":

    import sys
    import ellyToken
    import stemTest

    if len(sys.argv) < 2:
        print "usage: X stem_logic_file_name"
        sys.exit(0)

    log = StemLogic()

    print sys.argv[1]

    sta = log.define(sys.argv[1])
    if (sta > 0):
        print "definition errar at " , sta
        sys.exit(1)

    tab = log.table
    siz = len(tab)
    print "sta= ", sta, " siz= ", siz
    if siz == 0:
        print "NULL table"
        sys.exit(1)
    M = 16
    for i in range(siz):
        if (i%M == 0): print ""
        print tab[i],
    print ""

    stemTest.stemTest(log,tab[0][::-1])
