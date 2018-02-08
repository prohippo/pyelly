#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyWildcard.py : 06feb2018 CPM
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
for defining wildcards and semi-wildcards in text pattern matching
"""

import ellyChar
import ellyBuffer

X  = 0xE000       # start of private codes in Unicode, used for encoded pattern elements
Xc = unichr(X)    #   (Python 2.* only)

Enc = [ u')' , u']' , ellyChar.RSQm , ellyChar.RDQm ]

def isWild ( c ):

    """
    check if char is PyElly wildcard

    arguments:
        c   - character to check

    returns:
        True if wild, False otherwise
    """

#   print ' c=' , c  , '(' + str(ord(c))  + ')'
#   print 'Xc=' , Xc , '(' + str(ord(Xc)) + ')'
    return Xc < c and c <= cEND

def isSemiWild ( c ):

    """
    check if char is PyElly lowercase letter in a pattern--
    this is semiwild in that it will match both upper and lowercase,
    but is NOT encoded

    arguments:
        c   - character to check

    returns:
        True if semiwild, False otherwise
    """

    return ellyChar.isLowerCaseLetter(c)

cANY = unichr(X+1 ) # match any char
cCAN = unichr(X+2 ) # match nonalphanumeric char
cDIG = unichr(X+3 ) # match any digit
cALF = unichr(X+4 ) # match any letter
cUPR = unichr(X+5 ) # match any uppercase letter
cLWR = unichr(X+6 ) # match any lowercase letter
cVWL = unichr(X+7 ) # match any vowel
cCNS = unichr(X+8 ) # match any consonant
cALL = unichr(X+9 ) # match any character sequence without spaces, including empty
cSAN = unichr(X+10) # match any sequence of 1 or more alphanumeric
cSDG = unichr(X+11) # match any sequence of 1 or more digits
cSAL = unichr(X+12) # match any sequence of 1 or more letters
cSOS = unichr(X+13) # start of optional sequence
cEOS = unichr(X+14) # end of optional sequence
cSPC = unichr(X+15) # match any space
cAPO = unichr(X+16) # match any apostrophe
cEND = unichr(X+17) # match end of token (must be highest wildcard code)

def isNonSimpleMatch ( c ):

    """
    can pattern char match 0 or more than 1 char?

    arguments:
        c - pattern char

    returns:
        False if pattern char always matches one text char,
        True otherwise
    """

    if c in [ cALL , cSAN , cSDG , cSOS , cEOS , cEND ]:
        return True
    else:
        return False


Separate = [ cSPC , cAPO ] # must each be in a separate match binding for wildcards

## special pattern input characters to be interpreted as wildcards for matching

RSQm = ellyChar.RSQm  # right single quote
RDQm = ellyChar.RDQm  # right double quote
PRME = ellyChar.PRME  # prime
LCWc = u'\u00A1'      # inverted exclamation mark

wANY = u'?'    # to match any alphanumeric character
wDIG = u'#'    # to match digit
wALF = u'@'    # to match alphabetic
wUPR = u'!'    # to match uppercase alphabetic
wLWR = LCWc    # to match lowercase alphabetic
wVWL = u'^'    # to match vowel
wCNS = u'%'    # to match consonant
wSPC = u'_'    # to match space char
wCAN = u'~'    # to match nonalphanumeric
wALL = u'*'    # to match any substring with no spaces
wSPN = u'&'    # to match one or more characters of next wildcard type
wAPO = RSQm    # to match any apostrophe
wEND = u'$'    # to match end of token

## encoding of wildcards

Coding = [ wANY , wCAN , wDIG , wALF , wUPR , wLWR , wVWL , wCNS , wALL ,
           wSPN + wANY , wSPN + wDIG , wSPN + wALF , u'[' , u']' ,
           wSPC , wAPO , wEND ]

## associating wildcards with char type checking methods

Matching = {
    cANY : ellyChar.isLetterOrDigit ,
    cDIG : ellyChar.isDigit  ,
    cALF : ellyChar.isLetter ,
    cUPR : ellyChar.isUpperCaseLetter ,
    cLWR : ellyChar.isLowerCaseLetter ,
    cVWL : ellyChar.isVowel  ,
    cCNS : ellyChar.isConsonant  ,
    cSPC : ellyChar.isWhiteSpace ,
    cCAN : ellyChar.isNotLetterOrDigit ,
    cALL : ellyChar.isText   ,
    cSOS : lambda x: True    ,
    cSAL : ellyChar.isLetter ,
    cSDG : ellyChar.isDigit  ,
    cAPO : ellyChar.isApostrophe ,
    cSAN : ellyChar.isLetterOrDigit
}

def convert ( strg ):

    """
    convert wildcard and escaped chars in a string to coded chars

    arguments:
        strg  - the original string or list of chars

    returns:
       list of converted Unicode chars on success, None otherwise
    """

    if strg == None: return None
#   print 'strg=' , strg

    lng = len(strg)
    nlb = 0                          # check balancing of brackets
    t = [ ]                          # converted output
    i = 0
    while True:
#       print 'loop nlb=' , nlb
        if i == lng: break
        wild = True                  # flag for wildcard char, True by default
        x = strg[i]
#       print "convert",i,x

        if   x == wANY:              # check for wildcard
            t.append(cANY)
        elif x == wCAN:
            t.append(cCAN)
        elif x == wALF:
            t.append(cALF)
        elif x == wUPR:
            t.append(cUPR)
        elif x == wLWR:
            t.append(cLWR)
        elif x == wDIG:
            t.append(cDIG)
        elif x == wVWL:
            t.append(cVWL)
        elif x == wCNS:
            t.append(cCNS)
        elif x == wSPC:
            t.append(cSPC)
        elif x == wAPO:
            t.append(cAPO)
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
#           print 'escaping'
            if i + 1 == lng:         # nothing to escape?
                t.append(x)
            elif strg[i+1] == ' ':   # escaped space?
                t.append(ellyChar.NBS)
                i += 1
            else:                    # escaped non-space?
                z = strg[i+1]
#               print 'escaped=',z,'@',i
                t.append(z)      # otherwise, keep the next char as lower case
#               print 'slash t=',list(t)
                i += 1
        else:
            t.append(x)
            wild = False

        if wild and nlb > 0 and x != ellyChar.LBR and x != ellyChar.USC:
#           print 'at wildcard' , x , 'nlb=' , nlb
            return None              # no wildcards except _ allowed in optional segments

        i += 1

#   print "converted=", list(t)

    return t                         # converted pattern to match against

toEscape = [ # chars that could be wildcards plus backslash itself
    RSQm, RDQm, PRME, u'\\',
    wANY, wDIG, wALF, wUPR, wLWR, wVWL, wCNS,
    wSPC, wCAN, wALL, wSPN, wAPO, wEND
]

def deconvert ( patl ):

    """
    ASCII representation of pattern

    arguments:
        patl  - pattern to represent

    returns:
        Unicode string representation
    """

    if patl == None:
        return u''
    s = [ ]           # for output
    for x in patl:
        xo = ord(x)
        if xo < X:    # check for non-wildcard
            if x in toEscape:
                s.append('\\' + x)
            else:
                s.append(x)
        else:         # convert wildcard
            s.append(Coding[xo - X - 1])
    return u' '.join(s)

def numSpaces ( seg , cnv=False ):

    """
    check for space chars and wildcards,
    optionally converting chars to wildcards

    arguments:
        seg  - text segment as list
        cnv  - flag for wildcard conversion

    returns:
        number of space chars and wildcards
    """

    nsp = 0
    if seg == '': return 0
    ls = len(seg)
    for i in range(ls):
        c = seg[i]
        if ellyChar.isSpace(c):
            if cnv:
                seg[i] = cSPC
            nsp += 1
        elif c == cSPC:
            nsp += 1
    return nsp

def minMatch ( patn ):

    """
    compute minimum number of chars matched by pattern

    arguments:
        patn  - pattern with possible Elly wildcards

    returns:
        minimum count of chars matched
    """

    inOption = False

    k = 0
    m = 0
    ml = len(patn)

    while m < ml:

        tmc = patn[m]

        if tmc == ellyChar.SPC:        # space in pattern will stop scan
            if not inOption: break
        elif ellyChar.isText(tmc):     # ordinary text char is counted
            if not inOption: k += 1
        elif tmc == cSOS:              # optional start code
#           print "START optional match" , inOption
            inOption = True
        elif tmc == cEOS:              # optional end   code
#           print "END optional match" , inOption
            inOption = False
        elif tmc == cALL:              # ALL (*) wildcard?
            pass
        elif tmc == cEND:              # END code
            pass
        else:                          # any other wildcard
#           print "count up wildcard minimum match"
            k += 1

        m += 1

    return k

Trmls = [ RDQm , u'"' , RSQm , u"'" , u'.' , u')' , u']' ]  # chars marking extent of pattern match

def match ( patn , text , offs=0 , limt=None , nsps=0 ):

    """
    compare a pattern with wildcards to input text

    arguments:
        patn  - pattern to matched
        text  - what to match against
        offs  - start text offset for matching
        limt  - limit of matching
        nsps  - number of spaces to match in pattern

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
            nsps   - saved count of spaces matched
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
            self.nsps  = 0

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
                     ',bd=' + unicode(self.bnds)  +
                     ',ns=' + unicode(self.nsps)  + ']' )

    #### local variables for match( ) ####

    mbd = [ 0 ]       # stack for pattern match bindings (first usable index = 1)
    mbi = 1           # current binding index
    unw = [ ]         # stack for unwinding on match failure
    unj = 0           # current unwinding index

    ##
    # four private functions using local variables of match() defined just above
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

    def _modify ( ):
        """
        set special tag for binding
        arguments:

        """
        mbd[mbi].append(None)

    def _mark ( kind , nsp=0 ):
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
        uf.nsps  = nsp
        return uf

    def _span ( typw , nsp=0 ):
        """
        count chars available for wildcard match
        arguments:
            typw - wildcard
            nsp  - spaces to be matched in pattern
        returns:
            non-negative count if any match possible, otherwise -1
        """
