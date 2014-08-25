#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyWildcard.py : 25aug2014 CPM
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
for defining wildcards in text pattern matching
"""

import ellyChar
import ellyBuffer

X  = 0xE000       # start of private codes in Unicode, used for pattern syntax
Xc = unichr(X)    #   (Python 2.* only)

def isWild ( c ):

    """
    check if char is wildchar

    arguments:
        c   - character to check

    returns:
        True if wild, False otherwise
    """

#   print ' c=' , c  , '(' + str(ord(c))  + ')'
#   print 'Xc=' , Xc , '(' + str(ord(Xc)) + ')'
    return (c >= Xc)

cANY=unichr(X+1 ) # match any char
cCAN=unichr(X+2 ) # match nonalphanumeric char
cDIG=unichr(X+3 ) # match any digit
cALF=unichr(X+4 ) # match any letter
cUPR=unichr(X+5 ) # match any uppercase letter
cVWL=unichr(X+6 ) # match any vowel
cCNS=unichr(X+7 ) # match any consonant
cALL=unichr(X+8 ) # match any character sequence, including empty
cSAN=unichr(X+9 ) # match any sequence of 1 or more alphanumeric
cSDG=unichr(X+10) # match any sequence of 1 or more digits
cSAL=unichr(X+11) # match any sequence of 1 or more letters
cSOS=unichr(X+12) # start of optional sequence
cEOS=unichr(X+13) # end of optional sequence
cSPC=unichr(X+14) # match any space
cEND=unichr(X+15) # match end of token

## special pattern input characters to be interpreted as wildcards for matching

wANY=u'?'    # to match any alphanumeric character
wDIG=u'#'    # to match digit
wALF=u'@'    # to match alphabetic
wUPR=u'!'    # to match upper case alphabetic
wVWL=u'^'    # to match vowel
wCNS=u'%'    # to match consonant
wSPC=u'_'    # to match space char
wCAN=u'~'    # to match nonalphanumeric
wALL=u'*'    # to match any substring
wSPN=u'&'    # to match one or more characters of next wildcard type
wEND=u'$'    # to match end of token

## encoding of wildcards

Coding = [ wANY , wCAN , wDIG , wALF , wUPR , wVWL , wCNS , wALL ,
           wSPN + wANY , wSPN + wDIG , wSPN + wALF , u'[' , u']' ,
           wSPC , wEND ]

## associating wildcards with char type checking methods

Matching = {
    cANY : ellyChar.isLetterOrDigit ,
    cDIG : ellyChar.isDigit  ,
    cALF : ellyChar.isLetter ,
    cUPR : ellyChar.isLetter ,
    cVWL : ellyChar.isVowel  ,
    cCNS : ellyChar.isConsonant  ,
    cSPC : ellyChar.isWhiteSpace ,
    cCAN : ellyChar.isNotLetterOrDigit ,
    cALL : ellyChar.isText   ,
    cSOS : lambda x: True    ,
    cSAL : ellyChar.isLetter ,
    cSDG : ellyChar.isDigit  ,
    cSAN : ellyChar.isLetterOrDigit
}

def convert ( strg ):

    """
    convert wildcard and escaped chars in a string to coded chars

    arguments:
        strg  - the original string

    returns:
        the converted string on success, None otherwise
    """

    if strg == None: return None

    lng = len(strg)
    nlb = 0                          # check balancing of brackets
    t = [ ]                          # converted output
    i = 0
    while True:
        if i == lng: break
        wild = True                  # flag for wildcard char, True by default
        x = strg[i]
#       print "convert",i,x

        if   x == wANY:              # check for wildcard
            t.append(cANY)
        elif x == wALF:
            t.append(cALF)
        elif x == wUPR:
            t.append(cUPR)
        elif x == wDIG:
            t.append(cDIG)
        elif x == wVWL:
            t.append(cVWL)
        elif x == wCNS:
            t.append(cCNS)
        elif x == wSPC:
            t.append(cSPC)
        elif x == wEND:
            t.append(cEND)
        elif x == wALL:
            if len(t) == 0 or t[-1] != cALL:
                t.append(cALL)
        elif x == wSPN:              # check for repetition of wildcard
            if i + 1 == lng:
                t.append(x)
            else:
                i += 1
                y = strg[i]
                if   y == wANY:      # only these wildcards can be repeated
                    op = cSAN
                elif y == wDIG:
                    op = cSDG
                elif y == wALF:
                    op = cSAL
                else:
                    continue
                t.append(op)
        elif x == ellyChar.LBR:
#           print 'at \[ nlb=' , nlb
            if nlb != 0: return None
            nlb += 1
            t.append(cSOS)           # start of optional match in pattern
        elif x == ellyChar.RBR:
#           print 'at \] nlb=' , nlb
            if nlb !=  1: return None
            nlb -= 1
            t.append(cEOS)           # end   of optional match
        elif x == ellyChar.BSL:      # escape char
            if i + 1 == lng:         # nothing to escape?
                t.append(x)
            elif strg[i+1] == ' ':   # escaped space?
                t.append(ellyChar.NBS)
                i += 1
            else:                    # escaped non-space?
                z = strg[i+1]
#               print 'escaped=',z
                if ellyChar.isDigit(z):
                    t.append(x)      # if digit, preserve backslash to indicate substitution
                else:
                    t.append(z)      # otherwise, keep the next char literally
                    i += 1
        else:
            t.append(x)
            wild = False

        if wild and nlb > 0 and x != ellyChar.LBR:
#           print 'at wildcard' , x , 'nlb=' , nlb
            return None              # no wildcards allowed in optional segments
        
        i += 1

#   print "converted=", t

    return ''.join(t).lower() # converted string

def deconvert ( patn ):

    """
    ASCII representation of pattern

    arguments:
        patn  - pattern to represent

    returns:
        Unicode string representation
    """

    if (patn == None):
        return u''
    s = [ ]           # for output
    for x in patn:
        xo = ord(x)
        if xo < X:    # check for wildcard
            s.append(x)
        else:
            s.append(Coding[xo - X - 1])
    return u''.join(s)

def match ( patn , text , offs=0 , limt=None ):

    """
    compare a pattern with wildcards to input text

    arguments:
        patn  - pattern to matched
        text  - what to match against
        offs  - start text offset for matching
        limt  - limit of matching

    returns:
        bindings if match is successful, None otherwise
    """

    class Unwinding(object):

        """
        to hold unwinding information for macro pattern backup and rematch

        attributes:
            kind   - 0=optional 1=* wildcard
            count  - how many backups allowed
            pats   - saved pattern index for backup
            txts   - saved input text index
            bnds   - saved binding index
        """

        def __init__ ( self , kind ):
            """
            initialize to defaults

            arguments:
                self  -
                kind  - of winding
            """
            self.kind  = kind
            self.count = 0
            self.pats  = 0
            self.txts  = 0
            self.bnds  = 1

        def __unicode__ ( self ):
            """
            show unwinding contents for debugging

            arguments:
                self
            returns:
                attributes as array
            """                
            return ( '[kd=' + unicode(self.kind)  +
                     ',ct=' + unicode(self.count) +
                     ',pa=' + unicode(self.pats)  +
                     ',tx=' + unicode(self.txts)  +
                     ',bd=' + unicode(self.bnds)  + ']' )

    #### local variables for match( ) ####

    mbd = [ 0 ]       # stack for pattern match bindings (first usable index = 1)
    mbi = 1           # current binding index
    unw = [ ]         # stack for unwinding on match failure
    unj = 0           # current unwinding index

    ##
    # three private functions using local variables of match()
    #

    def _bind ( ns=None ):
        """
        get next available wildcard binding frame
        arguments:
            ns  - optional initial span of text for binding
        returns:
            binding frame
        """
#       print "binding:",offs,ns
        os = offs - 1
        if ns == None: ns = 1 # by default, binding is to 1 char
        if mbi == len(mbd):   # check if at end of available frames
            mbd.append([ 0 , 0 ])
        bf = mbd[mbi]         # next available record
        bf[0] = os            # set binding to range of chars
        bf[1] = os + ns       #
        return bf

    def _mark ( kind ):
        """
        set up for backing up pattern match
        arguments:
            kind  - 0=optional 1=* wildcard
        returns:
            unwinding frame
        """
        if unj == len(unw): # check if at end of available frames
            unw.append(Unwinding(kind))
        uf = unw[unj]       # next available
        uf.kind  = kind
        uf.count = 1
        uf.pats  = mp
        uf.txts  = offs
        uf.bnds  = mbi
        return uf

    def _span ( type ):
        """
        count chars available for wildcard match
        arguments:
            type - wildcard
        returns:
            non-negative count
        """
        m = mp  # start at current pattern position
        k = 0   # minimum required char count
        inOption = False

        # calculate minimum char count to match rest of pattern

#       print "pattern at=",m

        while m < ml:

            tmc = patn[m]

            if tmc == ellyChar.SPC:        # space in pattern will stop scan
                if not inOption: break
            elif ellyChar.isText(tmc):     # ordinary text char is counted
                if not inOption: k += 1
            elif tmc == cSOS:              # optional start code
                inOption = True
            elif tmc == cEOS:              # optional end   code
                inOption = False
            elif tmc == cALL:              # ALL (*) wildcard?
                pass
            elif tmc == cEND:              # END code
                pass
            else:                          # any other wildcard
                k += 1

            m += 1

#       print "exclude=",k,"@",offs

        # calculate maximum chars a wildcard can match

        mx = ellyChar.findBreak(text,offs) - k # max span reduced by exclusion
        if mx < 0: return -1                   # cannot match if max span < 0

        tfn = Matching[type]                   # char type matching a wildcard

#       print "text at",offs,"maximum wildcard match=",mx

        nm = 0
        for i in range(mx):
            c = text[offs+i]                   # next char in text from offset
            if not tfn(c): break               # stop when it fails to match 
            nm += 1

#       print "maximum wildcard span=",nm

        return nm

    #
    # end of private functions
    ##

    #############################
    ####  main matching loop ####
    #############################

    matched = False  # successful pattern match?

    if limt == None: limt = len(text)

    mp = 0           # pattern index
    ml = len(patn)   # pattern match limit

#   print text[offs:limt],":",list(patn)

    while True:

        ## literally match as many next chars as possible

        while mp < ml:
            if offs >= limt:
                last = ''
            else:
                last = text[offs].lower()
                offs += 1
            if patn[mp] != last: break
            mp += 1
            
        ## check whether mismatch is due to special pattern char
        
#       print 'pat',mp,"<",ml
#       print "txt @",offs

        if mp >= ml:        # past end of pattern?
            matched = True  # if so, match is made
            break

        tc = patn[mp]       # otherwise, get unmatched pattern element 
        mp += 1             # 
#       print "tc=",ord(tc)

        if tc == cALL:   # a * wildcard?

#           print "ALL last=< " + last + " >"
            if last != '': offs -= 1

            nm = _span(cALL)

            ## save info for restart of matching on subsequent failure

            bf = _bind(nm); mbi += 1  # get new binding record
            bf[0] = offs              # bind from current offset
            offs += nm                # move offset past end of span
            bf[1] = offs              # bind to   new     offset
#           print "offs=",offs
            uf = _mark(1); unj += 1   # get new unwinding record
            uf.count = nm             # can back up this many times on mismatch
            continue
            
        elif tc == cEND: # end specification
#           print "END $:",last
            if last == '':
                continue
            elif ellyBuffer.separators.find(last) >= 0:
                offs -= 1
                continue
            elif last in [ '.' , '?' , '.' ]:
                offs -= 1
                continue

        elif tc == cANY: # alphanumeric wildcard?
            if last != '' and ellyChar.isLetterOrDigit(last):
                _bind(); mbi += 1
                continue

        elif tc == cDIG: # digit wildcard?
            if last != '' and ellyChar.isDigit(last):
                _bind(); mbi += 1
                continue

        elif tc == cALF: # letter wildcard?
#           print "ALF:",last,offs
            if last != '' and ellyChar.isLetter(last):
                _bind(); mbi += 1
                continue

        elif tc == cSPC: # space wildcard?
#           print "SPC:"
            if last != '' and ellyChar.isWhiteSpace(last):
                continue

        elif tc == cSOS:
#           print "SOS"
#           print last,'@',offs
            mf = _bind(0); mbi += 1   # dummy record to block
            mf[0] = -1                #   later binding consolidation
            if last != '':
                offs -= 1             # try for rematch
            m = mp                    # find corresponding EOS
            while m < ml:             #
                if patn[m] == cEOS: break
                m += 1
            else:                     # no EOS?
                m -= 1                # if so, pretend there is one anyway
            uf = _mark(0); unj += 1   # for unwinding on any later match failure
            uf.pats = m + 1           # i.e. one char past next EOS
            uf.txts = offs            # start of text before optional match
            continue

        elif tc == cEOS:
#           print "EOS"
            if last != '':
                offs -= 1             # back up for rematch
            continue

        elif tc == cSAN or tc == cSDG or tc == cSAL:
            if last != '':            # still more to match?
                offs -= 1
                nm = _span(tc)        # maximum match possible
                if nm >= 1:
                    bf = _bind(nm); mbi += 1
                    bf[0] = offs      # bind from current offset
                    offs += nm        # move offset past end of span
                    bf[1] = offs      # bind to   new     offset
                    uf = _mark(1); unj += 1
                    uf.count = nm - 1 # at least one char must be matched
                    continue

        elif tc == '':
            if last == '' or not ellyChar.isPureCombining(last):
                matched = True        # successful match
                break

        ## match failure: rewind to last match branch

#       print "fail - unwinding",unj

        while unj > 0:               # try unwinding, if possible
#           print "unw:",unj
            uf = unw[unj-1]          # get most recent unwinding record
#           print uf
            if uf.count <= 0:        # if available count is used up,
                unj -= 1             # go to next unwinding record
                continue
            uf.count -= 1            # decrement available count
            uf.txts -= uf.kind       # back up one char for scanning text input
            mp = uf.pats             # unwind pattern pointer
            offs = uf.txts           # unwind text input
            mbi = uf.bnds            # restore binding
            mbd[mbi-1][1] -= uf.kind # reduce span of binding if for wildcard
            break
        else:
#           print "no unwinding"
            break                   # quit if unwinding is exhausted

    ##
    ## clean up on match mode or on no match possible
    ##

#   print "matched=",matched

    if not matched: return None     # no bindings
     
#   print text,offs

    ## consolidate contiguous bindings for subsequent substitutions

#   print "BEFORE consolidating"
#   print "bd:",len(mbd)
#   for b in mbd:
#       print b

    mbdo = mbd
    lb  = -1               # binding reference
    lbd = [ 0 , -1 ]       # sentinel value, not real binding
    mbd = [ lbd ]          # initialize with new offset after matching
    mbdo.pop(0)            # ignore empty binding
    while len(mbdo) > 0:   #
        bd = mbdo.pop(0)   # get next binding
        if bd[0] < 0:      # check for optional match indicator here
            lb = -1        # if so, drop from new consolidated bindings
        elif lb == bd[0]:  # check for binding continuous with previous
            lb = bd[1]     #
            lbd[1] = lb    # if so, combine with previous binding
        else:              #
            mbd.append(bd) # otherwise, add new binding
            lbd = bd       #
            lb = bd[1]     #

    mbd[0] = offs          # replace start of bindings with text length matched

#   print "AFTER"
#   print "bd:",len(mbd)
#   for b in mbd:
#       print b

    return mbd             # consolidated bindings plus new offset

############################ unit testing ############################

if __name__ == "__main__":

    import sys
    import ellyToken

    if len(sys.argv) < 2:
        print "usage: X pattern"
        sys.exit(0)

    print "pat=",sys.argv[1]

    pattern = convert(sys.argv[1])

    print "testing wildcard matching"
    print "enter text to match:"

    while True:
        try:
            print "> ",
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            break

        text = list(unicode(line.rstrip()))
        if len(text) == 0: break
        print "text=",text
        b = match(pattern,text,0)

        if b != None:
            n = b.pop(0)
            print n,"chars matched"
            while len(b) > 0:
                r = b.pop(0)
                print r
        else:
            print "NO MATCH!"
