#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# nameRecognition.py : 17mar2015 CPM
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
heuristic name recognition procedure to put into Elly configuration listing of
entity extractors
"""

import sys
import ellyChar
import ellyConfiguration
import nameTable

_table = None   # to save name table
_cntxt = [ ]    # for short-term name definitions
_toscan = 0     # number of chars available to scan

_typ = -1       # have to do this in Python 2.7.*
_nch =  0       # in absence of nonlocal statement

def scan ( buffr ):

    """
    recognize personal names in text at current position

    arguments:
        buffr - current contents as list of chars

    returns:
        char count matched on success, 0 otherwise
    """

    def doLook ( mth , itm ):

        """
        do lookup with specified method using
        global variables in Python 2.7.*

        arguments:
            mth  - name table method
            itm  - string to look up
        """

        global _typ , _nch            # really need nonlocal
        _typ = mth(itm)
        if _typ < 0 and len(itm) > 3: # if no match, check for final '.'
            if itm[-1] == '.':
                _typ = mth(itm[:-1])
                if _typ >= 0:
                    _nch -= 1         # match without '.'

    global _typ , _nch
    global _toscan

#   print 'table=' , _table
    bln = len(buffr)
    if _table == None or bln < 2: return 0
    if _toscan > 0:
        if bln > _toscan:
            return 0
        else:
            _toscan = 0

    chx = buffr[0]
#   print 'scan chx=' , chx
    if not ellyChar.isLetter(chx) and chx != '(' and chx != '"': return 0

    cmps = [ ]                                 # name components this time
    ncmp = 0                                   # number of components for current name
    ninf = 0                                   # number inferred
    ntyp = len(nameTable.TYP)
    stat = [False]*ntyp                        # define state for getting personal name
    mlen = 0                                   # last match length

    bix = 0                                    # buffer index to advance in scanning
    _typ = -1
    while bix < bln:
        ltyp = -1                              # last match type
        _nch = _limit(buffr[bix:],mlen)        # length of next possible name component
#       print 'top _nch=' , _nch
        if _nch == 0: return 0
        elm = _extract(buffr[bix:],_nch)       # get possible component as string
        sch = buffr[bix]
        enclosed = (sch == '(' or sch == '"')  # type of next element
        doLook(_table.lookUp,elm)              # look it up in saved name table
#       print 'lookUp(' , elm , ')=' , _typ

        if _typ < 0:
            if _typ == nameTable.REJ:
                return 0                       # immediate rejection of any match
            if _typ == nameTable.STP:
                break                          # stop any more matching
            if elm[-1] == '.':                 # drop any trailing '.'
                elm = elm[:-1]
                if not enclosed:
                    _nch -= 1
            if enclosed:                       # enclosed element assumed to be name
                if not elm in _cntxt:
                    _cntxt.append(elm)         # make sure always to save in local context
                    ninf += 1                  # this is inferred!
            if elm in _cntxt:
                _typ = nameTable.XNM           # neutral name type to be noncommital

        if _typ < 0:
            tok = buffr[bix:bix + _nch]        # unknown token to check
#           print 'call infer with tok=' , tok
            if infer(tok):
#               print 'digraph test passed'
                _typ = nameTable.XNM           # neutral name type inferred
                if not _table.checkPhonetic(tok):
                    ninf += 1                  # count inferred component if no phonetic support
#           print '_typ=' , _typ

        if nameTable.starts(_typ) and bix > 0: # if component not at start of name,
            break                              #     must stop name scan

#       print 'continuing bix=' , bix
        while _typ >= 0:                       # continue as long as match is viable
            ncmp += 1                          # count up component
            cmps.append(elm)                   # save component
            bix += _nch                        # move ahead in scan
#           print 'bix=' , bix
            if _typ > 0:
#               print '_typ=' , _typ
                if stat[_typ]:                 # check for duplication of component type
                    if (ltyp >= 0 and
                        ltyp != _typ):         # allowed only if duplicate is consecutive
                        break
                mlen = bix                     # save index on actual match
                ltyp = _typ

            if nameTable.ends(_typ):           # if component marks end of name,
                break                          #    must stop name scan

            stat[_typ] = True                  # update match state
            if bix == bln: break
            if ellyChar.isWhiteSpace(buffr[bix]):
                bix += 1                       # skip any space to start of next component

            _nch = _limit(buffr[bix:],mlen)    # length of next possible name component
            if _nch == 0: break
            elm = _extract(buffr[bix:],_nch)   # get possible next component as string
            doLook(_table.lookUpMore,elm)      # look it up in saved name table
#           print 'lookUpMore(' , elm , ')=' , _typ

        if _typ < 0:                           # while-loop terminated without break
#           print 'ltyp=' , ltyp , 'mlen=' , mlen
            if ltyp < 0 or mlen == 0: break
            bix = mlen                         # restart at end of last match
            if bix == bln: break
            if ellyChar.isWhiteSpace(buffr[bix]):
                bix += 1                       # skip any space to start of next component
            continue

        break

#
#
#### additional constraints on acceptable personal name
#
#   print 'checking ltyp=' , ltyp
    if (ltyp == nameTable.CNJ or
        ltyp == nameTable.REL):                # a name cannot end with these types
        mlen -= _nch                           # have to drop them from any match
        if mlen == 0: return 0
        if ellyChar.isWhiteSpace(buffr[mlen-1]):
            mlen -= 1
        ncmp -= 1
        cmps.pop()

#   print 'ncmp=' , ncmp

    if ncmp == 0:                              # nothing matched?
        _planAhead(buffr)                      # check for possible problems in next scan
        return 0

#   print 'cmps=' , cmps
    if ncmp == ninf:
        return 0                               # name cannot be purely inferred

#   print 'ncmp=' , ncmp
    if ncmp == 1:                              # single-component name must be known or contextual
        if (not stat[nameTable.SNG] and
            not cmps[0] in _cntxt):
            return 0

#   print 'stat=' , stat[3:7]
    expl = (stat[nameTable.PNM] or             # name must have a substantial component
            stat[nameTable.SNM] or
            stat[nameTable.XNM] or
            stat[nameTable.SNG])

#   print 'expl=' , expl
    if (not expl and
        not (stat[nameTable.TTL] and           # or it could have just a title
             stat[nameTable.INI])):            #    and an initial
        return 0
#
####

#   print 'accepted mlen=' , mlen
    for cmpo in cmps:                          # if whole name is OK,
        if not cmpo in _cntxt:                 #    remember all components
            _cntxt.append(cmpo)                #    not already listed in context

    return mlen                                # will be > 0 on successful match

def _limit ( buffr , hstry ):

    """
    get length of next possible name component in buffer

    arguments:
        buffr - list of chars
        hstry - how much matched already

    returns:
        number of chars in continuation of last component, 0 for no next component
    """

    lnb = len(buffr)
    if lnb == 0: return 0

    bix = 0
    quot = False                           # indicate component starting with "
    parn = False                           #                             with (
    cmma = False                           #                             with ,
#   print '_limit buffr=' , buffr , 'hstry=' , hstry
    if buffr[0] == ',':                    # handle possible leading comma
        if hstry == 0 or lnb < 4: return 0
        bix += 1
        if ellyChar.isWhiteSpace(buffr[1]):
            bix += 1
        cmma = True
#       print 'for comma, bix=' , bix

    if buffr[bix] == '(':                  # handle short name in parentheses
        bix += 1
        parn = True
    if buffr[bix] == '"':                  # handle short name in double quotes
        bix += 1
        quot = True
#       print 'parn=' , parn , 'quot=' , quot
    if parn or quot:
#       print 'enclosed component from' , buffr[bix:]
        while bix < lnb:                   # collect letters for name
            chx = buffr[bix]
            if ellyChar.isWhiteSpace(chx):
                break
            elif not quot and parn and chx == ')':
                return bix + 1             # add trailing parenthesis
            elif quot and chx == '"':
                if bix + 1 < lnb and parn and buffr[bix+1] == ')':
                    return bix + 2         # add trailing quote and parenthesis
                elif not parn:
                    return bix + 1         # add trailing quote only
                else:
                    return 0               # no match
            elif chx == '.':
                return bix + 1             # add trailing period
            elif not ellyChar.isLetter(chx):
                break                      # unrecognizable char for name
            bix += 1
#       print 'no closure'
        return 0
    else:
#       print 'find component in' , buffr[bix:]
        while bix < lnb:
            chx = buffr[bix]               # collect letters for name
#           print 'chx=' , chx
            if chx == "'":
                if bix + 2 < lnb:
                    chn = buffr[bix+1]
                    if ellyChar.isWhiteSpace(chn):
                        break
                    if chn == 's' and not ellyChar.isLetter(buffr[bix+2]):
                        break
            elif not ellyChar.isLetter(chx):
                if chx == '.':
                    bix += 1
#                   print 'increment bix=' , bix
                break
            bix += 1

        if bix == lnb:

#           print 'ran out of chars'
            return bix                     # running out of chars means match

        else:

#           getting here means that more text follows limit
#           and so we may have to pick up extra chars here

            chx = buffr[bix]
#           print 'next chx=' , chx , 'bix=' , bix
            if ellyChar.isWhiteSpace(chx) or chx == "'":
                return bix                 # component can be terminated by space or (')
            elif chx == ',':
                if cmma:
                    return bix + 1         #     or comma when sequence starts with comma
                else:
                    return bix             #              when there is no starting comma
            elif ellyChar.isLetter(chx):
                return bix                 #     or letter, implying previous char was '.'
            else:
                return 0                   # failure to find name limit


def _extract ( buf , nch ):

    """
    get next possible name components at current position

    arguments:
        buf  - current contents as list of chars
        nch  - char count to work with

    returns:
        component string if found, otherwise ''
    """

    if nch == 0: return ''
    lrw = buf[:nch]      # list of chars in possible component
#   print 'lwr=' , lrw
    if lrw[0] == ',':
        if nch == 1 or not ellyChar.isWhiteSpace(lrw[1]): return ''
        lrw.pop(0)
        lrw.pop(0)

#   print 'lrw=' , lrw
    if lrw[0] == '(':
        lrw.pop()        # remove any pair of parentheses before lookup
        lrw.pop(0)
#   print 'lrw=' , lrw
    if len(lrw) > 2 and lrw[0] == '"' and lrw[-1] == '"':
        lrw.pop()        # remove any pair of double quotes before lookup
        lrw.pop(0)
    if len(lrw) > 0 and lrw[-1] == ',':
        lrw.pop()
#   print 'lrw=' , lrw

    return u''.join(lrw) # possible name component as string

_det = [  # determiners that ain inferred name component cannot follow
  'the' , 'an' , 'a' ,
  'one' , 'two' , 'three' , 'four' , 'five', 'six' , 'seven' ,
  'eight' , 'nine' , 'ten' , 'eleven' , 'twelve' , 'thirteen'
]

def _planAhead ( buf ):

    """
    check for possible problems in the next scan while context
    is still available and set flags if needed

    arguments:
        buf  - buffer to be scanned
    """

    global _toscan

    nsk = 0                     # total skip count
    lb = len(buf)
    if lb > 4:
        if buf[0] == '(':       # skip initial '('
            nsk += 1
            buf = buf[1:]
        if buf[0] == '"':       # skip initial '"'
            nsk += 1
            buf = buf[1:]
        lb -= nsk

    nix = 0                    # scan count
    if lb > 8:
        for chx in buf:        # go to first non-letter
            if not ellyChar.isLetter(chx):
                if ellyChar.isWhiteSpace(chx):
                    break      # must be space
                return
            nix += 1

        sst = ''.join(buf[:nix]).lower()
        if not sst in _det:
            return            # must find determiner

        nix += 1              # skip space
        if ellyChar.isUpperCaseLetter(buf[nix]):
            nix += 1          # skip first letter
            buf = buf[nix:]
            for ch in buf:    # go to next non-letter
                if not ellyChar.isLetter(ch):
                    if ellyChar.isWhiteSpace(ch):
                        break
                    return
                nix += 1
               
            _toscan = lb + nsk - nix

def infer ( tok ):

    """
    infer a token as a possible name component with
    side effect of converting it to lowercase ASCII

    arguments:
        tok  - token as list of chars

    returns:
        True if inferred, False otherwise
    """

#   print 'inferring tok=' , tok
    nch = len(tok)
    if (nch < 5 or not ellyChar.isUpperCaseLetter(tok[0]) or
        len(ellyConfiguration.digraph) == 0): return False

    for i in range(nch):     # drop diacritical marks, set lowercase
        tok[i] = ellyChar.toLowerCaseASCII(tok[i])

    miss = 0
    last = ''
    for i in range(1,nch):   # check plausibility of all digraphs
        digr = ''.join(tok[i-1:i+1])
#       print 'digr=' , digr , 'last=' , last
        if (digr == last or
            not digr in ellyConfiguration.digraph):
            miss += 1
        last = digr

#   print 'miss=' , miss
    if nch < 7:
        return (miss == 0)
    else:
        return (miss <= 1)

def setUp ( table ):

    """
    associate a name table with a name recognizer

    arguments:
        table  - Elly name table
    """

    global _table                # must declare in order to set!
#   print 'before ntb=' , _table
    _table = table
#   print 'after  ntb=' , _table

#
# unit test
#

if __name__ == '__main__':

    import ellyDefinitionReader

    inp = 'test' if len(sys.argv) == 1 else sys.argv[1]
    pnm = inp + '.n.elly'
    rdr = ellyDefinitionReader.EllyDefinitionReader(pnm)
    if rdr.error != None:
        print rdr.error
        sys.exit(1)

    ntb = nameTable.NameTable(rdr)

    print 'table loaded=' , ntb.filled()

    ntb.dump()

    setUp(ntb)

    while True: # test examples from standard input

        sys.stdout.write('> ')
        lin = sys.stdin.readline().strip()
        if len(lin) == 0: break
        buff = list(lin.decode('utf8'))     # get input string for text example
        nchr = _limit(buff,0)
        print 'first component=' , nchr , 'chars'
        nml = scan(buff)
        print 'match length=' , nml , 'out of' , len(buff)
