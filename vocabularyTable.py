#!/usr/local/bin/python
# PyElly - scripting tool for analyzing natural language
#
# vocabularyTable.py : 19nov2018 CPM
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
Elly vocabulary database support using SQLite
"""

import os
import sys

import symbolTable
import ellyChar
import ellyException
import definitionLine
import deinflectedMatching
import vocabularyElement
import syntaxSpecification
import featureSpecification
import conceptualHierarchy
import sqlite3 as dbs
import unicodedata

SSpec = syntaxSpecification.SyntaxSpecification
FSpec = featureSpecification.FeatureSpecification

vocabulary = '.vocabulary.elly.bin' # built vocabulary file suffix
source     = '.v.elly'              # input vocabulary text file suffix

nerr = 0                            # shared error count among definition methods

initChr = [
    u'.' , u'-' , u'"' , u"'" , ellyChar.LDQm , u',' , u'%' , ellyChar.MDSH , ellyChar.HYPH ,
    u'\u03B1' , u'\u03B2' , u'\u03B3' , u'\u03B4' , u'\u03B5' ,
    u'\u03B6' , u'\u03B7' , u'\u03B8' , u'\u03B9' , u'\u03BA' ,
    u'\u03BB' , u'\u03BC' , u'\u03BD' , u'\u03BE' , u'\u03BF' ,
    u'\u03C0' , u'\u03C1' , u'\u03C3' , u'\u03C4' , u'\u03C5' ,
    u'\u03C6' , u'\u03C7' , u'\u03C8' , u'\u03C9'
]

def delimitKey ( t ):

    """
    get bounds of vocabulary table key for looking up a term
    starting at the front of a given text string
    with special stripping of 'S at the end

    arguments:
        t  - text string to scan

    returns:
        count of chars to take for search key
    """

    ln = len(t)                   # number of chars in input text
    if ln == 0: return 0
    if not ellyChar.isLetterOrDigit(t[0]): return 1

#   print 'delimitKey t=' , t

    k = t.find('-')               # find rough range of SQLite key in text
    n = t.find(' ')               # delimited by either a hyphen or a space
    if n < 0: n = ln              # if space, take everything
    if k > 1 and n > k: n = k     # hyphen delimits if it comes first
    n -= 1                        # index of last char of candidate key
#   print 'k=' , k , 'n=' , n

    while n > 0:                  # scan input text backwards
        c = t[n]                  # check char for alphanumeric
        if ellyChar.isLetterOrDigit(c):
#           print 'n=' , n , 'c=' , c
            if n > 1:             # check for 'S as special case!
                if ( c in [ 's' , 'S' ] and
                     ellyChar.isApostrophe(t[n-1]) ):
#                   print 'drop \'S from SQLite key'
                    n -= 1
                else:
                    break
            else:
                break
        n -= 1                    # continue scanning backwards
#   print 'key=' , t[:n+1]
    return n + 1                  # to get key length ending in alphanumeric

GrkL = {
    u'\u03B1' : 'a' , u'\u03B2' : 'b' , u'\u03B3' : 'g' , u'\u03B4' : 'd' , u'\u03B5' : 'e' ,
    u'\u03B6' : 'z' , u'\u03B7' : 'e' , u'\u03B8' : 't' , u'\u03B9' : 'i' , u'\u03BA' : 'k' ,
    u'\u03BB' : 'l' , u'\u03BC' : 'm' , u'\u03BD' : 'n' , u'\u03BE' : 'x' , u'\u03BF' : 'p' ,
    u'\u03C0' : 'p' , u'\u03C1' : 'r' , u'\u03C3' : 's' , u'\u03C4' : 't' , u'\u03C5' : 'u' ,
    u'\u03C6' : 'f' , u'\u03C7' : 'x' , u'\u03C8' : 'p' , u'\u03C9' : 'o'
}

def toKey ( s ):

    """
    convert string or list of chars to ASCII key for SQLite

    arguments:
        s   - string or list of Unicode chars

    returns:
        ASCII key as string
    """

    if len(s) == 1 and s[0] in GrkL:
        return GrkL[s[0]]
    sl = list(s)
    ellyChar.toLowerCaseASCII(sl)
#   print 'VT key=' , sl
    return ''.join(sl)

def _err ( s='malformed vocabulary input' ):

    """
    for error handling

    arguments:
        s  - error message

    exceptions:
        FormatFailure on malformed vocabulary entry
    """

    global nerr
    nerr += 1
    print >> sys.stderr , '** vocabulary error:' , s
    raise ellyException.FormatFailure('in vocabulary entry')

_smfchk = [None]*symbolTable.NMAX     # for extra consistency check

def build ( name , stb , defn ):

    """
    static method to create an Elly vocabulary database from text file input

    arguments:
        name  - for new SQLite database
        stb   - Elly symbol table
        defn  - Elly definition reader for vocabulary

    exceptions:
        TableFailure on error
    """

    global nerr
    nerr = 0
    cdb = None  # SQLite db connection
    cur = None  # SQLite db cursor

#   print 'built stb=' , stb

    if stb == None :
        print >> sys.stderr, 'no symbol table'
        raise ellyException.TableFailure

    try:
        zfs = FSpec(stb,'[$]',True).positive.hexadecimal(False)
    except ellyException.FormatFailure:              # should never need this
        print >> sys.stderr , 'unexpected failure with zero features'
        raise ellyException.TableFailure

#   print 'zfs=' , zfs               # hexadecimal for all features off

    tsave = ''                                       # original term
    dsave = ''                                       #          definition

    try:
        filn = name + vocabulary                     # where to put vocabulary database
        try:
            os.remove(filn)                          # delete the file if it exists
        except OSError:
            print >> sys.stderr , 'no' , filn        # if no such file, warn but proceed

#### SQLite DB operations
####
        try:
            cdb = dbs.connect(filn)                  # create new database
            cur = cdb.cursor()
            cur.execute("CREATE TABLE Vocab(Keyx TEXT, Defn TEXT)")
            cdb.commit()
        except dbs.Error , e:
            print >> sys.stderr , e
            raise ellyException.TableFailure         # give up on any database failure

#       print 'creating' , filn
#
####

        r = None                                          # for error reporting

        while True:                                       # process vocabulary definition records

            try:                                          # for catching FormatFailure exception
#               print '------------'
                r = defn.readline()                       # next definition
                if len(r) == 0: break                     # stop on EOF
#               print type(r) , r
                r = definitionLine.normalize(r)           #
#               print 'to' , r

                k = r.find(' : ')                           # look for first ' : '
                if k < 0:
                    tsave = r
                    dsave = None
                    _err()                                # report error and quit entry

                t = r[:k].strip()                         # term to go into dictionary
                d = r[k+2:].strip()                       # its definition
                tsave = t                                 # save for any error reporting
                dsave = d                                 #

#               print ' tm=' , '<' + t + '>' , 'df=' , '<' + d + '>'
                if len(t) == 0 or len(d) == 0:
                    _err()                                # quit on missing parts
                c = t[0]
                if not ellyChar.isLetterOrDigit(c) and not c in initChr:
                    _err('bad term')

                n = delimitKey(t)                         # get part of term to index
#               print 'delimit=' , n
                if n <= 0:
                    _err()                                # quit on bad term
                wky = toKey(t[:n])                        # key part of term to define
#               print '  SQLite key=' , wky

#               print 'd=' , d
                ns = syntaxSpecification.scan(d)          # find extent of syntax info
#               print 'ns=' , ns , '"' + d[ns:] + '"'
                if ns <= 0: _err('bad syntax specification')
                if not d[ns:] == '' and d[ns] != ' ': _err('trailing chars in syntax specification')
#               print 'PoS=' , d[:ns]

                syn = d[:ns]                              # syntax info as string
                d = d[ns:].strip()                        # rest of definition

                try:
#                   print 'VT syn=' , syn
                    ss = SSpec(stb,syn)                   # decode syntax info
#                   print 'VT ss =' , ss
                except ellyException.FormatFailure:
                    _err('malformed syntax specification')
                cat = str(ss.catg)                        #   syntax category
                cid = _smfchk[ss.catg]                    #   associated semantic feature ID
                syf = ss.synf.positive.hexadecimal(False) #   syntactic flags
#               print 'cat=' , cat
#               print 'syf=' , syf

                smf = zfs                                 # initialize defaults for
                pb = '0'                                  #   cognitive semantics
                cn = conceptualHierarchy.NOname           #

#               print '0:d=[' + d + ']'
                if len(d) > 1:                            # check for cognitive semantics
                    x = d[0]
                    if x == '[' or x == '0' or x == '-':  # semantic features?
                        if x != '[':                      # a '0' or '-' means to take default
                            if len(d) == 1 or d[1] != ' ':
                                _err('missing semantic features')
                            d = d[2:].strip()             # skip over
                        else:
                            ns = featureSpecification.scan(d) # look for ']' of features
#                           print 'ns=' , ns
                            if ns < 0:
                                _err()
                            sem = d[:ns]                  # get semantic features
                            d = d[ns:].strip()            # skip over for subsequent processing

                            sid = sem[1]                  # feature ID
                            if sid != cid:
                                if cid != None:
                                    _err('inconsistent semantic feature id')
                                _smfchk[ss.catg] = sid

                            try:
#                               print 'smf=' , smf
                                fs = FSpec(stb,sem,True)
                            except ellyException.FormatFailure:
                                _err('bad semantic features')
                            smf = fs.positive.hexadecimal(False) # convert to hex

#                       print '1:d=[' + d + ']'
                        ld = len(d)
#                       print 'ld=' , ld
                        if ld == 0:
                            _err('missing plausibility')
                        np = 0
                        x = d[np]
                        if x == '+' or x == '-':
                            np += 1                       # take any plus or minus sign
                        while np < ld:                    # and successive digits
                            if ellyChar.isDigit(d[np]): np += 1
                            else: break
#                       print 'np=' , np
                        if np == 0:
                            _err('missing plausibility')
                        pb = d[:np]                       # plausibility bias
#                       print 'pb=' , pb
                        d = d[np:]
                        ld = len(d)
#                       print '2:d=[' + d + ']'
                        if ld > 1:                        # any more to process?
                            c = d[0]                      # get next char after bias
                            d = d[1:]                     # advance scan
                            ld -= 1
                            if c == '/':                  # check for explicit concept
#                               print 'getting concept'
                                np = 0
                                while np < ld:            # get extent of concept
                                    if ellyChar.isWhiteSpace(d[np]): break
                                    np += 1
                                if np == 0:
                                    _err('missing concept for plausibility')
                                cn = d[:np]               # extract concept
                                d = d[np:]
                            elif c != ' ':
                                _err()                    # signal bad format
                        elif ld > 0:
                            _err()                        # unidentifiable trailing text
                    elif d[0] != '(':
                        dd = d
                        while ellyChar.isLetterOrDigit(dd[0]):
                            dd = dd[1:]
                        if len(dd) == 0 or dd[0] != '=':
                            _err()

                d = d.strip()                             # rest of definition
#               print 'rest of d=' , d
                if len(d) > 0 and d[-1] == '=':
                    if len(d) == 1 or d[0] != '=':
                        _err('incomplete definition')

                ld = [ ]                            # for normalizing definition

                k = 0                               # count spaces removed
                sd = ''                             # previous char seen
                for cd in d:                        # scan all chars in translation
#                   print 'cd=' , cd
                    if cd == ' ':
                        if sd == '=' or sd == ',' or sd == ' ':
                            k += 1
                            sd = cd
                            continue
                    elif cd == '=' or cd == ',':    # no spaces before '=' or ','
                        if sd == ' ':
                            k += 1
                            ld.pop()
                    if cd == ',':
                        if sd == '=':
                            _err('missing translation')
                        cd = '#'                    # format for PICK operation
                    elif cd == '=' and sd == '=':
                        print >> sys.stderr , '** WARNING \'=\' followed by \'=\''
                        print >> sys.stderr , '*  at [' , tsave , ']'

                    sd = cd
                    ld.append(cd)                   # add char to reformatted definition

#               print 'ld=' , ld
                if k > 0:
                    d = ''.join(ld)                 # definition with spaces removed

#               print '3:d=[' + d + ']'

                vrc = [ t , '=:' , cat , syf , smf ,
                        pb , cn ]                   # start data record
                vss = u' '.join(vrc)                # convert to string
                vss += u' ' + d                     # fill out record with rest of input
#               print 'type(vss)=' , type(vss)

#               print 'rec=' , vrc , 'tra=' , d
#               print '   =' , vss

            except ellyException.FormatFailure:     # will catch exceptions from _err()
                print >> sys.stderr , '*  at [' , tsave ,
                if dsave != None:
                    print >> sys.stderr , ':' , dsave ,
                print >> sys.stderr , ']'
                continue                            # skip rest of processing this rule

#### SQLite DB operation
####
            try:
                sql = "INSERT INTO Vocab VALUES(?,?)"
#               print type(wky) , wky , type(vss) , vss
                cur.execute(sql,(wky,vss))
            except dbs.Error , e:
                print >> sys.stderr , 'FATAL' , e
                sys.exit(1)
#
####


#### SQLite DB operations
####
        if nerr == 0:
            cdb.commit()
        cdb.close()                                   # clean up
#       print 'DONE'
#
####

    except StandardError , e:                         # catch any other errors
        print >> sys.stderr , '**' , e
        print >> sys.stderr , '*  at' , r
        nerr += 1

    if nerr > 0:
        print >> sys.stderr , '**' , nerr , 'vocabulary table errors in all'
        print >> sys.stderr , '*  compilation FAILed'
        cdb.close()                                   # discard any changes
        raise ellyException.TableFailure

class Result(object):

    """
    structured data to return as result of vocabulary table search

    attributes:
        vem    - vocabulary entry record matched
        nspan  - character count in match including any suffix
        suffx  - suffix disregarded in matching
    """

    def __init__ ( self , vem , nspan , suffx ):

        """
        initialization

        arguments:
            self  -
            vem   - vocabulary entry record
            nspan - total character span in match
            suffx - suffix removed
        """

        self.vem   = vem
        self.nspan = nspan
        self.suffx = suffx

    def __unicode__ ( self ):

        """
        show result parts

        arguments:
            self

        returns:
            string representation
        """

        return u''.join(self.vem.chs) + u' ' + unicode(self.nspan) + u' <' + ''.join(self.suffx) + u'>'

    def __str__ ( self ):

        """
        ASCII string representation

        arguments:
            self

        returns:
            string representation
        """

        return unicodedata.normalize('NFKD',unicode(self)).encode('ascii','ignore')

class VocabularyTable(deinflectedMatching.DeinflectedMatching):

    """
    interface to external data base

    attributes:
        cdb    - SQLite db connection
        cur    - SQLite db cursor

        string - (inherited from SimpleTransform)

        endg   - any ending removed for match
    """

    def __init__ ( self , name ):

        """
        initialization

        arguments:
            self  -
            name  - system name
        """

        super(VocabularyTable,self).__init__()
        database = name + vocabulary
        self.cdb = None
        self.cur = None
        if not os.path.isfile(database):
            return

#### SQLite DB operations
#
        try:
            self.cdb = dbs.connect(database)
            self.cur = self.cdb.cursor()
        except dbs.Error , e:
            print >> sys.stderr , 'FATAL' , e
            sys.exit(1)
#
####

        self.endg = None

    def __del__ ( self ):

        """
        cleanup

        arguments;
            self
        """

        if self.cdb != None:
            self.cdb.close()  # close database file for completeness

    def _getDB ( self , key ):

        """
        get list of records associated with specified key

        arguments:
            self  -
            key   - string value for lookup

        returns:
            data records if successful, None otherwise
        """

#       print '_getDB()'
        if self.cdb == None: return None

        try:

            rs = [ ]                      # for results
            akey = key.lower()            # convert to ASCII lower case for lookup

#           print 'key=' , type(akey) ,akey

#### SQLite DB operations
#
            sql = "SELECT * FROM Vocab WHERE Keyx = ?"
            self.cur.execute(sql,(akey,))
            tup = self.cur.fetchall()
#
####

#           print 'loop, tup=',tup
            for v in tup:                 # retrieved vocabulary match
                ve = vocabularyElement.VocabularyElement(v)
                rs.append(ve)             # add entry to results

            return rs

        except StandardError , e:
            print >> sys.stderr , 'general error:' , e
            return None

    def lookUp ( self , chrs , keyl ):

        """
        look for terms in vocabulary at current text position

        arguments:
            self  -
            chrs  - text char list
            keyl  - number of initial chars to use a DB key

        returns:
            list of tuples [  VocabularyElement , Result ], possibly empty
        """

#       print 'lookUp: chrs=' , chrs , 'keyl=' , keyl

        res = [ ]                     # result list initially empty
        rln = 0

        if len(chrs) == 0:
            return res                # empty list at this point

#       print 'chrs=' , type(chrs) , type(chrs[0])

        if keyl < 1:
            return res                # still empty list

        strg = toKey(chrs[:keyl])

#       print 'vocab search key=' , list(strg) , type(strg)
#       print '0 endg=' , self.endg

#       print listDBKeys(self.cdb)

        vs = self._getDB(strg)        # look up first word in vocabulary table
#       print '1 endg=' , self.endg

        if vs == None or len(vs) == 0:
            return res

#       print len(vs) , 'raw entries found'

        lm = len(chrs)                # total length of text for lookup

        for v in vs:                  # look at possible vocabulary matches

#           print 'entry=' , v

            ln = v.length()           # total possible match length for vocabulary entry

#           print 'rln=' , rln , 'ln=' , ln , 'lm=' , lm

            if ln  > lm:              # must be enough text in entry to match
                continue

            k = ln
            while k < lm:
                chrsk = chrs[k]
                if not ellyChar.isLetter(chrsk) and chrsk != '\'': break
                k += 1
#           print 'k=' , k
#           print v.chs , ':' , chrs[:k]
            nm = self.doMatchUp(v.chs,chrs)
            if nm == 0 or nm < rln: continue
#           print '2 endg=' , self.endg

#           print 'rln=' , rln , 'ln=' , ln
            if rln < nm:              # longer match than before?
#               print 'new list'
                res = [ ]             # if so, start new result list for longer matches
                rln = nm              # set new minimum match length

#           print 'returning' , v.chs , nm , '<' + self.endg + '>'
            rs = Result(v,nm,self.endg)   # new result object be returned
#           print 'rs=' , rs
            res.append(rs)            # add to current result list

        rem = [ ]
#       print 'len(res)=' , len(res)
        if len(res) > 1:              # check for special case where term with and
            for re in res:            # without inflection is in vocabulary
#               print 're=' , re
                if len(re.suffx) == 0:
                    rem.append(re)
        if len(rem) > 0:
            return rem                # if so, keep only full matches
        else:
            return res                # return surviving matches

    def lookUpSingleWord ( self , word ):

        """
        look single word up in vocabulary table with no stemming

        arguments:
            self  -
            word  - text char string (preferred) or list

        returns:
            list of VocabularyElement objects
        """

        ves = [ ]                     # result list initially empty
#       print 'word=' , word

        lw = len(word)
#       print 'lw=' , lw
        if lw == 0:
            return ves                # empty list at this point
        key = toKey(word)             # SQLite search key

        vs = self._getDB(key)         # look up key in vocabulary table
#       print 'vs=' , vs

        if vs == None or len(vs) == 0:
            return ves

        for v in vs:                  # look at possible vocabulary matches

#           print 'v=' , v , v.length() , lw
            if lw == v.length() and icmpr(v.chs,word) == 0:
#               print 'match'
                ves.append(v)         # only exact match acceptable

        return ves                    # return all exact matches

def icmpr ( vc , tc ):

    """
    compare vocabulary entry to text with case insensitivity

    arguments:
        vc    - vocabulary chars
        tc    - text chars

    returns:
        0 on match, n if mismatch at n chars before end, -1 if unmatched
    """

    k = len(vc)
    n = len(tc)
    if k > n: return -1
    if k == 0: return n
#   print 'vc=' , vc
#   print 'tc=' , tc[:k]
    for i in range(k):
#       print i , vc[i] , tc[i]
        if vc[i].lower() != tc[i].lower(): return k - i
    return 0

def listDBKeys ( dbso ):

    """
    get all database keys

    arguments:
        dbso  - SQLite database object

    returns:
        list of keys
    """

#   print 'listDBkeys():'

#### SQLite DB operations
#
    try:
        ucur = dbso.cursor()
        ucur.execute("SELECT * FROM Vocab")
        ursl = ucur.fetchall()
#       print '=' , ursl
        return [ u[0] for u in ursl ]
    except dbs.Error:
        print >> sys.stderr , 'cannot access vocabulary table'
        sys.exit(1)
#
####

#
# unit test and standalone database building
#

if __name__ == '__main__':

    import ellyDefinitionReader

    from ellyPickle import load
    from ellyBase   import rules

    from generativeDefiner import showCode

    def check ( vtb , ts , kl=None ):
        """ lookup method for unit testing
            arguments:
                vtb  - target vocabulary table
                ts   - text as list of chars
                kl   - length of text to use as key
        """
        lts = len(ts)
        if kl == None or kl > lts: kl = lts
        rs = vtb.lookUp(ts,kl)               # check for possible vocabulary matches
        print 'full text=' , '<' + u''.join(ts) + '>' ,
        if len(rs) == 0:                     # any vocabulary entries found?
            print 'FOUND NONE'
        else:
            print 'FOUND' , len(rs)
            print ''
            for r in rs:                     # if found, note each entry
                print '=' , unicode(r.vem)   # show each match
                print ' ' , r.nspan , 'chars matched, endings included'
                if r.suffx != '':
                    print '  ending=' , '[' +  r.suffx + ']'
#               print 'generative semantics'
                showCode(r.vem.gen.logic)
                print ''
            print '--'

    nams = sys.argv[1] if len(sys.argv) > 1 else 'test'
    dfns = nams + source
    limt = sys.argv[2] if len(sys.argv) > 2 else 24

    erul = load(nams + rules)                       # get pickled Elly rules
    if erul == None:
        ustb = symbolTable.SymbolTable()            # if none, make new symbol table
    else:
        ustb = erul.stb                             # else, get existing symbol table

    unkns = ustb.findUnknown()                      # check for new symbols added
    print "new symbols"
    for us in unkns:
        print '[' + us + ']'                        # show every symbol
    print ''

    print 'source=' , dfns
    inp = ellyDefinitionReader.EllyDefinitionReader(dfns)
    if inp.error != None:
        print >> sys.stderr , inp.error
        sys.exit(1)

    try:
        build(nams,ustb,inp)             # create database from vocabulary table
    except ellyException.TableFailure:
        print >> sys.stderr , 'exiting'
        sys.exit(1)                      # quit on failure

    uvtb = VocabularyTable(nams)         # load vocabulary table just created

    ucdb = uvtb.cdb                      # get database for table
    if ucdb == None:
        print >> sys.stderr , 'no vocabulary table found'
        sys.exit(1)

    nu = 0

    resl = listDBKeys(ucdb)

    hk = { }
    for ur in resl:
        hk[ur] = 0
    unqk = hk.keys()
    print len(unqk) , 'unique DB keys\n'
    print 'checking DB keys as SINGLE-word vocabulary entries'
    for ky in unqk:
        if nu >= limt: break           # stop when too many keys
        nu += 1
        check(uvtb,list(ky))           # dump all info for key
        print ''

    print 'enter SINGLE- and MULTI-word terms to look up in table with NO delimiting'
    while True:                        # now look up terms from standard input
        sys.stdout.write('> ')
        ul = sys.stdin.readline()      # get test example to look up
        if len(ul) <= 1: break
        ssx = ul.strip().decode('utf8')
        tsx = list(ssx)                # get list of chars
        kn = delimitKey(ssx)           # get part of term for indexing
        if kn == 0:                    # if none, cannot look up
            print 'index NOT FOUND:' , ssx
            continue
        print 'raw key=' , tsx[:kn]
        check(uvtb,tsx,kn)
        print ''

    sys.stdout.write('\n')

