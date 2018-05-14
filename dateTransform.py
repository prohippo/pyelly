#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# dateTransform.py : 13may2018 CPM
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
        ycur - current year  (2 digits)
        cent - century       (2 digits)

        lgth - length of rewritten date

        _mo  - month of year (2 digits)
        _dy  - day of month  (2 digits plus hyphen and 1 or 2 digits)
        _yr  - year          (4 digits)
        _ep  - epoch         (2 or 3 chars)
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
        self.lgth = 0

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
        self._dy = [ ]                       #
        self._yr = [ '_' , '_' , '_' , '_' ] #
        self._ep = [ ]                       #

        self.lgth = 0

#       print 'ts=' , ts

        m            = self._matchN(ts)  # look for date patterns
        if m == 0: m = self._matchAN(ts) #

        if m <= 0: return False   # if no date matched, done

#       print 'prepop:' , m , ts

        while m > 0:              # remove matched chars from text
            ts.pop(0)             #
            m -= 1                #
                                  # insert normalized date instead
        ep = self._ep             #
        self.lgth = len(ep)       #
        while len(ep) > 0:        #
            ts.insert(0,ep.pop()) # add epoch of date, if specified
        ts.insert(0,self._yr[3])  # add year of date
        ts.insert(0,self._yr[2])  #
        self.lgth += 2            #
        if self._yr[1] != '_':    #
            ts.insert(0,self._yr[1])  # add 2 chars if not '_'
            ts.insert(0,self._yr[0])  #
            self.lgth += 2            #

#       print 'date lgth=' , self.lgth
        if self._mo[0] == '0' and self._mo[1] == '0': return True

        ts.insert(0,u'/')         #
        dy = self._dy             #
        ld = len(dy)              #
        if ld > 0:                # add day of date
            while len(dy) > 0:    #
                ts.insert(0,dy.pop()) #
            ts.insert(0,u'/')         #
            self.lgth += 1            # includes prior '/'
        ts.insert(0,self._mo[1])  # add month of date
        ts.insert(0,self._mo[0])  #
        self.lgth += ld + 3       # includes another '/'

#       print 'date lgth=' , self.lgth
        return True

    def length ( self ):

        """
        get length of rewritten date

        arguments:
            self

        returns:
            char count
        """

        return self.lgth

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
        comma = False
#       print 'month len=' , k
        if k > 0:
            if k == tl: return 0
            if not ellyChar.isWhiteSpace(t[k]): return 0
            k += 1                     # skip space after month
            if k == tl: return 0
            t = t[k:]
            k = self._aDay(t)          # look for day of month
#           print 'day len=' , k
            if k == 0:
                self._dy = [ ]
                k = self._aYear(t)     # look for year immediately following
                if k > 0:
                    return tl - len(t) + k
                else:
                    return 0
#           print 'ts=' , ts
            tl = len(t)                # _aDay may have rewritten alphabetic day
            t = t[k:]
            if len(t) == 0:
#               print 'no year tl=' , tl , 'k=' , k , t
                return len(ts) - tl + k
            if t[0] == u',':           # look for comma after day
                t = t[1:]             # if found, remove and note
                comma = True
            if len(t) == 0: return tl
            if ellyChar.isWhiteSpace(t[0]): t = t[1:]
            if len(t) == 0: return tl
            k = self._aYear(t)         # look for year
#           print 'year len=' , k
            lnt = len(t)
            if comma and k < lnt and t[k] == ',':
                k += 1                 # remove comma after year if paired
#           print 'len(ts)=' , len(ts) , 'len(t)=' , len(t) , t
            return len(ts) - len(t) + k

        k = self._aDay(t)              # look for day of month to start date string
#       print 'start day len=' , k
        if k == 0:
            self._dy = [ ]
        elif k > 0 and k < tl:         # cannot be just bare number by itself
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
                comma = True
            if ellyChar.isWhiteSpace(t[0]):
                t = t[1:]
                if len(t) == 0: return tl
                nd += 1
            k = self._aYear(t)         # look for year
            if k > 0:
                if comma and k < len(t) and t[k] == ',': k += 1
                return ntl + k + nd    # full date found
            else:
                return ntl - nd        # only month and day of date found

#       print 'look for year only in' , t
        k = self._aYear(t)
        if k > 0:
            if k == tl:
                return k
            elif not ellyChar.isLetter(t[k]) and t[k] != '-':
                return k

        return 0                       # nothing found


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
        y = ''
        if not ellyChar.isDigit(x):
            if not self.rewriteNumber(ts):
                return 0
            else:
                x = ts[0]

#       print 'rewritten ts=' , ts

        ls = len(ts)
        if ls == 1:
            if x == '0': return 0    # cannot have 0 as day
            self._dy.append(x)       # accept at end of input as possible date
            return 1
        elif not ellyChar.isDigit(ts[1]):
            k = 1
        elif x > '3':                # reject first digit bigger than '3'
            return 0
        else:
            y = x                    # save first digit
            x = ts[1]                # this will be second digit
            if y == '3' and x > '1': # reject day > 31
                return 0
            k = 2

        ls -= k
        if k == 2:
            self._dy.append(y)
        self._dy.append(x)
        if ls == 0:
            return k

        z = ts[k]
        if ellyChar.isDigit(z):
            return 0         # reject 3-digit day

        if z == '.' and ls > 1 and ellyChar.isDigit(ts[k+1]):
            return 0         # reject digit after decimal point

        if ls >= 2:          # at least 2 chars to check after day number
            if z == u'-':
