#!/usr/local/bin/python
# PyElly - scripting tool for analyzing natural language
#
# vocabularyTable.py : 30apr2015 CPM
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

import ellyChar
import ellyException
import vocabularyElement
import syntaxSpecification
import featureSpecification
import sqlite3 as dbs

SSpec = syntaxSpecification.SyntaxSpecification
FSpec = featureSpecification.FeatureSpecification

vocabulary = '.vocabulary.elly.bin' # compiled vocabulary file suffix
source     = '.v.elly'              # input vocabulary text file suffix

nerr = 0                            # shared error count among methods

def toIndex ( t ):

    """
    get part of term for vocabulary table indexing that
    ends in alphanumeric or is a single nonalphanumeric

    arguments:
        t  - term as string

    returns:
        count of chars to index
    """

    ln = len(t)                   # number of chars in term
    if ln == 0: return 0
    n = t.find(' ')               # find first part of term
    if n < 0: n = ln              # if indivisible, take everything
    n -= 1                        # find last alphanumeric chars of first part
    while n > 0 and not ellyChar.isLetterOrDigit(t[n]):
        n -= 1
    return n + 1

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

def compile ( name , stb , defn ):

    """
    static method to create an Elly vocabulary database from text file input

    arguments:
        name  - for new BSDDB database
        stb   - Elly symbol table
        defn  - Elly definition reader for vocabulary

    exceptions:
        TableFailure on error
    """

    global nerr
    nerr = 0
    cdb = None  # SQLite db connection
    cur = None  # SQLite db cursor

#   print >> sys.stderr , 'compiled stb=' , stb

    if stb == None :
        print >> sys.stderr, 'no symbol table'
        raise ellyException.TableFailure

    try:
        zfs = FSpec(stb,'[$]',True).positive.hexadecimal(False)
    except ellyException.FormatFailure:              # should never need this
        print >> sys.stderr , 'unexpected failure with zero features'
        raise ellyException.TableFailure

#   print >> sys.stderr , 'zfs=' , zfs               # hexadecimal for all features off

    tsave = ''                                       # original term
    dsave = ''                                       #          definition

    try:
        filn = name + vocabulary                     # where to put vocabulary database
        try:
            os.remove(filn)                          # delete the file if it exists
        except OSError:
            print >> sys.stderr , 'no' , filn

#### SQLite
#
        try:
            cdb = dbs.connect(filn)                  # create new database
            cur = cdb.cursor()
            cur.execute("CREATE TABLE Vocab(Keyx TEXT, Defn TEXT)")
            cdb.commit()

        except dbs.Error , e:
            print >> sys.stderr , e
            raise ellyException.TableFailure         # give up on any failure

#       print >> sys.stderr , 'creating' , filn
#
####

        r = None                                          # for error reporting

        while True:                                       # process vocabulary records

            try:
#               print >> sys.stderr , '------------'
                r = defn.readline()                       # next definition
                if len(r) == 0: break                     # stop on EOF
                if r[0] == '#': continue                  # skip comment line
#               print >> sys.stderr , type(r) , r

                k = r.find(':')                           # look for first ':'
                if k < 0:
                    tsave = r
                    dsave = None
                    _err()                                # report error and quit entry
                    continue

                t = r[:k].strip()                         # term to go into dictionary
                d = r[k+1:].strip()                       # its definition
                tsave = t                                 # save for any error reporting
                dsave = d                                 #

#               print >> sys.stderr , ' tm=' , '<' + t + '>' , 'df=' , '<' + d + '>'
                if len(t) == 0 or len(d) == 0:
                    _err()                                # quit on missing parts
                    continue
                c = t[0]
                if not ellyChar.isLetterOrDigit(c) and c != '.' and c != '"':
                    _err('bad term')
                    continue

                n = toIndex(t)                            # get part of term to index
                if n == 0:
                    _err()                                # quit on bad term
                    continue
                wky = t[:n].lower()                       # first word of term to define
#               print >> sys.stderr , '  SQLite key=' , wky

                ns = syntaxSpecification.scan(d)          # find extent of syntax info
#               print >> sys.stderr , 'ns=' , ns
                if ns <= 0: _err('bad syntax specification')
#               print >> sys.stderr , 'PoS=' , d[:ns]

                syn = d[:ns]                              # syntax info as string
                d = d[ns:].strip()                        # rest of definition

                try:
#                   print >> sys.stderr , 'VT syn=' , syn
                    ss = SSpec(stb,syn)                   # decode syntax info to get
