#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# interpretiveContext.py : 09nov2015 CPM
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
data structures for communicating between generative procedures and collecting
their output into a single stream
"""

import sys
import conceptualWeighting

deletion = '_d_'  # name to save deletions under in local stack

class InterpretiveContext(object):

    """
    for context object shared by all semantic procedures for a grammar,
    both generative and cognitive

    attributes:
        lbstk  - for tracking binding of local variables
        locls  - for storing string values of defined local  variables
        glbls  - for storing string values of defined global variables
        buffs  - buffers currently defined
        buffn  - index of currently active buffer
        tokns  - token list by position
        procs  - for storing standalone procedures under name
        wghtg  - weighting of semantic concepts by current importance
        syms   - symbol table for grammar
        cncp   - saved concept
    """

    def __init__ ( self , syms , procs , glbls , hiery ):

        """
        initialization

        arguments:
            self  -
            syms  - symbol table
            procs - standalone procedure dictionary
            glbls - global variables dictionary
            hiery - conceptual hierarchy
        """

        self.syms = syms
        self.procs = procs
        self.glbls = glbls
        self.wghtg = conceptualWeighting.ConceptualWeighting(hiery)
        self.reset()

    def reset ( self ):

        """
        start with empty buffers and global variables with default values

        arguments:
            self  -
        """

        self.lbstk = [ ]             # stack for procedures

        self.clearLocalStack()       # for defining local variables later
        self.clearBuffers()          # for output buffers

        self.tokns = [ ]             # empty out token list for parse
        self.cncp = None             # no initial contextual concept

    def getProcedure ( self , name ):

        """
        get code for named procedure

        arguments:
            self  -
            name  - procedure name

        returns:
            GenerativeProcedure
        """

        return None if not name in self.procs else self.procs[name]

    def setProcedure ( self , name , proc ):

        """
        set code for named procedure

        arguments:
            self  -
            name  - procedure name
            proc  - generative semantic procedure
        """

        self.procs[name] = proc

    def getGlobalVariable ( self , name ):

        """
        get string for specified global

        arguments:
            self  -
            name  - of global

        returns:
            string if successful, None otherwise
        """

        return '' if not name in self.glbls else self.glbls[name]

    def setGlobalVariable ( self , name , s ):

        """
        set string for specified global

        arguments:
            self  -
            name  - of global
            s     - new value to be assigned
        """

        self.glbls[name] = s

    def defineLocalVariable ( self , var , val='' ):

        """
        define new local variable in current stack frame

        arguments:
            self  -
            var   - variable name
            val   - option initial value
        """

#       print 'local stack' , self.lbstk
        ls = self.lbstk[-1]             # get locals defined already for procedure
        if not var in ls:               # already in list?
            ls.append(var)              # can define only once per procedure
            if not var in self.locls:   # already defined elsewhere?
                self.locls[var] = [ ]   # if not, need to initialize dictionary
            self.locls[var].append(val) # set to initial value

    def getLocalVariable ( self , var ):

        """
        get current value of a given local variable

        arguments:
            self  -
            var   - variable name
        """

        if not var in self.locls: return '' # if not locally defined anywhere, return ''
        h = self.locls[var]                 # list of bindings for variable
        return '' if len(h) == 0 else h[-1] # if not empty, return last binding

    def setLocalVariable ( self , var , val='' ):

        """
        set given local variable to value

        arguments:
            self  -
            var   - variable name
            val   - value
        """

#       print 'var=' , var
#       print self.locls
        if not var in self.locls:         # locally defined anywhere?
            self.defineLocalVariable(var) # if not, define locally for current procedure
        self.locls[var][-1] = val         # reset last binding to new value

    def getDeletion ( self ):

        """
        get sequence last deleted

        arguments:
            self

        returns:
            string of last deleted chars
        """

        h = self.locls[deletion]            # find deletion saver
        return '' if len(h) == 0 else h[-1] # get last deletion if there was one

    def putDeletion ( self , ds ):

        """
        save last deleted sequence

        arguments:
            self  -
            ds    - deletion sequence
        """

        h = self.locls[ deletion ] # find deletion saver
        h[-1] = ''.join(ds)        # save last deletion as string

    def clearLocalStack ( self ):

        """
        empty out local stack

        arguments:
            self
        """

        self.locls = { }
        self.locls[ deletion ] = [ [ ] ] # for saving deletions

    def splitBuffer ( self ):

        """
        create new output buffer and move to it

        arguments:
            self
        """

        self.buffn += 1
        if self.buffn < len(self.buffs):
            return
        self.buffs.append([ ])
        return

    def backBuffer ( self ):

        """
        return to preceding buffer

        arguments:
            self
        """

        if self.buffn == 0:
            return
        self.buffn -= 1
        return

    def mergeBuffers ( self ):

        """
        merge current buffer with all later buffers

        arguments:
            self
        """

        n = len(self.buffs) - self.buffn - 1   # how many buffers to merge in
        while n > 0:
            b = self.buffs.pop()               # get last buffer
            self.buffs[-1].extend(b)           # merge its contents with preceding buffer
            n -= 1

    def clearBuffers ( self ):

        """
        revert to single empty buffer

        arguments:
            self
        """

        self.buffn = 0
        self.buffs = [ [ ] ]

    def findCharsInBuffer ( self , ts , sns=True ):

        """
        find string ts in next buffer and transfer chars up to and including
        first occurrence or until entire next buffer is exhausted

        arguments:
            self  -
            ts    - string to look for
            sns   - direction of search: True=forward, False=backward
        """

        n = self.buffn + 1
        if n >= len(self.buffs): return
        t = list(ts)         # list of chars to look for
        ln = len(t)          # length of list
        bn = self.buffs[n]   # next buffer
        bc = self.buffs[n-1] # current one
        if sns:              # forward scanning
            while len(bn) >= ln:
                if t == bn[:ln]:
                    bc += t
                    self.buffs[n] = bn[ln:]
                    return   # match
                bc.append(bn.pop(0))
            bc.extend(bn)
            self.buffs[n] = [ ]
        else:                # reverse scanning
            tmp = [ ]        # buffer scanned chars for reverse scan
            while len(bc) >= ln:
                if t == bc[-ln:]:
#                   print 'find < ln=' , ln , bc
                    self.buffs[n] = t + tmp + bn
                    self.buffs[n-1] = bc[:-ln]
                    return   # match
                tmp.insert(0,bc.pop())
            self.buffs[n] = bc + tmp + bn
            self.buffs[n-1] = [ ]

    def mergeBuffersWithReplacement ( self , ts , ss ):

        """
        merge current and next buffers, replacing occurrences of ts with ss

        arguments:
            self  -
            ts    - string to look for
            ss    - its replacement
        """

        n = self.buffn + 1
        if n >= len(self.buffs): return
        t = list(ts)
        ln = len(t)
        s = list(ss)
        bs = self.buffs
        k = len(bs) - 1
        while k > n:
            b = bs.pop()             # merge all newer buffers
            bs[k-1].extend(b)        #
            k -= 1
        bn = bs.pop()                # is now immediately next buffer
        bc = bs[-1]                  # current one
        while len(bn) >= ln:         # match is still possible?
            if t == bn[:ln]:         # compare chars
                bn = bn[ln:]         # on match, remove those chars
                bc.extend(s)         # and put replacement in current buffer
            else:
                bc.append(bn.pop(0)) # no match; move 1 char from next to current buffer
        bc.extend(bn)                # move remaining chars from next to current one

    def deleteCharsFromBuffer ( self , n=1 ):

        """
        delete up to n chars from next or current buffer

        arguments:
            self  -
            n     - maximum char count to delete
                  -   n < 0 means current buffer
                  -   n > 0       next    buffer
        """

        if n == 0:
            return
        k = self.buffn
        if n > 0:
            k += 1
            if k >= len(self.buffs): return
        b = self.buffs[k]           # buffer to delete from
        l = len(b)                  # its current char count
        if l <= abs(n):             # enough chars to delete
            self.buffs[k] = [ ]     # if not, empty out buffer
            self.putDeletion(b)
        elif n > 0:                 # delete from next buffer?
            self.buffs[k] = b[n:]   # remove n chars from front
            self.putDeletion(b[:n])
        else:
            self.buffs[k] = b[:n]   # remove n chars from back of current buffer
            self.putDeletion(b[n:])

    def deleteCharsInBufferTo ( self , s ):

        """
        delete chars in next buffer up to first occurrence of specified sequence

        arguments:
            self  -
            s     - specified sequence as string
        """

#       print '  deleting to' , s
        k = self.buffn + 1
        if k >= len(self.buffs): return
        ls = list(s)              # convert string to list for comparisons
        l = len(ls)               # char count
        bs = self.buffs[k]        # saved buffer
        b = list(bs)              # copy of buffer for scanning
        while l <= len(b):        # enough chars to match?
            if ls == b[:l]: break # if so, check match
            b.pop(0)
        else:
            b = [ ]               # no match, empty out scan
            l = 0                 # take zero length match

        nd = len(bs) - len(b) + l # must delete matched sequence also
#       print '  delete' , nd , k
        self.putDeletion(bs[:nd]) # save deletion
        self.buffs[k] = bs[nd:]   # shorten next buffer

    def deleteCharsInBufferFrom ( self , s ):

        """
        delete chars in current buffer from last occurrence of specified sequence

        arguments:
            self  -
            s     - specified sequence as string
        """

#       print '  deleting from' , s
        k = self.buffn
        ls = list(s)               # convert string to list for comparisons
        l = len(ls)                # char count
        bs = self.buffs[k]         # saved buffer
        b = list(bs)               # copy of buffer for scanning
        while l <= len(b):         # enough chars to match?
            if ls == b[-l:]: break # if so, check match
            b.pop()
        else:
            b = [ ]                # no match, empty out scan
            l = 0                  # take zero length match

        nd = len(bs) - len(b) + l  # must delete matched sequence also
#       print '  delete' , nd , k
        self.putDeletion(bs[-nd:]) # save deletion
        self.buffs[k] = bs[:-nd]   # shorten current buffer

    def prependCharsInCurrentBuffer ( self , s ):

        """
        put specified chars at start of current buffer

        arguments:
            self  -
            s     - chars in string
        """

        self.buffn -= 1                 # make current buffer into next
        self.insertCharsIntoBuffer(s,1) # insert into next
        self.buffn += 1                 # next becomes current again

    def insertCharsIntoBuffer ( self , s , dirn=0 ):

        """
        insert specified chars in current or next buffer

        arguments:
            self  -
            s     - chars in string
            dirn  - direction (0= current, 1= next)
        """

        if dirn == 0:
            b = self.buffs[self.buffn]
            b.extend(list(s))
        else:
            k = self.buffn + 1
            if k >= len(self.buffs):
                self.buffs.append([ ])
            b = self.buffs[k]
            self.buffs[k] = list(s) + b

    def checkBufferForChars ( self , s ):

        """
        check start of next buffer against string

        arguments:
            self  -
            s     - comparison string
        returns:
            True on match, False otherwise
        """

        if self.buffn + 1 == len(self.buffs): return False
        l = len(s)
        b = self.buffs[self.buffn]
        return False if l > len(b) or s != b[:l] else True

    def extractCharsFromBuffer ( self , n=1 , m=0 ):

        """
        get chars from start of next or current buffer

        arguments:
            self  -
            n     - character count
            m     - mode
                  -   m == 0 means from next    buffer
                  -   m == 1            current buffer
        returns:
            string of chars if successful, '' otherwise
        """

        if n == 0:
            return ''
        elif m == 0:
            k = self.buffn + 1
            if k == len(self.buffs): return ''
            b = self.buffs[k]
            l = len(b)
            if n > l: return ''
            s = b[:n]
            self.buffs[k] = b[n:]
        else:
            b = self.buffs[self.buffn]
            l = len(b)
            if n > l: return ''
            s = b[-n:]
            self.buffs[self.buffn] = b[:-n]
        return u''.join(s)

    def moveCharsBufferToBuffer ( self , n ):

        """
        move up to n chars between adjacent buffers

        arguments:
            self  -
            n     - maximum char count
                  -   n > 0 means from next to current buffer
                  -   n < 0 means      current to next
        """

        k = self.buffn + 1
        if n == 0:
            return
        if n < 0:
            n = -n
            if k == len(self.buffs):
                self.buffs.append([ ])
            bs = self.buffs[k-1]
            bd = self.buffs[k]
            l = len(bs)
            if n > l: n = l
            self.buffs[k] = bs[-n:] + bd
            self.buffs[k-1] = bs[:-n]
        else:
            if k == len(self.buffs):
                return
            bs = self.buffs[k]
            bd = self.buffs[k-1]
            l = len(bs)
            if n > l: n = l
            self.buffs[k-1].extend(bs[:n])
            self.buffs[k] = bs[n:]

    def peekIntoBuffer ( self , nxtb=True ):

        """
        look at last char in current or first char in next buffer without disturbing it

        arguments:
            self  -
            nxtb  - selects next buffer

        returns:
            peeked char if it exists, otherwise ''
        """

        c = ''
        if nxtb:
            k = self.buffn + 1
            if k < len(self.buffs):
                b = self.buffs[k]
                if len(b) > 0:
                    c = b[0]
        else:
            b = self.buffs[self.buffn]
            if len(b) > 0:
                c = b[-1]
        return c

    def getBufferContent ( self ):

        """
        get content of all buffers as single char list

        arguments:
            self

        returns:
            list of chars from buffers
        """

        self.mergeBuffers()   # combine all current buffers into first one
#       print 'merged=' , self.buffs[0]
        return self.buffs[0]  # list of combined chars

    def getBufferContents ( self ):

        """
        get list of the lists of chars from all active buffers

        arguments:
            self

        returns:
            list of lists of chars in each buffer
        """

        b = [ ]
        for bs in self.buffs:
            b.append(bs)  # append buffer content, but keep lists separate
        return b

    def viewBufferDivide ( self , n ):

        """
        show last n chars of current buffer and
        first n chars of next buffer

        arguments:
            self  -
            n     - char count

        returns:
            list of two char lists
        """

        k = self.buffn
        buf = self.buffs[k]
        nbc = len(buf)
        if nbc == 0:
            curs = [ ]
        else:
            curs = buf[-n:] if nbc > n else buf[-nbc:]
        k += 1
        if k == len(self.buffs):
            nxts = [ ]
        else:
            buf = self.buffs[k]
            nbc = len(buf)
            if nbc == 0:
                nxts = [ ]
            else:
                nxts = buf[:n] if nbc > n else buf[:nbc]
        return [ curs , nxts ]

    def addTokenToListing ( self , tok ):

        """
        put token into list for current sentence being parsed

        arguments:
            self  -
            tok   - token to save
        """

        self.tokns.append(tok)

    def getNthTokenInListing ( self , n ):

        """
        get specified token in parsing

        arguments:
            self  -
            n     - which token

        returns:
            token if successful, None otherwise
        """

        return None if n >= len(self.tokns) else self.tokns[n]

    def interpretConcept ( self , cn ):

        """
        get importance score for specified concept

        arguments:
            self  -
            cn    - concept as name string

        returns:
            integer importance score
        """

        return self.wghtg.interpretConcept(cn)

    def relateConceptPair ( self , cna , cnb ):

        """
        get relatedness of two specified concepts

        arguments:
            self  -
            cna   - first concept as name string
            cnb   - second

        returns:
            integer relatedness score
        """

        return self.wghtg.relateConceptPair(cna,cnb)

    def pushStack ( self ):

        """
        make stack frame for local variables of generative procedure

        arguments:
            self
        """

#       print 'pushStack' , len(self.lbstk)
        self.lbstk.append([ deletion ])     # to hold bindings for procedures
        self.locls[ deletion ].append([ ])  # set deletion to empty char list

    def popStack ( self ):

        """
        free up stack for generative procedure

        arguments:
            self
        """

#       print 'popStack' , len(self.lbstk)
        r = self.lbstk.pop()      # remove procedure bindings from binding stack
        for v in r:
            stk = self.locls[v]
            stk.pop()             # remove their values from local stack
            if len(stk) == 0:
                del self.locls[v] # if all values gone, remove empty list

    def printStatus ( self , pnam='' ):

        """
        show where current stack and buffer are

        arguments:
            self  -
            pnam  - procedure name to report
        """

        sys.stderr.write(' stk=' + str(len(self.lbstk)))
        if pnam != '':
            sys.stderr.write(' in (' + pnam + ')')
        sys.stderr.write(' buf=' + str(len(self.buffs)))
        sys.stderr.write(' (' +  str(len(self.buffs[self.buffn])) + ' chars)\n')
        sys.stderr.flush()

    def echoTokensToOutput ( self ):

        """
        copy all tokens to output buffer

        arguments:
            self
        """

        toks = map((lambda x: 'NONE' if x == None else x.orig),self.tokns)
        self.insertCharsIntoBuffer(u''.join(toks))