#               print 'hypen ls=' , ls , 'k=' , k
                if ellyChar.isDigit(ts[k+1]):                     # hyphen, digit match
#                   print 'digit=' , ts[k+1]
                    self._dy.append(z)
                    self._dy.append(ts[k+1])
                    if ls == 2:                                   # only 2 chars to check?
                        k += 2                                    # add hyphen, digit to day
                    elif ls == 3:                                 # only 3 chars to check?
#                       print 'ts[k]=' , ts[k:]
                        if not ellyChar.isLetterOrDigit(ts[k+2]): #
                            k += 2                                # add hyphen, digit to day
                        elif ellyChar.isDigit(ts[k+2]):           # found second digit to add?
                            self._dy.append(ts[k+2])              # if so, add to day string
                            k += 3
                    elif not ellyChar.isLetterOrDigit(ts[k+2]):   # more than 3 chars to check?
                        k += 2                                    # if not, we are done
                    elif ellyChar.isDigit(ts[k+2]):               # check for second digit
#                       print 'k=' , k
                        if ls > 3 and ellyChar.isDigit(ts[k+3]):
                            return 0
                        if ts[k+1] > '3':                         # check for valid day
                            return 0
                        if ts[k+1] == '3' and ts[k+2] > '1':
                            return 0
                        self._dy.append(ts[k+2])
                        k += 3
                    else:
                        return 0                                  # no other hyphen allowed in day
                else:
                    return 0                                      #

        t = ts[k:]
#       print 'k=' , k , 't=' , t
        if len(t) == 0 or not ellyChar.isLetterOrDigit(t[0]):
            return k

        if ellyChar.isDigit(t[0]) or len(t) < 2:
            return 0
        sx = t[0].lower() + t[1].lower()

#       print 'y=' , y , 'x=' , x , 'sx=' , sx

        if x == '1':
#           print 'end of day=' , y
            if y == '1':
                if sx != 'th': return 0
            elif sx != 'st':   return 0
        elif x == '2':
            if sx != 'nd': return 0
        elif x == '3':
            if sx != 'rd': return 0
        else:
#           print 'default ordinal indicator'
            if sx != 'th': return 0

#       print 'ord k=' , k
        t = t[2:]
        k += 2

#       print 'k=' , k , 'len=' , len(ts)

        if len(ts) == k: # check next char in stream
            return k     # if none, match succeeds
        elif ellyChar.isLetterOrDigit(ts[k]):
#           print 'ts[k]=' , ts[k] , k
            return 0     # otherwise, match fails if next char is alphanumeric
        else:
#           print 'return k=' , k
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

        k = 0
        while k < lts:          # scan for digits in input list
            if not ellyChar.isDigit(ts[k]):
                break
            k += 1

#       print k , 'digits scanned'
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
#       print 'epoch t=' , t

        ns = 0
        if len(t) > 0 and t[0] == ' ':
            t = t[1:]
            ns = 1

        lss = self.get(t)
#       print 'lss=' , lss , self.string
        if self.string in Ep:
            self._ep = list(self.string)
            k += ns + lss
#           print 'k=' , k , 'ns=' , ns
        elif k < 4:
            return 0

#       print 'k=' , k
        return k if k > 3 else 0

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

#       print 'k=', k , 'Lm=' , Lm , 'ns=' , ns
        if k < Lm: return 0
        if ns != 1 and ns != 2: return 0

#       print 'ss=' , ss

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
        if dt1 == '': return 0
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


    xxxx = [
    ]
    tdat = [
        u'September 11th' ,
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
        u'15th of April, 1775,' ,
        u'fifteenth of April, 1775' ,
        u'april fifteenth, 1775' ,
        u'dec. 25th, 1880' ,
        u'Sep 33, 1955' ,
        u'Sept 3, 1955' ,
        u'Sept 3, 1955,' ,
        u'May 1941' ,
        u'December 1949' ,
        u'Twelfth of Never' ,
        u'Feb. 7-8' ,
        u'May 15-17th' ,
        u'MAY 15-37th' ,
        u'1000 BC' ,
        u'1234 x' ,
        u'123 x' ,
        u'2016'
    ]
    yyyy = [
    ]

    de = DateTransform()
    for xd in tdat:
        tst = list(xd)
        stat = de.rewrite(tst)
        print xd , '-->>' , ''.join(tst) , '=' , stat

    print "----------------"
    print ""

    import sys

    while True:
        print '> ' ,
        st = sys.stdin.readline().strip()
        if len(st) <= 0: break
        tst = list(st.strip())
        stat = de.rewrite(tst)
        print st , '-->>' , ''.join(tst) , '=' , stat
        print ''