#                   print >> sys.stderr , 'VT ss =' , ss
                except ellyException.FormatFailure:
                    _err('malformed syntax specification')
                    continue
                cat = str(ss.catg)                        #   syntax category
                syf = ss.synf.positive.hexadecimal(False) #   syntactic flags
#               print >> sys.stderr , 'syf=' , syf

                smf = zfs                                 # initialize defaults for
                pb = '0'                                  #   cognitive semantics
                cn = '-'                                  #

#               print >> sys.stderr , '0:d=[' + d + ']'
                if len(d) > 1:                            # check for cognitive semantics
                    x = d[0]
                    if x == '[' or x == '0' or x == '-':  # semantic features?
                        if x != '[':                      # a '0' or '-' means to take default
                            if len(d) == 1 or d[1] != ' ':
                                _err('missing semantic features')
                                continue
                            d = d[2:].strip()             # skip over
                        else:
                            ns = featureSpecification.scan(d) # look for ']' of features
#                           print >> sys.stderr , 'ns=' , ns
                            if ns < 0:
                                _err()
                                continue
                            sem = d[:ns]                  # get semantic features
                            d = d[ns:].strip()            # skip over
                            try:
#                               print >> sys.stderr , 'smf=' , smf
                                fs = FSpec(stb,sem,True)
                            except ellyException.FormatFailure:
                                _err('bad semantic features')
                                continue
                            smf = fs.positive.hexadecimal(False) # convert to hex

#                       print >> sys.stderr , '1:d=[' + d + ']'
                        ld = len(d)
#                       print >> sys.stderr , 'ld=' , ld
                        if ld == 0:
                            _err('missing plausibility')
                            continue
                        np = 0
                        x = d[np]
                        if x == '+' or x == '-':
                            np += 1                       # take any plus or minus sign
                        while np < ld:                    # and successive digits
                            if ellyChar.isDigit(d[np]): np += 1
                            else: break
#                       print >> sys.stderr , 'np=' , np
                        if np == 0:
                            _err('missing plausibility')
                            continue
                        pb = d[:np]                       # plausibility bias
#                       print >> sys.stderr , 'pb=' , pb
                        d = d[np:]
                        ld = len(d)
#                       print >> sys.stderr , '2:d=[' + d + ']'
                        if ld > 1:                        # any more to process?
                            c = d[0]                      # get next char after bias
                            d = d[1:]                     # advance scan
                            ld -= 1
                            if c == '/':                  # check for explicit concept
#                               print >> sys.stderr , 'getting concept'
                                np = 0
                                while np < ld:            # get extent of concept
                                    if ellyChar.isWhiteSpace(d[np]): break
                                    np += 1
                                if np == 0:
                                    _err('missing concept for plausibility')
                                    continue
                                cn = d[:np]               # extract concept
                                d = d[np:]
                            elif c != ' ':
                                _err()                    # signal bad format
                                continue
                        elif ld > 0:
                            _err()                        # unidentifiable trailing text
                            continue

                d = d.strip()                             # rest of definition
#               print 'rest of d=' , d
                if len(d) > 0 and d[-1] == '=':
                    if len(d) == 1 or d[0] != '=':
                        _err('incomplete definition')
                        continue

                ld = [ ]                            # for normalizing definition

                k = 0                               # count spaces removed
                sd = ''                             # previous char seen
                for cd in d:                        # scan all chars in translation
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

                if k > 0:
                    d = ''.join(ld)                 # definition with spaces removed

#               print >> sys.stderr , '3:d=[' + d + ']'

                vrc = [ t , ':' , cat , syf , smf ,
                        pb , cn ]                         # start data record
                vss = u' '.join(vrc)                      # convert to string
                vss += u' ' + d                           # fill out record with rest of input
#               print >> sys.stderr , 'type(vss)=' , type(vss)

#               print >> sys.stderr , 'rec=' , vrc , 'tra=' , d
#               print >> sys.stderr , '   =' , vss

            except ellyException.FormatFailure:
                print >> sys.stderr , '*  at [' , tsave ,
                if dsave != None:
                    print >> sys.stderr , ':' , dsave ,
                print >> sys.stderr , ']'
                continue

#### SQLite
#
            try:
                sql = "INSERT INTO Vocab VALUES(?,?)"
#               print >> sys.stderr , type(wky) , wky , type(vss) , vss
                cur.execute(sql,(wky,vss))
            except dbs.Error , e:
                print >> sys.stderr , 'FATAL' , e
                sys.exit(1)
#
####


#### SQLite
#
        cdb.commit()
        cdb.close()                                   # clean up
