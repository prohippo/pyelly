#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# phondexEN.py : 20mar2015 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2015, Clinton Prentiss Mah
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
Python extended version of Name Trace phondex.c and transf.c for phonetic
analysis of names according to American English spelling
"""

# phonetic transforms for English spelling and pronunciation

_xfs = [
 { } ,
 { "x":"ks" , "'":"h"
 } ,
 { "ch":"j"  , "ce":"se" , "ci":"si" , "ck":"k"   , "ct":"kt"  ,
   "cy":"sy" , "ge":"je" , "gg":"k"  , "gh":"g"   , "gi":"ji"  ,
   "ia":"Ya" , "io":"Yo" , "iu":"Yu" , "kn":"n"   , "ph":"f"   ,
   "qu":"kW" , "sh":"j"  , "th":"t"  , "ua":"Wa"  , "uo":"Wo"  ,
   "wh":"W"  , "wy":"Y"  , "xc":"ks" , "xe":"kze" , "xi":"kzi" , "yw":"W"  ,
   "ha":"Ha" , "he":"He" , "hi":"Hi" , "ho":"Ho"  , "hu":"Hu"  , "hy":"Hy" ,
   "ua":"Wa" , "uo":"Wo" , "wa":"Wa" , "we":"We"  , "wi":"Wi"  , "wo":"Wo" ,
   "wu":"Wu" , "ya":"Ya" , "ye":"Ye" , "yi":"Yi"  , "yo":"Yo"  , "yu":"Yu"
 } ,
 { "asa":"aza" , "ase":"aze" , "asi":"azi" , "asu":"aju" , "chr":"kr"  ,
   "cia":"ja"  , "cio":"jo"  , "ciu":"ju"  , "cti":"kji" , "ctu":"kjw" ,
   "dge":"je"  , "dua":"jWa" , "ese":"eze" , "esi":"ezi" , "esu":"ezu" ,
   "ght":"t"   , "ien":"Yn"  , "iet":"Yt"  , "iex":"YKs" , "igh":"i"   ,
   "igl":"il"  , "ign":"in"  , "ise":"ize" , "isi":"izi" , "iso":"izo" ,
   "nio":"nYo" , "nyo":"nYo" , "ose":"oze" , "osi":"ozi" , "que":"ke"  ,
   "qui":"qWi" , "sch":"j"   , "tch":"j"   , "tia":"ja"  , "tio":"jo"  ,
   "wyn":"Wn" 
 } ,
 { "euph":"Yf"  , "iect":"YKt" , "quee":"kWe" , "quel":"kWl" ,
   "quen":"kWn" , "ssia":"ja"  , "ssio":"jo"  , "stle":"sle" ,
   "sura":"jra" , "sure":"jre" , "tura":"jra" , "ture":"jre" ,
   "uiti":"Wji" , "uity":"Wty"
 } ,
 { "ssure":"jre"
 }
]

def _xf ( strg ):

    """
    rewrite input string for phonetic encoding

    arguments:
        strg  - ASCII string

    returns:
        rewritten string
    """

    ol = [ ]                        # output list
    ln = len(strg)
    if ln >= 2:                     # handle special case of string
        if strg[:2] == 'mc':        # starting with MC
            strg = strg[2:]
            ol.append('mk')         # C is hard
            ln -= 2
        if ln >= 3:
            if strg[:3] == 'wya':   # starting with WY
                strg = strg[3:]
                ol.append('WY')     # Y is semi-consonant here
                ln -= 3
            if strg[:2] == 'eu':    # starting with EUT or EUR or EUP or EUG
                chx = strg[2]
#               print 'chx=' , chx
                if chx in [ 't' , 's' , 'r' , 'g' ]:
                    if chx == 'g': chx = 'j'
                    strg = strg[3:]
                    ol.append('Y')  # EU is semi-consonant
                    ol.append(chx)
                    ln -= 3

#   print 'encoding ln=' , ln
    while ln > 0:                   # process rest of string
        nch = 5 if ln > 5 else ln   # try longest transforms first
#       print 'start nch=' , nch
        while nch > 0:
            sstrg = strg[:nch]
            h = _xfs[nch]           # transforms of nch chars
            if sstrg in h:
#               print sstrg , '->' , h[sstrg]
                ol.append(h[sstrg]) # result of transform to output list
                strg = strg[nch:]   # move to next position in input string
                ln -= nch
                break
            nch -= 1                # if no match, try shorter transforms
#       print 'ln=' , ln , 'nch=' , nch , 'strg=' , strg
        if nch == 0 and ln > 0:     # if no matches
            ol.append(strg[0])      #   move single char to output list
            strg = strg[1:]         #
            ln -= 1

    return ''.join(ol)              # get single string from output list

# default phonetic encoding of consonants

phonCOD = {
    'b':'P' , 'c':'K' , 'd':'T' , 'f':'P' , 'g':'K' , 'j':'S' ,
    'k':'K' , 'l':'L' , 'm':'M' , 'n':'M' , 'p':'P' , 'q':'K' ,
    'r':'R' , 's':'S' , 't':'T' , 'v':'P' , 'x':'S' , 'z':'S' ,
    'H':'H' , 'W':'W' , 'Y':'Y'  # note upper case keys!
}

def phondex ( token ):

    """
    calculate a Soundex-like classification of consonants
    with encoding also of initial vowels and distinguishing
    hard and soft C and G.

    arguments:
        token  - list of ASCII characters

    returns:
        string for phonetic representation of token
    """

#   print 'token=' , token
    ltoken = len(token)
    if ltoken == 0: return ''

    strg = _xf(''.join(token).lower())
#   print 'transformed strg=' , strg

    rslt = [ ]
    lpho = ''
    chx = strg[0]
    if chx in [ 'a' , 'e' , 'i' , 'o' , 'u' ]:
        rslt.append('a')
    for chx in strg:
#       print 'chx=' , chx
        if not chx in phonCOD:
            lpho = ''
        else:
#           print 'lpho=' , lpho 
            if lpho != phonCOD[chx]:
                lpho = phonCOD[chx]
                rslt.append(lpho)

    return ''.join(rslt)

#
# unit test
#

if __name__ == '__main__':

    import sys

    while True: # test examples from standard input

        sys.stdout.write('> ')
        tos = sys.stdin.readline().decode('utf8').strip()
        if len(tos) == 0: break
        phontos = phondex(list(tos))
        print tos , '->' , phontos
