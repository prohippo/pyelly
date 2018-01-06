#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# extractionProcedure.py : 05jan2018 CPM
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
standard Elly entity extraction procedures

use also as model for methods to handle other kinds of entities, which may be
defined in other source files (modules)
"""

import ellyChar
import dateTransform
import timeTransform

dT = dateTransform.DateTransform()
tT = timeTransform.TimeTransform()

def date ( buffr ):

    """
    recognize date expressions in text

    arguments:
        buffr - current contents as list of chars

    returns:
        char count matched on success, 0 otherwise
    """

    if dT.rewrite(buffr):
        return dT.length()
    else:
        return 0  # just a stub

def time ( buffr ):

    """
    recognize time expressions in text

    arguments:
        buffr - current contents as list of chars

    returns:
        char count matched on success, 0 otherwise
    """

    if tT.rewrite(buffr):
        return tT.length()
    else:
        return 0  # just a stub

# state abbreviations and starting digits for zipcodes

ziprs = {
    'AK':'99', 'AL': '3', 'AR':  '7', 'AZ': '8', 'CA': '9',
    'CO': '8', 'CT':'06', 'DC':'200', 'DE':'19', 'FL': '3',
    'GA': '3', 'HI':'96', 'IA':  '5', 'ID':'83', 'IL': '6',
    'IN': '4', 'KS':'66', 'KY':  '4', 'LA': '7', 'MA': '0',
    'MD': '2', 'ME': '0', 'MI':  '4', 'MN': '5', 'MO': '6',
    'MS': '3', 'MT':'59', 'NB':  '6', 'NC': '2', 'ND':'58',
    'NH':'03', 'NJ': '0', 'NM':  '8', 'NV': '8', 'NY': '1',
    'OH': '4', 'OK': '7', 'OR': '97', 'PA': '1', 'RI':'02',
    'SC':'29', 'SD':'57', 'TN':  '3', 'TX': '7', 'UT':'84',
    'VA': '2', 'VT':'05', 'WA':  '9', 'WI': '5', 'WV': '2', 'WY': '8'
}

def stateZip ( buffr ):

    """
    recognize U.S. state abbreviation and zip code

    arguments:
        buffr - current contents as list of chars

    returns:
        char count matched on success, 0 otherwise
    """

    if len(buffr) < 8 or buffr[2] != ' ': return 0
    st = ''.join(buffr[:2]).upper()    # expected 2-char state abbreviation
    if not st in ziprs: return 0       # if not known, quit
    zc = ziprs[st]                     # get zip-code start
    b = buffr[3:]                      # expected start of zipcode
    i = 0
    for c in zc:                       # check starting digits of zipcode
        if c != b[i]: return 0
        i += 1
    while i < 5:                       # check for digits in rest of zipcode
        if not ellyChar.isDigit(b[i]): return 0
        i += 1
    b = b[5:]                          # look for proper termination
    if len(b) == 0:                    # if end of input, success
        return 8                       # success: 5-digit zip
    c = b[0]
    if ellyChar.isLetterOrDigit(c):    # if next char is alphanumeric, failure
        return 0
    elif b[0] == '-':                  # look for possible 9-digit zip
        if len(b) > 5:
            b = b[1:]
            for i in range(4):
                if not ellyChar.isDigit(b[i]): return 0 # check for 4 more digits
            b = b[4:]                                   # past end of 4 digits
            if len(b) > 0 and ellyChar.isLetterOrDigit(b[0]): return 0 # termination check
            return 8 + 5                                # success: 9-digit zip
    else:
        return 8                       # success: 5-digit zip

Lmin = 4
Lmax = 8

def acronym ( buffr ):

    """
    recognize parenthesized introduction of acronym in text

    arguments:
        buffr - current contents as list of chars

    returns:
        char count matched on success, 0 otherwise
    """

    lb = len(buffr)
    if lb > Lmax: lb = Lmax
    if lb < Lmin or buffr[0] != '(': return 0

    nu = 0          # uppercase count
    ib = 1
    while ib < lb:
        bc = buffr[ib]
        ib += 1
        if bc == ')':
            break
        if not ellyChar.isLetter(bc): return 0
        if ellyChar.isUpperCaseLetter(bc): nu += 1
    else:
        return 0    # must have enclosing ')'

    if ib < Lmin or ib - 2*nu > 0: return 0
    if len(buffr) > ib and ellyChar.isLetterOrDigit(buffr[ib]): return 0

    return ib

Tmin = 10
Tmax = 44
lDQ = ellyChar.LDQm
rDQ = ellyChar.RDQm
aDQ = '"'

def title ( buffr ):

    """
    recognize double-quoted title in text

    arguments:
        buffr - current contents as list of chars

    returns:
        char count matched on success, 0 otherwise
    """

    lb = len(buffr)
    if lb > Tmax: lb = Tmax
    if lb < Tmin: return 0
    qm = buffr[0]
    if qm != aDQ and qm != lDQ: return 0

    ib = 1
    while ib < lb:
        bc = buffr[ib]
        ib += 1
        if bc == rDQ:
            break
        if not ellyChar.isUpperCaseLetter(bc): return 0

        while ib < lb:
            bc = buffr[ib]
            ib += 1
            if bc == ' ': break
            if qm == aDQ:
                if bc == aDQ: break
            else:
                if bc == rDQ: break
            if bc in [ '!' , '?' ]:
                return 0
        if bc == rDQ or bc == aDQ: break
    else:
        return 0    # must have enclosing rDQ or aDQ

    if ib < Tmin: return 0
    if len(buffr) > ib and ellyChar.isLetterOrDigit(buffr[ib]): return 0

    return ib

####
#### look for time period reference

_modifier = [
    'early' , 'late'
]

_day = [
    'sunday' , 'monday' , 'tuesday' , 'wednesday' , 'thursday' , 'friday' , 'saturday' ,
    'christmas' , 'easter'
]

_period = [
    'morning' , 'noon' , 'afternoon' , 'evening' , 'night'
]

def _scan ( buffr ):
    """
    count chars to first non-alphabetic char
    arguments:
        buffr - list of chars
    returns:
        number of letters
    """
    n = 0
    ln = len(buffr)
    while n < ln:
        if not ellyChar.isLetter(buffr[n]):
            break
        n += 1
    return n

def timePeriod ( buffr ):

    """
    recognize time period in a day

    arguments:
        buffr - current contents as list of chars

    returns:
        char count matched on success, 0 otherwise
    """

#   print 'buffr=' , buffr
    ln = len(buffr)
    if ln == 0 or not ellyChar.isLetter(buffr[0]):
        return 0
    k = _scan(buffr)
#   print '0 k=' , k
    if k == ln or buffr[k] != ' ':
        return 0
    a = u''.join(buffr[:k]).lower()
#   print 'a=' , a
    if a in _modifier:
        n = k + 1
        buffr = buffr[n:]
    else:
        n = 0
    k = _scan(buffr)
#   print '1 k=' , k
    if k < 6:
        return 0
    b = u''.join(buffr[:k]).lower()
    if not b in _day:
        return 0
    buffr = buffr[k:]
    n += k
    if len(buffr) < 5 or buffr[0] != ' ':
        return n if n > k else 0
    m = _scan(buffr[1:])
#   print '2 m=' , m
    c = u''.join(buffr[1:m+1]).lower()
    if c in _period:
        return n + m + 1
    else:
        return n if n > k else 0

#
# unit test
#

if __name__ == '__main__':

    import sys

    so = sys.stdout
    si = sys.stdin

    while True:  # translate successive lines of text as sentences for testing

        so.write('> ')
        line = si.readline()
        l = line.decode('utf8')
        if len(l) == 0 or l[0] == '\n': break
        txt = list(l.strip())
        so.write('\n')
        nc = acronym(txt)
        so.write(str(nc) + ' char(s) matched for acronym')
        so.write('\n')
        nc = title(txt)
        so.write(str(nc) + ' char(s) matched for title')
        so.write('\n')
        nc = timePeriod(txt)
        so.write(str(nc) + ' char(s) matched for timePeriod')
        so.write('\n')

    so.write('\n')
