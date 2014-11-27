#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# timeTransform.py : 06nov2014 CPM
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
recognize English time references in text and normalize to 00:00:00zzz form
"""

import ellyChar
import simpleTransform

Zn = [ # time zones
    u'est' , u'edt' ,
    u'cst' , u'cdt' ,
    u'mst' , u'mdt' ,
    u'pst' , u'pdt' ,
    u'gmt' , u'utc'
]

Lm =  5  # minimum time length
Ln = 11  # maximum time length

class TimeTransform(simpleTransform.SimpleTransform):

    """
    to extract time as entity

    attributes:
        _hr   - hour   - int
        _m    - minute - chars
        _s    - second - chars
        _xm   - 'a' or 'p' for 'ante' or 'post' meridian
        _tz   - default time zone - chars

        _rwl  - rewritten length
    """

    def __init__ ( self ):

        """
        initialization

        arguments:
            self
        """

        super(TimeTransform,self).__init__()
        self._tz = u''

    def setZone ( self , zone ):

        """
        change default time zone

        arguments:
            self  -
            zone  - 3-char time zone
        """

        if type(zone) is str and len(zone) == 3:
            self._tz = zone

    def rewrite ( self , ts ):

        """
        check for date at current text position and rewrite if found

        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            True on any rewriting, False otherwise
        """

        lts = len(ts)
        if lts < Lm: return False

        tz = self._tz      # default

        self._xm = ''      # default

        self._m = u'00'    # defaults
        self._s = u'00'

        c = ts[0]          # first char
        if not ellyChar.isDigit(c):
            return False   # time can never start with a letter
                           # because of number transforms

        k = self._matchN(ts)
#       print 'match numeric=' , k

        if k == 0: return False

#       print 'ts[k:]=' , ts[k:]
        k += self._findAMorPM(ts[k:])
#       print 'AM or PM k=' , k

#       print 'hour=' , self._hr
        if   self._xm == 'p' and self._hr <  12: # convert to 24-hour time
            self._hr += 12
        elif self._xm == 'a' and self._hr == 12: #
            self._hr = 0
#       print 'hour=' , self._hr

        t = ts[k:]                 # remainder of text
#       print 'rest t=' , t
        dk = 0                     # skip count
        ns = 0                     # space count
        if len(t) > 0:             # look for time zone
            if t[0] == ' ':        # skip any initial space
                dk += 1
                ns = 1
#           print 't[dk:]=' , t[dk:] , 'dk=' , dk
            dk += self.get(t[dk:]) # extract next token from input
            ss = self.string       #
#           print 'zone=' , ss
            if ss in Zn:           # match to known time zone?
                tz = ss
            elif ns == 0 and ss == u'z': # military ZULU time
                tz = u'gmt'        # translate
            else:
                dk = 0             # no match

        k += dk                    # update match count
        t = t[dk:]                 # advance scan

#       print 't=' , t
        if len(t) > 0 and ellyChar.isLetterOrDigit(t[0]): return False

        for _ in range(k):         # strip matched substring to be rewritten
            ts.pop(0)

        r  = str(self._hr).zfill(2) + u':' + self._m + u':' + self._s + tz
        rr = r[::-1]
        for c in rr:               # do rewriting
            ts.insert(0,c)
        self._rwl = len(r)
        return True

    def length ( self ):

        """
        get length of rewritten date

        arguments:
            self

        returns:
            char count
        """

        return self._rwl

    def _matchN ( self , ts ):

        """
        apply logic for numeric only time recognition

        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            total number of chars matched
        """

        self._m = u'00'       # initialize defaults
        self._s = u'00'       #

        k = 1                 # count of chars already scanned
        if len(ts) < 3:       # enough chars for time expression?
            return 0          # if not, fail
        if ellyChar.isDigit(ts[k]):
            k += 1            # skip second digit

        if ts[k] != ':':      # short time expression?
            if k == 2:
                h = u''.join(ts[:k])
                if h > '12':  # check 2-digit hour
                    return 0
            else:
                h = ts[0]
                if h  == '0': # check 1-digit hour
                    return 0
            m = self._findAMorPM(ts[k:]) # AM or PM
            if m == 0:        # if none in short expression, fail
                return 0
            self._hr = int(h) # set the hour
            return k + m      # return success

        self._hr = int(u''.join(ts[:k])) # numerical hour
        if self._hr >= 24: return 0

        k += 1
        t = ts[k:]
        lt = len(t)
        if lt < 2: return 0
        c = t[0]           # should be minutes
        d = t[1]
        if not ellyChar.isDigit(c) or not ellyChar.isDigit(d): return 0
        if c > '5': return 0
        self._m = u''.join(t[:2])          # save
        t = t[2:]
        lt -= 2
        k += 2
        if lt > 2:         # should be seconds
            if t[0] == ':':
                c = t[1]
                d = t[2]
                if not ellyChar.isDigit(c) or not ellyChar.isDigit(d): return 0
                if c > '5': return 0
                if lt > 3 and ellyChar.isDigit(t[3]): return 0
                self._s = u''.join(t[1:3]) # save
                t = t[3:]
                lt -= 3
                k += 3

        if lt > 0 and ellyChar.isDigit(t[0]):
            return 0
        else:
            return k

    def _findAMorPM ( self , ts ):

        """
        look for AM or PM in time expression

        arguments:
            self  -
            ts    - char list

        returns:
            length of string match on success, 0 otherwise
        """

        k = 0                     # for match count
        lt = len(ts)              # maximum match

        if lt < 2:                # minimum number of chars for any match
            return 0
        elif ts[k] == ' ':        # skip over any leading space
            k += 1

#       print 'find AM or PM in' , ts[k:]
        x = ts[k].lower()
        if x != 'a' and x != 'p': # first char in AM or PM
            return 0
        k += 1
        if lt == k:               # end of input check
            return 0
        if ts[k] == '.':          # '.' is optional
            k += 1
        if lt == k:               # end of input check
            return 0
        y = ts[k].lower()
        if y != 'm':              # last char in AM or PM
            return 0
        k += 1
        if lt == k or not ellyChar.isLetterOrDigit(ts[k]): # check for break
            self._xm = x          # save just 'a' or 'p'
            return k              # return match count for success
        else:
            return 0              # for match failure

#
# unit test
#

if __name__ == '__main__':

    import sys

    tdat = [                # test examples
        u'4pm est' ,
        u'4:33 PM' ,
        u'4:33:01 P.M' ,
        u'4:33pm'  ,
        u'4:33am PDT'  ,
        u'11:17pm' ,
        u'22:22:22z'   ,
        u'24:24:24z'   ,
        u'12:15 AM'    ,
        u'3:45pm xxxx' ,
        u'11:66:00am'
    ]

    if len(sys.argv) > 1: # look for additional test samples as commandline arguments
        sys.argv.pop(0)
        for tme in sys.argv:
            tdat.append(tme.decode('utf8'))

    te = TimeTransform()  # instantiate time transformation object
    for xt in tdat:
        tst = list(xt)     # convert to list
        stat = te.rewrite(tst)
        print xt , '>>' , u''.join(tst) , '=' , stat
        print ''

