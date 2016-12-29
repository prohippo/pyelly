#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# symbolTable.py : 23dec2016 CPM
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
saved grammar rule symbols for syntactic analysis
plus associated lookup methods

(may be referenced at run-time for Elly error messages)
"""

import ellyBits
import ellyChar
import sys

NMAX = 72  # maximum number of syntactic type names
FMAX = 16  # maximum number of feature names per set

LAST = FMAX - 1

def featureConsistencySplit ( rslt , lfts , rhts , lh=False , rh=False ):

    """
    check consistency of syntactic and semantic feature sets
    for splitting rule

    arguments:
        rslt  - result feature bits
        lfts  - first  component feature bits
        rhts  - second
        lh    - left  inheritance?
        rh    - right

    returns:
        True if consistent, False otherwise
    """

#   print '-- Split' , rslt
    if rslt == None or rslt.id == '':
        return True
#   print 'set' , rslt.id , 'lh=' , lh , 'rh=' , rh
#   print 'left=' , lfts , 'right=', rhts
    if lh and lfts != None and lfts.id != '' and rslt.id != lfts.id:
#       print 'lh=' , lh , rslt.id , rslt , lfts.id , lfts
        return False
    if rh and rhts != None and rhts.id != '' and rslt.id != rhts.id:
#       print 'rh=' , rh , rslt.id , rslt , rhts.id , rhts
        return False
    return True

def featureConsistencyExtend ( rslt , lfts , rhts , lh=False , rh=False ):

    """
    check consistency of syntactic and semantic feature sets
    for extending rule

    arguments:
        rslt  - result feature bits
        lfts  - first  component feature bits
        rhts  - second
        lh    - left  inheritance?
        rh    - right

    returns:
        True if consistent, False otherwise
    """

#   print '-- Extend' , rslt
    if rslt == None or rslt.id == '':
        return True
    if lh or rh:
        if lfts != None and lfts.id != '' and rslt.id != lfts.id:
#           print 'lh=' , lh , rslt.id , rslt , lfts.id , lfts
            return False
        if rhts != None and rhts.id != '' and rslt.id != rhts.id:
#           print 'rh=' , rh , rslt.id , rslt , rhts.id , rhts
            return False
    return True

class SymbolTable(object):

    """
    tables of grammatical symbol names for relating different rules

    attributes:
        ntindx - syntactic type lookup
        ntname - syntactic type names
        sxindx - syntactic feature set names
        smindx - semantic  feature set names
        bsymbs - base symbol set for anomaly check
        excpns - symbols to ignore for anomaly check
    """

    def __init__ ( self ):

        """
        initialize

        arguments:
            self
        """

        self.ntindx = { } # start with everything empty
        self.ntname = [ ] #
        self.sxindx = { } #
        self.smindx = { } #
        self.bsymbs = [ ] #
        self.excpns = [ ] #

    def getFeatureSet ( self , fs , ty=False ):

        """
        get feature indices associated with given names in given set

        arguments:
            self  -
            fs    - feature set without enclosing brackets
            ty    - False=syntactic, True=semantic

        returns:
            list of EllyBits [ positive , negative ] on success, None on failure
        """

        if len(fs) < 1: return None

        bp = ellyBits.EllyBits(FMAX) # all feature bits zeroed
        bn = ellyBits.EllyBits(FMAX) #

        fsx = self.smindx if ty else self.sxindx
#       print '--------  fs=' , fs
        fid = fs[0]                  # feature set ID
        fnm = fs[1:].split(',')      # feature names
        if not fid in fsx:           # known ID?
#           print 'new feature set'
            d = { }                  # new dictionary of feature names
            if ty:
                d['*c'] = 0          # always define '*c' as semantic  feature
                d['*capital'] = 0    # equivalent to '*c'
            else:
                d['*r'] = 0          # always define '*r' as syntactic feature
                d['*right'] = 0      # equivalent to '*r'
                d['*l'] = 1          # always define '*l'
                d['*left']  = 1      # equivalent to '*l'
                d['*x'] = LAST       # always define '*x'
                d['*u'] = LAST       # always define '*u'
                d['*unique'] = LAST  # equivalent to '*u' and '*x'
            fsx[fid] = d             # make new feature set known
        h = fsx[fid]                 # for hashing of feature names
        if len(fnm) == 0:            # check for empty features
            return [ bp , bn ]
        for nm in fnm:
            nm = nm.strip()
            if len(nm) == 0: continue
            if nm[0] == '-':         # negative feature?
                b = bn               # if so, look at negative bits
                nm = nm[1:]
            elif nm[0] == '+':       # positive feature?
                b = bp               # if so, look at positive bits
                nm = nm[1:]
            else:
                b = bp               # positive bits by default

#           print '--------  nm=' , nm
            nmc = nm if nm[0] != '*' else nm[1:]
            for c in nmc:            # check feature name chars
                if not ellyChar.isLetterOrDigit(c):
                    print >> sys.stderr , 'bad feature name=' , nm
                    return None
            if not nm in h:          # new name in feature set?
                if nm[0] == '*':     # user cannot define reserved name
                    print >> sys.stderr , 'unknown reserved feature=' , nm
                    return None
                k = len(h)           # yes, this will be next free index
                l = FMAX             # upper limit on feature index
                if ty:               # semantic feature?
                    k -= 1           # if so, adjust for extra name *C
                else:
                    k -= 5           # else,  adjust for *UNIQUE and extra names *L, *R , *U , *X
                    l -= 1           #        adjust upper limit for *UNIQUE
                if k == l:           # overflow check
                    print >> sys.stderr, '+* too many feature names'
                    return None
                if k < 0:
                    print >> sys.stderr , 'bad index=' , k , 'l=' , l
                    return None
                h[nm] = k            # define new feature

#           print 'set bit' , h[nm] , 'for' , fid + nm
            b.set(h[nm])             # set bit for feature
        return [ bp , bn ]

    def getSyntaxTypeIndexNumber ( self , s ):

        """
        get index number for a syntax type name, defining it if necessary

        arguments:
            self  -
            s     - name

        returns:
            type index index number
        """

        if s in self.ntindx:
            return self.ntindx[s]
        else:
            n = len(self.ntindx)
            self.ntindx[s] = n
            self.ntname.append(s)
            return n

    def getSyntaxTypeName ( self , n ):

        """
        get a syntax type name from its index number

        arguments:
            self  -
            n     - index number

        returns:
            type name as string on success, '' on failure
        """

        if n < len(self.ntname):
            return self.ntname[n]
        else:
            return ''

    def getSyntaxTypeCount ( self ):

        """
        get number of syntax types defined

        arguments:
            self

        returns:
            integer count
        """

        return len(self.ntindx)

    def setBaseSymbols ( self ):

        """
        support check for undefined symbols in rules

        arguments:
            self
        """

#       print 'define base symbol set'
        self.bsymbs = self.getAllSymbols()

    def getAllSymbols ( self ):

        """
        list out all currently defined grammar symbols

        arguments:
            self

        returns:
            sorted list of unique symbols
        """

#       print 'in getAllSymbols()'

        ls = list(self.ntname)           # start collecting symbols

        for sid in self.sxindx.keys():   # syntactic features
            tb = self.sxindx[sid]
            for t in tb.keys():
                if t[0] != '*':          # ignore predefined ones
                    ls.append(sid + t)   # tagged by feature ID

        for did in self.smindx.keys():   # semantic features
            tb = self.smindx[did]
            for t in tb.keys():
                ls.append(did + t)       # tagged by ID

#       print len(ls) , ' symbols defined'
#       print 'unsorted' , ls
        ls.sort()
#       print 'sorted  ' , ls
        return ls                        # sort list in place

    def findUnknown ( self ):

        """
        find unknown symbols in language definition files

        arguments:
            self  -

        retuns:
            list of symbols not found in reference list
        """

#       print 'base symbol=' , self.bsymbs
        symbs = self.getAllSymbols() # listing of all currently seen symbols
        known = self.bsymbs          # listing of saved base symbols
        unkns = [ ]

        while len(known) > 0 and len(symbs) > 0:
            r = known[0]             # next reference symbol
            s = symbs[0]             # next new symbol
            if r == s:
                known = known[1:]    # new symbol in reference list
                symbs = symbs[1:]    # continue scanning
            elif r < s:
                known = known[1:]    # no match with reference symbol
            else:
                symbs = symbs[1:]    # symbol not in reference list
                unkns.append(s)

        unkns.extend(symbs)          # take any unlooked up symbols as unknown
        rslts = [ ]
        for s in unkns:              # update exceptions with latest unknowns
            if not s in self.excpns:
                self.excpns.append(s)
                rslts.append(s)      # return only unknowns not previously seen
#               if s[0] == '^': print '<' + s
        return rslts