#       print "_span: typw=" , '{:04x}'.format(ord(typw)) , deconvert(typw)
#       print "_span: txt @",offs,"pat @",mp,"nsp=",nsp
#       print "text to span:",text[offs:]
#       print "pat rest=" , patn[mp:]
        k = minMatch(patn[mp:])                # calculate min char count to match rest of pattern

#       print "exclude=",k,"chars from possible span for rest of pattern"

        # calculate maximum chars a wildcard can match

        mx = ellyChar.findExtendedBreak(text,offs,nsp)
#       print mx,"chars available to scan"
        mx -= k                                # max span reduced by exclusion
        if mx < 0: return -1                   # cannot match if max span < 0

        tfn = Matching[typw]                   # char type matching a wildcard

#       print "text at",offs,"maximum wildcard match=",mx

        nm = 0
        for i in range(mx):
            c = text[offs+i]                   # next char in text from offset
#           print 'span c=' , c
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

    matched = False  # successful pattern match yet?

    if limt == None: limt = len(text)

#   print 'starting match, limt=',limt,text[offs:limt],":",patn
#   print 'nsps=' , nsps

    mp = 0           # pattern index
    ml = len(patn)   # pattern match limit
    last = ''

    while True:

        ## literally match as many next chars as possible

#       print 'loop mp=' , mp , 'ml=' , ml
        while mp < ml:
            if offs >= limt:
