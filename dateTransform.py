#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# dateTransform.py : 29oct2013 CPM
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
recognize English date references in text and normalize to 00/00/0000 form
"""
 
import ellyChar
import simpleTransform
import datetime

Mo = { # months
    'january':1, 'february':2, 'march':3     , 'april':4   , 'may':5      , 'june':6      ,
    'july':7   , 'august':8  , 'september':9 , 'october':10, 'november':11, 'december':12 ,
    'jan':1 , 'feb':2  , 'mar':3  , 'apr':4  , 'jun':6  , 'jul':7 , 'aug':8 ,
    'sep':9 , 'sept':9 , 'oct':10 , 'nov':11 , 'dec':12
}

Ep = [ # calendar epoch
    'bc' , 'bce' , 'ce' , 'ad'
]

Lm =  3  # minimum numeric date length (without year)
Ln = 10  # maximum numeric date length

class DateTransform(simpleTransform.SimpleTransform):

    """
    to extract date as entity

    attributes:
        ycur  - current year (2 digits)
        cent  - century      (2 digits)

        _mo  - month of year (2 digits)
        _dy  - day of month  (2 digits)
        _yr  - year          (4 digits)
    """

    def __init__ ( self ):

        """
        initialization

        arguments:
            self
        """

        super(DateTransform,self).__init__()
        yr = str(datetime.date.today())[:4]
        ce = yr[:2]
        self.ycur = yr[2:]
        self.cent = [ str(int(ce) - 1) , ce ]

    def rewrite ( self , ts ):

        """
        check for date at current text position and rewrite if found

        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            True on any rewriting, False otherwise
        """

        self._mo = [ '0' , '0' ]             # set defaults for return
        self._dy = [ '0' , '0' ]             #
        self._yr = [ '_' , '_' , '_' , '_' ] #

#       print 'ts=' , ts

        m            = self._matchN(ts)  # look for date patterns
        if m == 0: m = self._matchAN(ts) #

        if m <= 0: return False   # if no date matched, done

#       print 'prepop:' , m , ts

        while m > 0:              # remove matched chars from text
            ts.pop(0)             #
            m -= 1                #

        ts.insert(0,self._yr[3])  # insert normalized date instead
        ts.insert(0,self._yr[2])  #
        ts.insert(0,self._yr[1])  #
        ts.insert(0,self._yr[0])  #
        ts.insert(0,u'/')
        ts.insert(0,self._dy[1])  #
        ts.insert(0,self._dy[0])  #
        ts.insert(0,u'/')
        ts.insert(0,self._mo[1])  #
        ts.insert(0,self._mo[0])  #

        return True

    def length ( self ):

        """
        get length of rewritten date

        arguments:
            self

        returns:
            char count
        """

        return 10  # rewritten date will always be  MM/DD/YYYY

    def _matchAN ( self , ts ):

        """
        apply logic for alphanumeric date recognition

        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            total number of chars matched
        """

#       print 'ALPHANUMERIC'

        t = ts
        tl = len(ts)
        k = self._aMonth(t)            # look for month to start date string
        if k > 0:
            if k == tl: return 0
            if not ellyChar.isWhiteSpace(t[k]): return 0
            k += 1                     # skip space after month
            if k == tl: return 0
            t = t[k:]
            k = self._aDay(t)          # look for day of month
            if k == 0: return 0
            tl = len(ts)               # _aDay may have rewritten alphabetic day
            t = t[k:]
            if len(t) == 0: return 0
            if t[0] == u',': t = t[1:] # look for comma after day
            if len(t) == 0: return tl
            if ellyChar.isWhiteSpace(t[0]): t = t[1:]
            if len(t) == 0: return tl
            k = self._aYear(t)         # look for year
            return tl - len(t) + k
        else:
            k = self._aDay(t)          # look for day of month to start date string
            if k == 0 or k == tl: return 0
            tl = len(ts)               # _aDay may have rewritten alphabetic day
            t = t[k:]
#           print 'new t=' , t
            if (k > 2 and len(t) > 2 and
                t[0] == u' ' and
                t[1].upper() == 'O' and
                t[2].upper() == 'F'):
                t = t[3:]              # to handle day reference like '4th of'
            if len(t) == 0: return 0
            if not ellyChar.isWhiteSpace(t[0]): return 0
            t = t[1:]
            k = self._aMonth(t)        # look for month
            if k == 0: return 0
            t = t[k:]
            if len(t) == 0: return tl
            ntl = tl - len(t)
#           print 'ntl=' , ntl
            nd = 0
            if t[0] == u',':           # look for comma after month
                t = t[1:]
                if len(t) == 0: return tl
                nd += 1
            if ellyChar.isWhiteSpace(t[0]):
                t = t[1:]
                if len(t) == 0: return tl
                nd += 1
            k = self._aYear(t)         # look for year
            if k > 0:
                return ntl + k + nd    # full date found
            else:
                return ntl - nd        # only month and day of date found

    def _aMonth ( self , ts ):

        """
        parse a month name

        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            total number of chars matched
        """

        lss = self.get(ts)
        if not self.string in Mo: return 0
        m = Mo[self.string]

        if m > 9:
            self._mo[0] = '1'  # first digit of month
            m -= 10
        self._mo[1] = str(m)   # second

        if lss < len(ts):      # drop any period after month
            if ts[lss] == '.':
                lss += 1
        return lss

    def _aDay ( self , ts ):

        """
        parse a day number
        
        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            total number of chars matched
        """

#       print 'aDay', ts

        if len(ts) == 0:
            return 0

        k = 0              # running match count
        x = ts[0]
        if not ellyChar.isDigit(x):
            if not self.rewriteNumber(ts):
                return 0
            else:
                x = ts[0]

#       print 'ts=' , ts

        if len(ts) == 1:
            self._dy[0] = x          # accept at end of input as possible date
            return 1
        elif not ellyChar.isDigit(ts[1]):
            k = 1
        elif x > '3':                # reject first digit bigger than '3'
            return 0
        else:
            y = x                    # save first digit
            x = ts[1]                # this known to be second digit
            if y == '3' and x > '1': # reject day > 31
                return 0

            lr = len(ts) - 2         # how many chars after possible date
            if lr > 0:
                z = ts[2]
                if ellyChar.isDigit(z):
                    return 0         # reject 3-digit date
                if z == '.' and lr > 1 and ellyChar.isDigit(ts[3]):
                    return 0         # reject 2 digits before decimal point
            self._dy[0] = y
            k = 2

        self._dy[1] = x

        t = ts[k:]
        if len(t) == 0 or not ellyChar.isLetterOrDigit(t[0]):
            return k

        if ellyChar.isDigit(t[0]) or len(t) < 2:
            return 0
        sx = t[0].lower() + t[1].lower()

#       print 'x=' , x , 'sx=' , sx

        if x == '1':
            if sx != 'st': return 0
        elif x == '2':
            if sx != 'nd': return 0
        elif x == '3':
            if sx != 'rd': return 0
        else:
            if sx != 'th': return 0

        t = t[2:]
        k += 2

#       print 'k=' , k

        if len(ts) == k: # check next char in stream
            return k     # if none, match succeeds
        elif ellyChar.isLetterOrDigit(ts[k]):
            return 0     # otherwise, match fails if next char is alphanumeric
        else:
            return k     # otherwise succeed

    def _aYear ( self , ts ):

        """
        parse a year
        
        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            total number of chars matched
        """

        lts = len(ts)
        if lts < 2: return 0    # year must be at least 2 digits

        k = n = 0
        while k < lts:          # scan for digits in input list
            if not ellyChar.isDigit(ts[k]):
                break
            k += 1

        if k != 2 and k != 4:   # simple check for year range (change this as needed)
            return 0
        if k == 4 and ts[0] != '1' and ts[0] != '2':
            return 0
        self._yr[2:] = ts[k-2:] # save last 2 digits of year
        if k == 2:
            ce = self.cent[0] if ts[k-2:k] > self.ycur else self.cent[1]
            self._yr[:2] = ce
        else:
            self._yr[:2] = ts[k-4:]

        t = ts[k:]              # look for what follows year

        ns = 0
        if len(t) > 0 and t[0] == ' ':
           t = t[1:]
           ns = 1

        lss = self.get(t)
#       print 'lss=' , lss
        if self.string in Ep:
            k += lss

        return k + ns

    def _matchN ( self , ts ):

        """
        apply logic for numeric only date recognition

        arguments:
            self  -
            ts    - text stream as list of chars

        returns:
            total number of chars matched
        """

#       print 'NUMERIC'

        lts = len(ts)
        if lts < Lm: return 0  # shortest date is 0/0
        if not ellyChar.isDigit(ts[0]): return 0

        n = Ln
        if n > lts: n = lts

        ss = [ ]               # substring to compare
        ns = 0                 # slash count

#       print 'lts=' , lts , 'n=' , n

        k = 0
        while k < n:
            c = ts[k]
            if c == '/':
                ns += 1
            elif c == '-':
                ns += 1
                c = '/'
            elif not ellyChar.isDigit(c):
                break
            ss.append(c)
            k += 1

        if k < Lm: return 0
        if ns != 1 and ns != 2: return 0

#       print 'k=' , k , 'ns=' , ns , ss

        if k < lts and ellyChar.isLetterOrDigit(ts[k]):
            return 0

        dt = ''.join(ss).split('/')

        dt0 = dt.pop(0)               # get first two date components
        dt1 = dt.pop(0)               #

#       print 'split=' , dt0 , dt1

        if len(dt0) == 4 or dt0[0] == '0':
            if ns == 1: return 0      #
            dt.append(dt0)            # put first component at end if it looks like year
            dt0 = dt1                 # move month up
            dt1 = dt.pop()            # move date  up

        m = int(dt0)
        if m < 1 or m > 12: return 0  # check validity of month
        d = int(dt1)
        if d < 1 or d > 31: return 0  # check validity of day
        if ns == 2:
            y = dt.pop(0)             # if there is a year, process it also
            ly = len(y)
            if ly == 4:               # 4-digit year?
                s = y[0]
                if s != '1' and s != '2': return 0
                yls = list(y)
            elif ly == 2:
                ix = 0 if y > self.ycur else 1
                yls = list(self.cent[ix] + y)
            else:
                return 0              # fail on any other number of year digits

            self._yr = yls            # handle year

        self._mo = list(dt0.zfill(2)) # handle month
        self._dy = list(dt1.zfill(2)) # handle day
        return k

#
# unit test
#

if __name__ == '__main__':

    xs = [
        u'9/11' ,
        u'4th of July, 1776' ,
        u'September 22, 1963, was' ,
        u'June 28, 1972' ,
        u'20 January 2009.' ,
        u'20 jan 09' ,
        u'Jan 3, 1900 AD' ,
        u'4/1/2000 (' ,
        u'4/11/00' ,
        u'4/11/99' ,
        u'15TH of April, 1775' ,
        u'15th of April, 1775' ,
        u'fifteenth of April, 1775' ,
        u'april fifteenth, 1775' ,
        u'dec. 25th, 1880' ,
        u'Sep 33, 1955' ,
        u'Sept 3, 1955' ,
        u'Twelfth of Never'
    ]

    de = DateTransform()
    for x in xs:
        ts = list(x) 
        stat = de.rewrite(ts)
        print x , '>>' , ''.join(ts) , '=' , stat
        print ''