#       print >> sys.stderr , 'DONE'
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
        vem    - vocabulary entry matched
        nspan  - match length for phrase selection
        suffx  - suffix disregarded in matching
    """

    def __init__ ( self , vem , nspan , suffx ):

        """
        initialization

        arguments:
            self  -
            vem   - vocabulary entry record
            nspan - character count spanned in match including suffix
            suffx - suffix removed
        """

        self.vem   = vem
        self.nspan = nspan
        self.suffx = suffx

class VocabularyTable(object):

    """
    interface to external data base

    attributes:
        cdb    - SQLite db connection
        cur    - SQLite db cursor
        stm    - stemmer

        string - (inherited from SimpleTransform)

        endg   - any ending removed for match
    """

    def __init__ ( self , name , stem=None ):

        """
        initialization

        arguments:
            self  -
            name  - system name
            stem  - stemmer for matching
        """

        database = name + vocabulary
        self.cdb = None
        self.cur = None
        self.stm = None
        if not os.path.isfile(database):
            return

#### SQLite
#
        try:
            self.cdb = dbs.connect(database)
            self.cur = self.cdb.cursor()
            self.stm = stem
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

        if self.cdb == None: return None

        try:
            rs = [ ]                      # for results

#           print >> sys.stderr , '_ stm=' , self.stm
            akey = key.lower()            # convert to ASCII lower case for lookup

#           print >> sys.stderr , 'key=' , type(akey) ,akey

#### SQLite
#
            sql = "SELECT * FROM Vocab WHERE Keyx = ?"
            self.cur.execute(sql,(akey,))
            tup = self.cur.fetchall()
#
####

#           print >> sys.stderr , 'loop, tup=',tup
            for v in tup:                 # retrieved vocabulary match
                ve = vocabularyElement.VocabularyElement(v)
                rs.append(ve)             # add entry to results

            return rs

        except StandardError , e:
            print >> sys.stderr , 'general error:' , e
            return None

    def doMatchUp ( self , vcs , txs ):

        """
        match current text with vocabulary entry, possibly removing final inflection
        (this method assumes English; override for other languages)

        arguments:
            self  -
            vcs   - vocabulary entry chars
            txs   - text chars to be matched

        returns:
            count of txs chars matched, 0 on mismatch
        """

        self.endg = ''                       # default inflection
        lvc = len(vcs)
        ltx = len(txs)
        tc = txs[-1]                         # last char in text segment
        dnc = ltx - lvc
        nr = icmpr(vcs,txs)                  # do match on lists of chars
#       print 'nr=' , nr , 'dnc=' , dnc
#       print 'txs=' , txs
        if nr > 1:                           # only one missed char allowed
            return 0
        elif nr == 0 and dnc == 0:           # exact match?
            return lvc
        elif nr == 0 and dnc == 2 and txs[-2:] == ['\'' , 's']:
#           print 'apostrophe s'
            self.endg = '-\'s'               # apostrophe + S
            return ltx
        elif lvc < 2:                        # can have inflectional ending?
            return 0
        else:                                # if so, look for one
#           print 'tc=' , tc
            if tc != 's' and tc != 'd' and tc != 'g':
                return 0                     # only -S, -ED, and -ING checked
            m = dnc + nr + 1

            for i in range(m,ltx):
                if txs[-i] == ' ':
                    m += i - 1
                    break
            else:
                m += ltx - 2
            tw = txs[-m:]                    # start of last word in text chars
            sw = self.stm.simplify(tw)       # inflectional stemming
#           print 'sw=' + sw , 'tw=' + tw
            if len(tw) - len(sw) != dnc:     # stemmed result should now align
                return 0                     #   with vocabulary entry
            nr += 1
#           print 'nr=' , nr
            ns = icmpr(vcs[-nr:],sw[-nr:])
            if ns == 0:                      # mismatch gone?
                self.endg = ( '-s'   if tc == 's' else
                              '-ed'  if tc == 'd' else
                              '-ing' )
                return ltx
        return 0

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

        res = [ ]                     # result list initially empty
        rln = 0

        if len(chrs) == 0:
            return res                # empty list at this point

#       print >> sys.stderr , 'chrs=' , type(chrs) , type(chrs[0])

        if keyl < 1:
            return res                # still empty list

        strg = u''.join(chrs[:keyl])

#       print >> sys.stderr , 'vocab first word=' , list(strg) , type(strg)

        vs = self._getDB(strg)        # look up first word in vocabulary table

        if vs == None or len(vs) == 0:
            return res

#       print >> sys.stderr , len(vs) , 'raw entries found'

        lm = len(chrs)                # total length of text for lookup

        for v in vs:                  # look at possible vocabulary matches

#           print >> sys.stderr , 'entry=' , v

            ln = v.length()           # total possible match length for vocabulary entry

#           print >> sys.stderr , 'rln=' , rln , 'ln=' , ln , 'lm=' , lm

            if ln  > lm:              # must be enough text in entry to match
                continue

            k = ln
            while k < lm:
                chrsk = chrs[k]
                if not ellyChar.isLetter(chrsk) and chrsk != '\'': break
                k += 1
#           print >> sys.stderr , 'k=' , k
#           print >> sys.stderr , v.chs , ':' , chrs[:k]
            nm = self.doMatchUp(v.chs,chrs[:k])
            if nm == 0 or nm < rln: continue

#           print >> sys.stderr , 'rln=' , rln , 'ln=' , ln
            if rln < nm:              # longer match than before?
#               print >> sys.stderr , 'new list'
                res = [ ]             # if so, start new result list for longer matches
                rln = nm              # set new minimum match length

            rs = Result(v,nm,self.endg)   # new result object be returned
            res.append(rs)            # add to current result list

        return res                    # return surviving matches

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
        if not isinstance(word,basestring):
            word = u''.join(word)     # make sure argument is list

        lw = len(word)
        if lw == 0:
            return ves                # empty list at this point

        vs = self._getDB(word)        # look up first word in vocabulary table

        if vs == None or len(vs) == 0:
            return ves

        for v in vs:                  # look at possible vocabulary matches

            if lw == v.length():
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
#   print >> sys.stderr , 'vc=' , vc
#   print >> sys.stderr , 'tc=' , tc[:k]
    for i in range(k):
#       print i , vc[i] , tc[i]
        if vc[i].lower() != tc[i].lower(): return k - i
    return 0

#
# unit test and standalone database building
#

if __name__ == '__main__':

    import ellyDefinitionReader
    import ellyConfiguration
    import inflectionStemmerEN
    import symbolTable

    from ellyPickle import load
    from ellyBase   import rules

    from generativeDefiner import showCode

    def check ( vtb , ts , kl=None ):
        """ lookup method for unit testing
        """
        if kl == None: kl = len(ts)
        rs = vtb.lookUp(ts,kl)               # check for possible vocabulary matches
        print 'for' , '"' + u''.join(ts) + '"' ,
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

    try:
        if ellyConfiguration.language == 'EN':
            ustem = inflectionStemmerEN.InflectionStemmerEN()
        else:
            ustem = None
    except ellyException.TableFailure:
        print >> sys.stderr , 'inflectional stemming failure'
        sys.exit(1)

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
        compile(nams,ustb,inp)             # create database from vocabulary table
    except ellyException.TableFailure:
        print >> sys.stderr , 'exiting'
        sys.exit(1)                        # quit on failure

    uvtb = VocabularyTable(nams,ustem) # load vocabulary table just created

    ucdb = uvtb.cdb                        # get database for table
    if ucdb == None:
        print >> sys.stderr , 'no vocabulary table found'
        sys.exit(1)

    nu = 0

#### SQLite
#
    try:
        ucur = ucdb.cursor()
        usql = "SELECT * FROM Vocab"
        ucur.execute(usql)
        resl = ucur.fetchall()
    except dbs.Error , e:
        print >> sys.stderr , 'cannot access vocabulary table'
        sys.exit(1)
#
####

    hk = { }
    for ur in resl:
        hk[ur[0]] = 0
    unqk = hk.keys()
    print len(unqk) , 'unique DB keys\n'
    print 'looking up each DB key as SINGLE-word vocabulary entry'
    for ky in unqk:
        if nu >= limt: break
        nu += 1
        check(uvtb,list(ky))                # dump all info for each key
        print ''

    print 'enter SINGLE- and MULTI-word terms to look up in table'
    while True:                        # now look up terms from standard input
        sys.stdout.write('> ')
        ul = sys.stdin.readline()      # get test example to look up
        if len(ul) <= 1: break
        ssx = ul.strip().decode('utf8')
        tsx = list(ssx)                # get list of chars
        kn = toIndex(ssx)              # get part of term for indexing
        if kn == 0:                    # if none, cannot look up
            print 'index NOT FOUND:' , ssx
            continue
        print 'DB key=' , tsx[:kn]
        check(uvtb,tsx,kn)
        print ''

    sys.stdout.write('\n')