#               print "offs=",offs,"limt=",limt
                last = ''
            else:
                last = text[offs]
                offs += 1
#           print 'patn=' , patn
            mc = patn[mp]
#           print 'matching last=' , last, '(' , '{:04x}'.format(ord(last)) if last != '' else '-', ') at' , offs
#           print 'against       ' , mc  , '(' , '{:04x}'.format(ord(mc)) , ')'
            if mc != last:
                if mc != last.lower(): break
#           print 'matched @mp=' , mp
            mp += 1

        ## check whether mismatch is due to special pattern char

#       print 'pat @',mp,"<",ml
#       print "txt @",offs,'<',limt,'last=',last
#       print '@',offs,text[offs:]

        if mp >= ml:        # past end of pattern?
            matched = True  # if so, match is made
            break

        tc = patn[mp]       # otherwise, get unmatched pattern element
        mp += 1             #
#       print "tc=",'{:04x}'.format(ord(tc)),deconvert(tc)

        if tc == cALL:      # a * wildcard?

#           print "ALL last=< " + last + " >"
            if last != '': offs -= 1

            nm = _span(cALL,nsps)

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
            elif last in [ '.' , ',' , '-' ]:
                if offs == limt:
                    offs -= 1
                    continue
                txc = text[offs]
                if ellyChar.isWhiteSpace(txc) or txc in Trmls:
                    offs -= 1
                    continue
            elif last in ellyBuffer.separators:
                offs -= 1
                continue
            elif last in [ '?' , '!' ]:
                offs -= 1
                continue

        elif tc == cANY: # alphanumeric wildcard?
            if last != '' and ellyChar.isLetterOrDigit(last):
                _bind(); mbi += 1
                continue

        elif tc == cCAN: # nonalphanumeric wildcard?
#           print 'at cCAN'
            if last != ellyChar.AMP:
                if last == '' or not ellyChar.isLetterOrDigit(last):
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

        elif tc == cUPR: # uppercase letter wildcard?
