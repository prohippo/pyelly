#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# extractionProcedure.py : 05nov2014 CPM
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
