#!/usr/local/bin/python
# PyElly - scripting tool for analyzing natural language
#
# vocabularyTable.py : 03jul2014 CPM
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
Elly vocabulary database support using open-source BdB package
"""

import os
import sys

try:  # get Python support for Berkeley DB
    from bsddb3 import db
except:
    print >> sys.stderr , 'bsddb3 unavailable'
    db = None

##
## The Berkeley DataBase (BdB) package and the bsddb3 module are both required
## here, but are not in the standard Python distribution. You must download and
## install both BDB and bsddb3 yourself before you can run any Elly vocabulary
## database modules. How to do this will vary according to your operating system
## and your particular release of Python.
##
## This code was developed with BSD 5.3.1 and bsddb3 6.0.0 with Python 2.7.5
## under Mac OS X 10.8.5 (Mountain Lion) and 10.9.3 (Mavericks).
##

import ellyChar
import vocabularyElement
import unicodedata

import syntaxSpecification
import featureSpecification

SSpec = syntaxSpecification.SyntaxSpecification
FSpec = featureSpecification.FeatureSpecification

lcAN = lambda x: unicodedata.normalize('NFKD',x).encode('ascii','ignore').lower()

vocabulary = '.vocabulary.elly.bin' # compiled vocabulary file suffix
source     = '.v.elly'              # input vocabulary text file suffix

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

def err ( ):

    """
    for error handling

    arguments:
    """

    raise RuntimeError('bad vocabulary format')

def compile ( name , stb , defn , stem=None ):

    """
    static method to create an Elly vocabulary database from text file input

    arguments:
        name  - for new BSDDB database
        stb   - Elly symbol table
        defn  - Elly definition reader for vocabulary
        stem  - optional stemmer for indexing

    returns:
        True on success, False otherwise
    """

#   print >> sys.stderr , 'compiled stb=' , stb , 'stem=' , stem , 'db=' , db

    if stb == None or db == None: return False

    zfs = FSpec(stb,'[$]',True).positive.hexadecimal(False)

#   print >> sys.stderr 'zfs=' , zfs                 # hexadecimal for all features off

    try:
        file = name + vocabulary                     # where to put vocabulary database
        try:
            os.remove(file)                          # delete the file if it exists
        except:
            print >> sys.stderr , 'no' , file
        dbs = db.DB()                                # create new database
        dbs.set_flags(db.DB_DUP)                     # keys may identify multiple records
        dbs.open(file,None,db.DB_HASH,db.DB_CREATE)  # open new database file
#       print >> sys.stderr , 'creating' , file

        while True:                                  # process vocabulary records

            try:
#               print >> sys.stderr , '------------'
                r = defn.readline()                       # next definition
                if len(r) == 0: break                     # stop on EOF
                if r[0] == '#': continue                  # skip comment line
#               print >> sys.stderr , 'def=' , r

                k = r.find(':')                           # look for first ':'
                if k < 0: err()                           # quit on failure here

                t = r[:k].strip()                         # term to go into dictionary
                d = r[k+1:].strip()                       # its definition

#               print >> sys.stderr , ' tm=' , '<' + t + '>' , 'df=' , '<' + d + '>'
                if len(t) == 0 or len(d) == 0: err()      # quit on missing parts

                n = toIndex(t)                            # get part of term to index
                if n == 0: err()   
                w = t[:n]                                 # first word of term to define  
                if stem != None:
                    w = stem.simplify(w)                  # reduce for lookup key
#               print >> sys.stderr , '  w=' , w
                lcw = lcAN(w)                             # convert to ASCII lower case
#               print >> sys.stderr , 'lcw=' , lcw

                ns = syntaxSpecification.scan(d)          # find extent of syntax info
#               print >> sys.stderr , 'ns=' , ns
                if ns <= 0: err()
#               print >> sys.stderr , 'PoS=' , d[:ns]

                syn = d[:ns]                              # syntax info as string
                d = d[ns:].strip()                        # rest of definition

                ss = SSpec(stb,syn)                       # decode syntax info to get
                cat = str(ss.catg)                        #   syntax category
                syf = ss.synf.positive.hexadecimal(False) #   syntactic flags
#               print >> sys.stderr , 'syf=' , syf

                smf = zfs                                 # initialize defaults for
                pb = '0'                                  #   cognitive semantics
                cn = '-'                                  #

#               print >> sys.stderr , '0:d=\[' + d + '\]'
                if len(d) > 1:                            # check for cognitive semantics
                    x = d[0]
                    if x == '[' or x == '0' or x == '-':  # semantic features?
                        if x != '[':                      # a '0' or '-' means to take default
                            if len(d) == 1 or d[1] != ' ': err()
                            d = d[2:].strip()             # skip over
                        else:
                            ns = featureSpecification.scan(d) # look for ']' of features
#                           print >> sys.stderr , 'ns=' , ns
                            if ns < 0: err()
                            sem = d[:ns]                  # get semantic features
                            d = d[ns:].strip()            # skip over
                            fs = FSpec(stb,sem,True)
                            smf = fs.positive.hexadecimal(False) # convert to hex
#                           print >> sys.stderr , 'smf=' , smf

#                       print >> sys.stderr , '1:d=\[' + d + '\]'
                        ld = len(d)
#                       print >> sys.stderr , 'ld=' , ld
                        if ld == 0: err()                 # expecting plausibility
                        np = 0
                        x = d[np]
                        if x == '+' or x == '-':
                            np += 1                       # take any plus or minus sign
                        while np < ld:                    # and successive digits
                            if ellyChar.isDigit(d[np]): np += 1
                            else: break
#                       print >> sys.stderr , 'np=' , np
                        if np == 0: err()
                        pb = d[:np]                       # plausibility bias
#                       print >> sys.stderr , 'pb=' , pb
                        d = d[np:]
                        ld = len(d)
#                       print >> sys.stderr , '2:d=\[' + d + '\]'
                        if ld > 1:                        # any more to process?
                            c = d[0]                      # get next char after bias
                            d = d[1:]                     # advance scan
                            ld -= 1
                            if c == '/':                  # check for explicit concept
                                np = 0
                                while np < ld:            # get extent of concept
                                    if ellyChar.isWhiteSpace(d[np]): break
                                    np += 1
                                cn = d[:np]               # extract concept
                                d = d[np:]
                            elif c != ' ':
                                err()                     # signal bad format

                d = d.strip()                             # rest of definition

#               print >> sys.stderr , '3:d=\[' + d + '\]'

                vrc = [ t , ':' , cat , syf , smf ,
                        pb , cn ]                         # start BdB data record
                vss = u' '.join(vrc)                      # convert to string
                vss += u' ' + d                           # fill out record with rest of input
#               print >> sys.stderr , 'type(vss)=' , type(vss)
                rss = vss.encode('utf8')                  # convert to UTF-8

#               print >> sys.stderr , 'rec=' , vrc , 'tra=' , d
#               print >> sys.stderr , '   =' , rss

            except Exception , e:
                sys.stderr.write('exception: ')
                sys.stderr.write(str(e) + '\n')
                sys.stderr.write('  [' + r + ']\n')
                continue

            dbs.put(lcw,rss)                          # save in database

#       print >> sys.stderr , 'DONE'
        dbs.close()                                   # clean up and return
        return True

    except Exception , e:
        sys.stderr.write('database exception: ')
        sys.stderr.write(str(e) + '\n')
        return False                                  # note failure

class Result(object):

    """
    structured data to return as result of search

    attributes:
        mtchl  - match length for phrase selection
        dropn  - count of chars to omit for token
        suffx  - suffix disregarded in matching
        restr  - replacement for last char in any token
    """

    def __init__ ( self ):

        """
        initialization

        arguments:
            self
        """

        self.mtchl = 0
        self.dropn = 0
        self.suffx = u''
        self.restr = None

class VocabularyTable(object):

    """
    interface to external data base

    attributes:
        dbs    - BdB database object via bsddb3
        cur    - database cursor object
        stm    - stemmer

        string - (inherited from SimpleTransform)
    """

    def __init__ ( self , name , stem=None ):

        """
        initialization

        arguments:
            self  -
            name  - system name
            stem  - stemmer for simplification
        """

        database = name + vocabulary

        if db == None:
            self.dbs = None
            self.cur = None
            self.stm = None
        else:
            self.dbs = db.DB()   # define database object
            try:
                self.dbs.open(database,None,db.DB_HASH,db.DB_RDONLY)
                self.cur = self.dbs.cursor()
                self.stm = stem
#               print >> sys.stderr , 'stm=' , self.stm
            except Exception , e:
                print >> sys.stderr, 'cannot access database'
                print >> sys.stderr, e
                self.dbs = None
                self.cur = None
                self.stm = None

    def __del__ ( self ):

        """
        cleanup

        arguments;
            self
        """

        if self.dbs != None:
            self.dbs.close()  # close database file for completeness

    def _getDB ( self , key ):

        """
        get list of records associated with specified key

        arguments:
            self  -
            key   - string value for lookup

        returns:
            data records if successful, None otherwise
        """

        if self.dbs == None: return None

        try:
            rs = [ ]                      # for results

#           print >> sys.stderr , '_ stm=' , self.stm
            if self.stm != None:
#               print >> sys.stderr , '_ stm=' , self.stm
                key = self.stm.simplify(key)
            akey = lcAN(key)              # convert to ASCII lower case for lookup

#           print >> sys.stderr , 'key=' , type(akey) ,akey
            tup = self.cur.set(akey)      # note cursor get() called here!

#           print >> sys.stderr , 'loop, tup=',tup
            while tup:                    # break when tup is None
                ve = vocabularyElement.VocabularyElement(tup)
                rs.append(ve)             # add entry to results
                tup = self.cur.next_dup() # get next entry with same key, if any
#               print >> sys.stderr , 'tup=',tup

            return rs

        except Exception , e:
            print >> sys.stderr , 'error:' , e
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

        res = [ ]                     # result list initially empty
        rln = 0

        if len(chrs) == 0:
            return res                # empty list at this point

#       print >> sys.stderr , 'chrs=' , type(chrs) , type(chrs[0])

        if keyl < 1:
            return res                # still empty list

        strg = u''.join(chrs[:keyl])
        if self.stm != None:
            strg = self.stm.simplify(strg)

#       print >> sys.stderr , type(strg)
#       print >> sys.stderr , 'vocab first word=' , list(strg)

        vs = self._getDB(strg)        # look up first word in vocabulary table

        if vs == None or len(vs) == 0:
            return res

#       print >> sys.stderr , len(vs) , 'raw entries found'

        lm = len(chrs)                # total length of text for matching

        for v in vs:                  # look at possible vocabulary matches

            nx = 0                    # extra chars for any match
            ln = v.length()           # total possible match length for vocabulary entry

            if rln > ln:
                continue              # reject if longer match already found

            if ln > lm:               # must be enough text to match
                continue

            rs = Result()             # new result object

            k = ln
#           print >> sys.stderr , v.chs , ':' , chrs[:k]
            if not _cmp(v.chs,chrs[:k]):   # do match on lists of chars
                lk = k - 1
#               print >> sys.stderr , 'no match lk=' , lk
                tc = chrs[lk]
                vc = v.chs[lk]
#               print >> sys.stderr , 'vc=' , vc , 'tc=' , tc
                if ( vc == 'y' and tc == 'i' or  # 
                     vc == 'e' and tc == 'i' ):  #
#                   print >> sys.stderr , v.chs[:lk] , ':' , chrs[:lk]
                    if not _cmp(v.chs[:lk],chrs[:lk]):
                        continue
                    rs.restr = vc
                else:
                    continue

#           print >> sys.stderr , 'preliminary match'
            r = chkT(chrs,k)          # confirm match in wider context

            if r == None: continue

            ln += r[0]                # adjust match length to include extra chars

#           print >> sys.stderr , 'rln=' , rln , 'ln=' , ln
            if rln < ln:              # longer match than before?
#               print >> sys.stderr , 'new list'
                res = [ ]             # if so, start new result list for longer matches
                rln = ln              # set new minimum match length

            rs.mtchl = ln             # collect results
            rs.dropn = r[0]
            rs.suffx = r[1]
            res.append([v,rs])        # add to current result list

        return res                    # return surviving matches

    def lookUpWord ( self , word ):

        """
        look word up in vocabulary table

        arguments:
            self  -
            word  - text char string

        returns:
            list of VocabularyElement objects
        """

        ves = [ ]                     # result list initially empty

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

def _cmp ( ve , tx ):

    """
    compare vocabulary entry to text with partial case sensitivity

    arguments:
        ve    - vocabulary chars
        tx    - text chars

    returns:
        True on match, False otherwise
    """

#   print >> sys.stderr , 've=' , ve
#   print >> sys.stderr , 'tx=' , tx
    if ve == tx:                      # straight char comparison
        return True
    tx = map(lambda x: x.lower(),tx)  # if no match, convert text to lower case
#   print >> sys.stderr , '    ve=' , ve
#   print >> sys.stderr , 'new tx=' , tx
    if ve == tx:                      # compare again
        return True
    else:
        return False

def chkT ( chrs , k ):

    """
    check for full match of vocabulary term with adjustments for
    simple inflectional endings (for English only! Override as needed))

    arguments:
        chrs  - input char list
        k     - extent of match

    returns:
        tuple of extra actions: [ skip , back ] on success, None otherwise
          skip = count of following chars to be added to match
          back = suffix chars to restore to input
    """

    ns = 0                         # skip count
    sx = ''                        # string to put back

    n = len(chrs) - k              # remaining chars in input
#   print n , 'more chars in input'
    if n == 0:
         return [ ns , sx ]        # match on no more chars

    lc = chrs[k-1]                 # last matched char
    c  = chrs[k]                   # next char in input
    cs = chrs[k+1:]                # rest of input after that
#   print 'match with lc=' , lc , 'c=' , c , 'n=' , n

    if not ellyChar.isLetterOrDigit(c) and c != "'":
        return [ ns , sx ]         # simple successful result

    if c == lc:                    # doubled char?
        if c == 's':
            return None            # s -s mismatch not allowed
        ns += 1                    # skip over doubled char otherwise
        c  = cs[0]                 #
        cs = cs[1:]                #
        n -= 1                     #
#   print 'match with lc=' , lc , 'c=' , c , 'n=' , n

    if c == "'":                   # possible -'s ending?
        if n == 1:
            return [ ns , sx ]     # successful result
        elif cs[0] == 's':
            ns = 2
            sx = u"'s"
            tm = cs[1] if n > 2 else ' '
    elif c == 's':                 # possible -s ending?
        ns = 1
        sx = u's'                  # for -s
        tm = cs[0] if n > 1 else ' '
    elif c == 'e':                 # possible -es or -ed ending?
        if n == 1:
            return None
        cn = cs[0]                 # look at char past -e
        ns += 2
        tm = cs[1] if n > 2 else ' '
        if cn == 's':
            sx = u's'              # for -s
        elif cn == 'd':
            sx = u'ed'             # for -ed
        else:
            return None
    elif c == 'd':                 # possible -d ending?
        if lc != 'e':
            return None
        ns = 1
        tm = cs[0] if n > 1 else ' '
        sx = u'ed'                 # for -ed
    elif c == 'i':                 # possible -ing ending?
        if n < 3 or cs[0] != 'n' or cs[1] != 'g':
            return None
        ns += 3
        tm = cs[2] if n > 3 else ' '
        sx = u'ing'                # for -ing
    elif c == 'n':                 # possible -ing ending?
        if lc !='i' or n < 2 or cs[0] != 'g':
            return None
        ns += 2
        tm = cs[1] if n > 3 else ' '
        sx = u'ing'
    else:
        return None

    if ellyChar.isLetterOrDigit(tm):
        return None                # no match after disregarding inflections

    return [ ns , sx ]             # successful result with later adjustment needed

#
# unit test and standalone database building
#

if __name__ == '__main__':

    import ellyBase
    import ellyDefinitionReader
    import ellyConfiguration
    import inflectionStemmerEN
    import symbolTable

    from generativeDefiner import showCode

    def look ( vtb , ts , kl ):
        vs = vtb.lookUp(ts,kl)               # check for possible vocabulary matches
        if len(vs) == 0:                     # any vocabulary entries found?
            print ts[:kl] , 'NOT FOUND'
        else:
            print ts[:kl] , 'FOUND' , len(vs)
            for v in vs:                     # if found, note each entry
                rec = v[0]
                vrs = v[1]
                print '=' , unicode(rec)     # show each match
                print ' ' , vrs.mtchl , 'chars matched, with' , vrs.dropn , 'extra'
                print '  suffix=' , '[-' +  vrs.suffx + ']' , 'restore=' , vrs.restr
                print 'generative semantics'
                showCode(rec.gen.logic)
            print '--'

    if ellyConfiguration.language == 'EN':
        stem = inflectionStemmerEN.InflectionStemmerEN()
    else:
        stem = None

    name = sys.argv[1] if len(sys.argv) > 1 else 'test'
    dfns = name + source
    limt = sys.argv[2] if len(sys.argv) > 2 else 24

    erul = ellyBase.load(name + ellyBase.rules)     # get pickled Elly rules
    if erul == None:
        stb = symbolTable.SymbolTable()             # if none, make new symbol table
    else:
        stb = erul.stb                              # otherwise, grab existing symbol table

    print 'source=' , dfns
    inp = ellyDefinitionReader.EllyDefinitionReader(dfns)

    f = compile(name,stb,inp,stem)     # create database from vocabulary table
    print 'compile=' , f
    if not f:                          # check for success
        print 'compilation FAILed'
        sys.exit()                     # quit on failure
    vtb = VocabularyTable(name,stem)   # load vocabulary table just created
    dbs = vtb.dbs                      # get database for table
    dst = dbs.stat()                   # get its BdB status
    dks = dst.keys()                   # all status tags 
    print '---- BdB status'
    for dk in dks:
        print '{0:12s} {1}'.format(dk,dst[dk])
    print '----'

    n = 0
    keys = dbs.keys()                  # all database keys
    for key in keys:
        if n >= limt: break
        n += 1
        lky = list(key)
        look(vtb,lky,len(key))         # dump all info for each key
        key = u''.join(lky)
#       print 'type(key)=' , type(key)
        vs = vtb.lookUpWord(key)       # look up just key
        nm = len(vs)
        print nm , 'key match' + ('' if nm == 1 else 'es')
        print ''

    print 'enter terms to look up'
    while True:                        # now look up terms from standard input
        sys.stdout.write('> ')
        s = sys.stdin.readline()       # get test example to look up
        if len(s) <= 1: break
        ss = s.strip().decode('utf8')
        ts = list(ss)                  # get list of chars
        k = toIndex(ss)                # get part of term for indexing
        if k == 0:                     # if none, cannot look up
            print 'index NOT FOUND:' , ss
            continue
        look(vtb,ts,k)
        ky = u''.join(ts[:k])
        vs = vtb.lookUpWord(ky)        # look up just key
        print len(vs) , 'key match only'


    sys.stdout.write('\n')