#           print "UPR:",last,'@',offs
            if last != '' and ellyChar.isUpperCaseLetter(last):
                _bind(); mbi += 1
                continue

        elif tc == cLWR: # lowercase letter wildcard?
#           print "LWR:",last,'@',offs
            if last != '' and ellyChar.isLowerCaseLetter(last):
                _bind(); mbi += 1
                continue

        elif tc == cSPC: # space wildcard?
#           print "SPC:","["+last+"]"
            if last != '' and ellyChar.isWhiteSpace(last):
                nsps -= 1
                _bind(); _modify(); mbi += 1
                continue
#           print 'NO space'

        elif tc == cAPO: # apostrophe wildcard?
#           print "APO: last=" , last
            if ellyChar.isApostrophe(last):
                _bind(); _modify(); mbi += 1
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
#           print 'spanning wildcard, offs=' , offs , 'last=(' + last + ')'
            if last != '':            # still more to match?
                offs -= 1
#               print 'nsps=' , nsps
#               print '@' , offs , text
                nm = _span(tc,nsps)   # maximum match possible

                if nm == 0:                             # compensate for findExtendedBreak peculiarity
                    if offs + 1 < limt and mp < ml:     # with closing ] or ) to be matched in pattern
                        if patn[mp] in Enc:             # from text input
                            nm += 1

#               print 'spanning=' , nm
                if nm >= 1:
                    bf = _bind(nm); mbi += 1
                    bf[0] = offs      # bind from current offset
                    offs += nm        # move offset past end of span
                    bf[1] = offs      # bind to   new     offset
                    uf = _mark(1); unj += 1
                    uf.count = nm - 1 # at least one char must be matched
#                   print 'offs=' , offs
                    last = text[offs] if offs < limt else ''
                    continue
#           print 'fail tc=' , deconvert(tc)

        elif tc == '':
            if last == '' or not ellyChar.isPureCombining(last):
                matched = True        # successful match
                break

        ## match failure: rewind to last match branch
        ##

#       print "fail - unwinding" , unj

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
            nsps = uf.nsps           #
            break
        else:
#           print "no unwinding"
            break                   # quit if unwinding is exhausted
#       print 'cnt=' , uf.count , 'off=' , offs

    ##
    ## clean up on match mode or on no match possible
    ##

#   print "matched=",matched

    if not matched: return None     # no bindings

#   print text,offs

    ## consolidate contiguous bindings for subsequent substitutions

#   print "BEFORE consolidating consecutive bindings"
#   print "bd:",len(mbd)
#   print mbd[0]
#   print '----'
#   for b in mbd[1:]:
#       print b

    mbdo = mbd
    lb  = -1               # binding reference
    lbd = [ 0 , -1 ]       # sentinel value, not real binding
    mbd = [ lbd ]          # initialize with new offset after matching
    mbdo.pop(0)            # ignore empty binding
    while len(mbdo) > 0:   #
        bd = mbdo.pop(0)   # get next binding
        if len(bd) > 2:
            bd.pop()
            mbd.append(bd)
            lbd = bd
            lb = -1
        elif bd[0] < 0:    # check for optional match indicator here
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
#   print mbd[0]
#   print '----'
#   for b in mbd[1:]:
#       print b

    return mbd             # consolidated bindings plus new offset

############################ unit testing ############################

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print "usage: X pattern [spaces]"
        sys.exit(0)

    rawp = unicode(sys.argv[1],'utf-8')
    spcg = (len(sys.argv) > 2)
    print 'spcg=' , spcg

    patx = convert(rawp)
    if patx == None:
        print >> sys.stderr , "** cannot convert pattern"
        sys.exit(1)
    nspx = numSpaces(patx,spcg)
    if nspx > 0 and not spcg:
        print >> sys.stderr , "** space in pattern without second command line argument"
        sys.exit(1)

    print "pat=" , rawp , "converted to" , list(patx)

    print ""
    print "testing wildcard matching"
    print "enter text to match:"

    while True:
        try:
            print "> ",
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            break

        txt = list(unicode(line.rstrip(),'utf-8'))
        if len(txt) == 0: break
        print "test text=" , txt
        b = match(patx,txt,0,None,nspx)

        if b != None:
            n = b.pop(0)
            print n , "chars matched with" , len(b) , "wildcard bindings"
            for j in range(len(b)):
                r = b[j]
                print '\\\\' + str(j + 1) , '=' , r , txt[r[0]:r[1]]
        else:
            print "NO MATCH!"
