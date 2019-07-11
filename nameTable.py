#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# nameTable.py : 14mar2015 CPM
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
a table for identifying personal name components as a given internal type (see TYP)

a single-word component can also be specified in one of four special forms,
where X is a substring of at least TWO literal chars
(1)  X+  X is a prefix, and the rest of a lookup string must be a known component
(2)  X-  X is a prefix, and the rest of a lookup string does not matter
(3) +X   X is a suffix, and the rest of a lookup string must be a known component
(4) -X   X is a suffix, and the rest of a lookup string does not matter

the CND (=0) type allows for handling of multi-word components in tables

to put all name-related rules in a single persistent object, a name table will
also include phonetic patterns of common names for name component inference
"""

import sys
import ellyChar
import ellyException
import phondexEN

# component type encodings

REJ = -3  # reject match immediately
STP = -2  # not name component
NON = -1  # no match
CND =  0  # conditional match
TTL =  1  # title
HON =  2  # honorific
PNM =  3  # personal name
SNM =  4  # surname
XNM =  5  # either personal or surname
SNG =  6  # single component name
INI =  7  # initial
REL =  8  # relational qualifier
CNJ =  9  # AND
GEN = 10  # generation indicator

TYP = { 'rej':REJ , 'stp':STP , 'cnd':CND ,
        'pnm':PNM , 'snm':SNM , 'xnm':XNM , 'sng':SNG ,
        'gen':GEN , 'ttl':TTL , 'hon':HON , 'rel':REL , 'ini':INI ,
        'cnj':CNJ }  # internal name component types (NOT syntactic types!)

START  = [ TTL ] # these types must start a name
END    = [ GEN ] # these types must end   a name
NOTEND = [ REL , GEN ] # these must not end a name

# restrictions on sequencing of component types

def starts ( typ ):

    """
    does type have to start a name?
    arguments:
        typ  - encoded type
    returns:
        True if yes, False otherwise
    """
    return (typ in START)

def ends ( typ ):

    """
    does type have to end a name?
    arguments:
        typ  - encoded type
    returns:
        True if yes, False otherwise
    """
    return (typ in END)

def mustNOTend ( typ ):

    """
    type cannot end a name?
    arguments:
        typ  - encoded type
    returns:
        True if yes, False otherwise
    """
    return (typ in NOTEND)

class NameTable(object):

    """
    support for name entity extraction

    attributes:
        pres  - name starting patterns
        posts - name ending patterns
        dictn - dictionary for looking up components
        phone - list of common name phonetics
        compn - compound component being matched
        _nerr - error count in table definition
    """

    def __init__ ( self , inpr ):

        """
        define table from text input

        arguments:
            self  -
            inpr  - EllyDefinitionReader

        throws:
            TableFailure on table definition failure
        """

        self.pres  = { }
        self.posts = { }
        self.dictn = { }
        self.phone = [ ]
        self.compn = ''
        self._nerr = 0

#       print 'TYP=' , TYP

        while True:
            lin = inpr.readline().lower()    # ignore capitalization
            if len(lin) == 0: break

            if lin[0] == '=':                # phonetic entry?
                lin = lin[1:]                # if so, remove marker
                first = ''
                if lin[0] == 'a':            # vowel is first?
                    first = 'a'              # if so, remove it
                    lin = lin[1:]
                pho = first + lin.upper()    # combine any vowel with uppercase rest
                self.phone.append(pho)       # save in phonetic list
                continue

            lins = lin.strip().split(':')

            if len(lins) != 2:               # type definition must have two parts
                self._err(lne=lin)
                continue

            typ = lins[1].strip()            # get component type
            if not typ in TYP:
                self._err('bad name component type',lin)
                continue
            cod = TYP[typ]

            els = lins[0].strip().split(' ') # name component

#           print 'type=' , '"' + typ + '"' , els

            lim = len(els)

            if lim == 1:
                cmpo = els[0]
                chf = cmpo[0]                # first char of component
                chl = cmpo[-1]               # last  char
                if chf == '-' or chf == '+':
                    if not ellyChar.isLetter(chl) or len(cmpo) < 3:
                        self._err('bad end of name',lin)
                        continue
                    dky = cmpo[-2:]          # dictionary key is 2 chars only
                    if not dky in self.posts:
                        self.posts[dky] = [ ]
                    self.posts[dky].append([ cmpo[1:] , cod , (chf == '+') ])
                elif chl == '-' or chl == '+':
                    if not ellyChar.isLetter(chf) or len(cmpo) < 3:
                        self._err('bad start of name',lin)
                        continue
                    dky = cmpo[:2]           # dictionary key is 2 chars only
                    if not dky in self.pres:
                        self.pres[dky] = [ ]
                    self.pres[dky].append([ cmpo[:-1] , cod , (chl == '+') ])
                else:
                    self.dictn[cmpo] = cod
                    if cmpo[-1] == '.':      # if ending with '.' , also save without
                        self.dictn[cmpo[:-1]] = cod
                continue

            Nix = 1
            while Nix <= lim:                # process elements of name component
                cmpo = ' '.join(els[0:Nix])
                Nix += 1
                if cmpo not in self.dictn:   # first Nix elements
                    self.dictn[cmpo] = CND
            if self.dictn[cmpo] != CND:
                self._err('name component redefined',lin)
                continue
            self.dictn[cmpo] = TYP[typ]      # put into table

        if self._nerr > 0:
            print >> sys.stderr , '**' , self._nerr, 'name errors in all'
            print >> sys.stderr , 'name table definition FAILed'
            raise ellyException.TableFailure

    def filled ( self ):

        """
        check if name table is non-empty

        arguments:
            self

        returns:
            True if non-empty, False otherwise
        """

        return (len(self.dictn.keys()) > 0)

    def lookUp ( self , itm ):

        """
        look up substring in name table

        arguments:
            self  -
            itm   - string to look up

        returns:
            -1 if not found, component type code >= 0 otherwise
        """

        self.compn = ''
        itm = itm.lower()
        status = self._find(itm)
        if status >= 0:
            self.compn = itm
        return status

    def lookUpMore ( self , itm ):

        """
        look up compounding of substring in name table

        arguments:
            self  -
            itm   - string to look up

        returns:
            -1 if not found, component type code >= 0 otherwise
        """

        if self.compn == '':
            return NON
        else:
            cat = self.compn + ' ' + itm.lower()
            status = self._find(cat,False)
            if status >= 0:
                self.compn = cat
            return status

    def _find ( self , cmpo , smpl=True ):

        """
        lookup method with recursion

        arguments:
            self  -
            cmpo  - simple or compound component
            smpl  - simple flag

        returns:
            -1 or -2 if not found, component type code >= 0 otherwise
        """

#       print '_find:' , cmpo
        lcmp = len(cmpo)
        if lcmp == 0:
            return NON
        if cmpo in self.dictn:               # full name component known?
            return self.dictn[cmpo]
        if lcmp == 1:
            return INI if ellyChar.isLetter(cmpo[0]) else NON

        if cmpo[-1] == '.':                  # component ends in '.'?
            if lcmp == 2:
                if ellyChar.isLetter(cmpo[0]):
                    return INI
            return NON

        if smpl and lcmp > 4:                # check component by parts?
            pre = cmpo[:2]
            suf = cmpo[-2:]
#           print 'pre=' , pre , 'suf=' , suf
            if pre in self.pres:             # if not known, check for prefix match
                for p in self.pres[pre]:
                    x = p[0]
                    n = len(x)
#                   print 'recursion=' , p[2]
                    if (n < lcmp and
                        cmpo[:n] == x):      # prefix match found?
                        if not p[2] or self._find(cmpo[n:]) > 0:
                            return p[1]
            elif suf in self.posts:          # last resort is check for suffix match
                for p in self.posts[suf]:
                    x = p[0]
                    n = len(x)
#                   print 'recursion=' , p[2]
                    if (n < lcmp and
                        cmpo[-n:] == x):     # suffix match found?
                        if not p[2] or self._find(cmpo[:-n]) > 0:
                            return p[1]
        return NON

    def _err ( self , msg='bad component definition' , lne='' ):

        """
        for error handling

        arguments:
            self  -
            msg   - error message
            lne   - problem line
        """

        self._nerr += 1
        print >> sys.stderr , '** name error:' , msg
        if lne != '':
            print >> sys.stderr , '*  at [' , lne , ']'

    def checkPhonetic ( self , tokn ):

        """
        look for phonetic in table listing

        arguments:
            self  -
            tokn  - token as list of chars

        returns:
            True if found, False otherwise
        """

        pho = phondexEN.phondex(tokn)
        return (pho in self.phone)

    def dump ( self ):

        """
        show contents of name table

        arguments:
            self
        """

        stp = [ ]
        print '------------'
        nix = 0
        kys = sorted(self.dictn.keys())
        for ky in kys:
            cod = self.dictn[ky]
            if cod == STP:
                stp.append(ky)
            elif cod == REJ:
                stp.append(ky.upper())
            else:
                print ' {0:<11.11s}:{1:2d}'.format(ky,cod) ,
                nix += 1
                if nix%6 == 0: print ''
        print ''
        print '------------'
        kys = sorted(self.pres.keys())
        for ky in kys:
            lp = self.pres[ky]
            for p in lp:
                x = '+' if p[2] else '-'
                print ky , '/' , p[0] + x , ':' , p[1]
        print '------------'
        kys = sorted(self.posts.keys())
        for ky in kys:
            lp = self.posts[ky]
            for p in lp:
                x = '+' if p[2] else '-'
                print ky , '/' , x + p[0] , ':' , p[1]
        print '------- stop'
        nix = 0
        for st in stp:
            print ' {0:<10.10s}'.format(st) ,
            nix += 1
            if nix%8 == 0: print ''
        print ''
        print '------- phonetic'
        nix = 0
        for ph in self.phone:
            print '{0:<8.8s}'.format(ph) ,
            nix += 1
            if nix%9 == 0: print ''
        print ''

#
# unit test
#

if __name__ == '__main__':

    import ellyConfiguration
    import ellyDefinitionReader

    inp = 'test' if len(sys.argv) == 1 else sys.argv[1]
    pnm = ellyConfiguration.baseSource + inp + '.n.elly'
    rdr = ellyDefinitionReader.EllyDefinitionReader(pnm)
    if rdr.error != None:
        print rdr.error
        sys.exit(1)

    try:
        ntb = NameTable(rdr)
    except ellyException.TableFailure:
        sys.exit(1)

    print 'name test with' , '<' + pnm + '>'
    print 'table filled=' , ntb.filled()
    ntb.dump()

    while True: # test examples from standard input

        sys.stdout.write('> ')
        tos = sys.stdin.readline().decode('utf8').strip()
        if len(tos) == 0: break
        idx = ntb.lookUp(tos)
        print 'lookUp' , '(' , tos , ')= ' ,
        print idx if idx >= 0 else 'NONE'
