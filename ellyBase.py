#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBase.py : 23oct2018 CPM
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
integrating PyElly components into a language processing tool to handle input
consisting of a single sentence on a single line with no \n chars
"""

import sys
import ellySession
import ellyConfiguration
import ellyDefinition
import ellyPickle
import ellyToken
import ellyChar
import ellyException
import substitutionBuffer
import parseTree
import parseTreeBottomUp
import parseTreeWithDisplay
import interpretiveContext
import entityExtractor
import simpleTransform
import nameRecognition
import punctuationRecognizer
import conceptualHierarchy
import vocabularyTable
import symbolTable

import os   # needed to get file modification times

# binary files created, saved, and reloaded

rules      = ellyDefinition.grammar     # for saving grammar rules
vocabulary = vocabularyTable.vocabulary # for saving built vocabulary

_session = '.session.elly.bin'          # for saving session information

# source text file suffixes for language definition rules

_rules      = [ '.g.elly' , '.m.elly' , '.p.elly' , '.t.elly' , '.n.elly' , '.h.elly' ,
                '.stl.elly' , '.ptl.elly' ]
_vocabulary = [ vocabularyTable.source ]

noParseTree = False                     # enable parse tree stub for debugging

# version ID

release = 'v1.5.4'                      # current version of PyElly software

def _timeModified ( basn , filn ):

    """
    get file modification time

    arguments:
        file  - pathname

    returns:
        integer number of seconds since base time if filn exists, 0 otherwise

    exceptions:
        OSError
    """

    pathn = basn + filn
#   print 'time check:' , pathn
    if os.path.isfile(pathn):
        return int(os.path.getmtime(pathn))
    else:
        return 0       # i.e. really, really old

def _isSaved ( systm , compn , srcs ):

    """
    check whether a definition for an Elly system has been saved

    arguments:
        systm - root name of Elly system
        compn - what to check
        srcs  - what sources to check against

    returns:
        True if it has been saved, False otherwise
    """

    try:
        date = _timeModified('./',systm + compn)
    except OSError:
        print >> sys.stderr , '**** time error on' , compn
        return False

    basn = ellyConfiguration.baseSource

    for f in srcs:
        try:
            d = _timeModified(basn,systm + f)
        except OSError:
            continue      # ignore inaccessible files
#       print f , ' d=' , d , 'date=' , date
        if d >= date:
#           print 'file' , f , 'changed'
            return False
    return True

def _notVocabularyToDate ( system ):

    """
    check vocabulary versus grammar time stamps

    arguments:
        system - application ID

    returns:
        True if vocabulary older, False otherwise
    """

    aid = './' + system
    try:
        rt = _timeModified(aid,rules)
        vt = _timeModified(aid,vocabulary)
#       print 'rt=' , rt , 'vt=' , vt
    except OSError:
        print >> sys.stderr , 'rule+vocabulary time exception!'
        return True
    return vt <= rt

########
# ParseTree stubs for debugging without parse tree building
#

class NoParseTree(parseTreeBottomUp.ParseTreeBottomUp):
    def __init__ ( self , stb , gtb , ptb , ctx ):
        print type(ctx)
        self.ctx = ctx
        self.queue = [ None ]
        super(NoParseTree,self).__init__(stb,gtb,ptb)
    def startUpX  ( self ):
        print >> sys.stderr , 'startUpX'
    def finishUpX ( self ):
        print >> sys.stderr , 'finishUpX'
    def digest ( self ): pass
    def restartQueue ( self ):
        self.queue = [ None ]
    def enqueue ( self , ph ):
        print >> sys.stderr , unicode(ph)
    def requeue ( self ) : pass
    def showTokens ( self ): pass
    def evaluate ( self , ctx ):
        ln = ctx.countTokensInListing()
        print >> sys.stderr , ''
        for i in range(ln):
            tok = ctx.getNthTokenInListing(i)
            print >> sys.stderr , i , ':' , tok.getOrig()
        return True
    def getLastPlausibility ( self ): return 0
    def goalCheck ( self , typ , gbs ):
        print >> sys.stderr , 'goalCheck typ=' , typ
        return True

#
# main class for processing single sentences, presented without NL's
#

class EllyBase(object):

    """
    base class for sentence analysis and rewriting

    attributes:
        ptr  - parse tree
        sbu  - input buffer with macro substitutions
        vtb  - vocabulary table
        rul  - grammar definitions
        pat  - pattern definitions
        ses  - session definitions
        ctx  - interpretive context
        iex  - entity extractor
        trs  - simple transformation
        pnc  - punctuation recognizer

        gundef - undefined symbols in *.p.elly and *.n.elly
        vundef - undefined symbols in *.v.elly
        pundef - undefined symbols for punctuation recognition
        eundef - undefined symbols in information extractors
    """

    def __init__ ( self , system , restore=None ):

        """
        initialization

        arguments:
            system   - root name for PyElly tables to load
            restore  - name of session to continue
        """

        nfail = 0          # error count for reporting
        self.rul = None

        self.gundef = [ ]  # record orphan symbols by module
        self.vundef = [ ]  #
        self.pundef = [ ]  #
        self.eundef = [ ]  #

#       print 'EllyBase.__init__()'
#       aid = './' + system
#       try:
#           print 'a rul time=' , _timeModified(aid,rules)
#           print 'a voc time=' , _timeModified(aid,vocabulary)
#       except:
#           print '\n**** a rul or voc time exception'

        sysf = system + rules
        redefine = not _isSaved(system,rules,_rules)
#       print '0 redefine=' , redefine
        try:
            self.rul = ellyDefinition.Grammar(system,redefine,release)
        except ellyException.TableFailure:
            nfail += 1
        if nfail == 0:
            self.gundef = self.rul.stb.findUnknown()
            if redefine:
                ellyPickle.save(self.rul,sysf)

#       try:
#           print 'b rul time=' , _timeModified(aid,rules)
#           print 'b voc time=' , _timeModified(aid,vocabulary)
#       except:
#           print '\n**** b rul or voc time exception'

#       print '1 redefine=' , redefine
        if restore != None:
            self.ses = ellyPickle.load(restore + '.' + system + _session)
        else:
            self.ses = ellySession.EllySession()

        s = self.ses  # session info
        d = self.rul  # language rules

#       print '0:' , len(d.stb.ntname) , 'syntactic categories'

        mtb = d.mtb if d != None else None
        self.sbu = substitutionBuffer.SubstitutionBuffer(mtb)

        try:
            inflx = self.sbu.stemmer
#           print 'inflx=' , inflx
        except AttributeError:
            inflx = None
#       print 'inflx=' , inflx
        if d != None:
            d.man.suff.infl = inflx   # define root restoration logic

#       print '2 redefine=' , redefine
        if not redefine:
            if not _isSaved(system,vocabulary,_vocabulary) or _notVocabularyToDate(system):
                redefine = True

        stb = d.stb if d != None else symbolTable.SymbolTable()

#       print self.rul.stb
#       print stb

        if nfail > 0:
            print >> sys.stderr , 'exiting: table generation FAILures'
            sys.exit(1)

#       print '1:' , len(stb.ntname) , 'syntactic categories'

        self.ctx = interpretiveContext.InterpretiveContext(stb,d.gtb.pndx,s.globals,d.hry)

        for z in d.gtb.initzn:        # initialize global symbols for parsing
            self.ctx.glbls[z[0]] = z[1]

#       print '2:' , len(stb.ntname) , 'syntactic categories'

        self.pnc = punctuationRecognizer.PunctuationRecognizer(stb)
        self.pundef = stb.findUnknown()

#       print '3:' , len(stb.ntname) , 'syntactic categories'

        nto = len(stb.ntname)         # for consistency check

        if noParseTree:
            self.ptr = NoParseTree(stb,d.gtb,d.ptb,self.ctx)
        elif ellyConfiguration.treeDisplay:
            self.ptr = parseTreeWithDisplay.ParseTreeWithDisplay(stb,d.gtb,d.ptb,self.ctx)
        else:
            self.ptr = parseTree.ParseTree(stb,d.gtb,d.ptb,self.ctx)

        ntabl = d.ntb

        if ntabl != None and ntabl.filled():
            nameRecognition.setUp(ntabl)
            ellyConfiguration.extractors.append( [ nameRecognition.scan , 'name' ] )

        self.iex = entityExtractor.EntityExtractor(self.ptr,stb) # set up extractors

        self.eundef = stb.findUnknown()

        if ellyConfiguration.rewriteNumbers:
            self.trs = simpleTransform.SimpleTransform()
        else:
            self.trs = None           # no automatic conversion of written out numbers

#       print '4:' , len(stb.ntname) , 'syntactic categories'

#       print '3 redefine=' , redefine
        if redefine: print 'recompiling vocabulary rules'
        try:
            voc = ellyDefinition.Vocabulary(system,redefine,stb)
        except ellyException.TableFailure:
            voc = None
            nfail += 1

        if ellyConfiguration.treeDisplay:
            print "tree display ON"
        else:
            print "tree display OFF"

#       try:
#           print 'c rul time=' , _timeModified(aid,rules)
#           print 'c voc time=' , _timeModified(aid,vocabulary)
#       except:
#           print 'rul or voc time exception'

#       print 'vundef=' , self.vundef
        if voc != None: self.vtb = voc.vtb
        self.vundef = stb.findUnknown()
#       print 'vundef=' , self.vundef

        ntn = len(stb.ntname)         # do consistency check on syntactic category count
        if nto != ntn:
            print >> sys.stderr , ''
            print >> sys.stderr , 'WARNING: grammar rules should predefine all syntactic categories'
            print >> sys.stderr , '         referenced in language definition files'
            for i in range(nto,ntn):
                print >> sys.stderr , '        ' , stb.ntname[i].upper() , '=' , i
            print >> sys.stderr , ''

        if nfail > 0:
            print >> sys.stderr , 'exiting: table generation FAILures'
            sys.exit(1)

        sys.stderr.flush()

#       print 'EllyBase.__init__() DONE'

    def setGlobalVariable ( self , var , val ):

        """
        set global variable for grammar at startup

        arguments:
            self  -
            var   - variable name
            val   - assigned value
        """

        self.ctx.glbls[var] = val

    def translate ( self , text , plsb=False ):

        """
        Elly processing loop for text input

        arguments:
            self  -
            text  - list of Unicode chars to translate
            plsb  - flag to show plausibility score in output

        returns:
            rewritten input on success, None otherwise
        """

#       print 'EllyBase.translate()'
        self.ptr.reset()                # empty out any previous parse tree
        self.ctx.reset()                # empty out any previous context

        if len(text) == 0:              # if no text, done
            return ''
#       print 'list' , list(text)
        self.sbu.refill(text)           # put text to translate into input buffer

        try:
            while True:
#               print 'BASE@0 current text chars=' , self.sbu.buffer
                if len(self.sbu.buffer) == 0:
                    break               # stop when sentence buffer is empty
                self.ptr.startUpX()     # for any initial ... grammar rule
#               print 'BASE@1 =' , self.sbu.buffer
                if not self._lookUpNext():
                    print >> sys.stderr , 'lookup FAILure'
                    self .ptr.showTokens(sys.stderr)
                    return None         # if next token caused error, quit
#               print 'BASE@2 =' , self.sbu.buffer
                if len(self.ptr.queue) == 0:
                    break
#               print 'BASE@3 =' , self.sbu.buffer
                self.ptr.digest()       # process queue to get all ramifications
#               print 'digested phrase limit=' , self.ptr.phlim
                self.ptr.restartQueue() # for any leading zero production
#               print self.ctx.countTokensInListing() , 'token(s) after digestion'
#               print 'digested phrases=' ,self.ptr.phlim
#               print 'BASE@4 =' , self.sbu.buffer
                self.sbu.skipSpaces()

            self.ptr.finishUpX()        # for any trailing ... grammar rule
        except ellyException.ParseOverflow:
            print >> sys.stderr , 'parse FAILed! overflow'
            self.ptr.showTokens(sys.stderr)
            return None

#       print 'evaluate'
        if not self.ptr.evaluate(self.ctx):
            return None                 # translation fails
#       print 'parse and evaluation succeeds'
        self.ctx.mergeBuffers()
#       self.ctx.printStatus()

        if plsb:                        # show plausibility in output if requested
            s = '=' + str(self.ptr.getLastPlausibility())
            if self.ctx.cncp != conceptualHierarchy.NOname:
                cnm = self.ctx.wghtg.hiery.generalize(self.ctx.cncp)
                s += ' ' + cnm
                c = self.ctx.wghtg.hiery.getConcept(cnm)
                if c != None and len(c.alias) > 0:
                    s += '=' + c.alias[0]
            s += ": "
            self.ctx.prependCharsInCurrentBuffer(s)

        return self.ctx.getBufferContent() # translated string

    def _lookUpNext ( self ):

        """
        look up possible next segments in input buffer by various means,
        keeping tokens only for the LONGEST segment

        arguments:
            self

        returns:
            True on successful lookup, False otherwise

        exceptions:
            ParseOverflow
        """

        self.sbu.skipSpaces()          # skip leading spaces
        s = self.sbu.buffer
#       print '_lookUp@0 buffer=' , s

        if len(s) == 0:                # check for end of input
            return False               # if so, done

#       print 'in =' , unicode(self.sbu)
        if self.trs != None:           # preanalysis of number expressions
            self.trs.rewriteNumber(s)

#       print '_lookUp@1 buffer=' , self.sbu.buffer
#       print 'macro expansion s[0]=' , s[0]
        self.sbu.expand()              # apply macro substitutions
#       print 'macro expanded  s[0]=' , s[0]
#       print '_lookUp@2 buffer=' , self.sbu.buffer

        s = self.sbu.buffer

#       print 'expanded len=' , len(s)
        if len(s) == 0: return True    # macros can empty out buffer

        k = self.sbu.findBreak()       # find extent of first component for lookup
        if k == 0:
            k = 1                      # must have at least one char in token

#       print 'break at k=' , k
        kl = len(s)
        if  k + 1 < kl and s[k] == '+' and s[k+1] == ' ':
            k += 1                     # recognize possible prefix

#       print 'len(s)=' , kl , 'k=' , k , 's=', s

#       print '_lookUp@3 buffer=' , self.sbu.buffer
        mr = self._scanText(k)         # text matching in various ways
        mx  = mr[0]                    # overall maximum match length
        chs = mr[1]                    # any vocabulary element matched
        suf = mr[2]                    # any suffix removed in matching
#       print '_lookUp@4 buffer=' , self.sbu.buffer
        s = self.sbu.buffer
#       print 'k=' , k
#       print 'scan result mx=' , mx , 'chs=' , chs , 'suf=' , suf
#       print 'len(s)=' , len(s) , 's=' , s

        if ( k < mx or
             k == mx and suf != '' ):  # next word cannot produce token as long as already seen?

#           print 'queue:' , len(self.ptr.queue)
#           print 'chs=' , chs
            if len(chs) > 0:           # any vocabulary matches?
#               print 'put back' , suf , mx , s
                self.sbu.skip(mx)      # if so, they supersede
                if suf != '':          # handle any suffix removal
                    self.sbu.prepend(list(suf))
#                   print 'suf=' , suf
            else:
                chs = self.sbu.extract(mx)
#               print 'extracted chs=' , chs
#           print 'token chs=' , chs
            to = ellyToken.EllyToken(chs)
#           print 'long token=' , unicode(to)
            self.ctx.addTokenToListing(to)
            if suf != '':
                if not ellyChar.isApostrophe(suf[1]):
                    to.dvdd = True     # must note suffix removal for token!
#           print 'only queue:' , len(self.ptr.queue)
            return True

#       print 'mx=' , mx
#       print 'plus queue:' , len(self.ptr.queue)
        wsk = self.sbu.buffer[:k]
        cap = ellyChar.isUpperCaseLetter(wsk[0])
#       print 'wsk=' , wsk
        rws = u''.join(wsk)
        found = self.ptr.createPhrasesFromDictionary(rws.lower(),False,cap)
        if not found:
#           print 'not found, k=' , k
            if k > mx and k > 1 and ellyChar.isEmbeddedCombining(rws[-1]):
                k -= 1
                rws = rws[:-1]
                found = self.ptr.createPhrasesFromDictionary(rws.lower(),False,cap)
#       print 'found in dictionary=' , found
        if found or mx > 0:            # match found in dictionary or by text scan
            if not found:
                k = mx                 # if by text scan, must make token longer
                rws = rws[:k]          # if mx > k
            self.sbu.skip(k)
#           print 'next=' , self.sbu.buffer[self.sbu.index:]
#           print 'queue after =' , len(self.ptr.queue)
            to = ellyToken.EllyToken(rws[:k])
            if len(suf) > 1:           # change token to show suffix properly
#               print 'suf=' , suf
                cs = suf[1]            # first char in suffix after '-'
                rt = to.root           # this is a list!
                lk = -1                # start at last char in token
                while rt[lk] != cs: lk -= 1
                sn = len(rt) + lk      # where to divide suffix from root
#               print 'sn=' , sn , rt
                to.root = rt[:sn]      # root without suffix
                self.sbu.prepend(suf)  # restore suffix to input for processing
            else:                      # no suffix
                chx = self.sbu.peek()  # look at next char after match
                if chx == '-':         # if hyphen, need to separate it
                    self.sbu.skip()
                    if ellyChar.isLetter(self.sbu.peek()):
                        self.sbu.prepend(' ')
                    self.sbu.prepend('-')
#           print 'add' , unicode(to)
            self.ctx.addTokenToListing(to)  # add token to listing for sentence
            return True

#       print '[' + rws + ']' , 'still unrecognized'

        chx = rws[0]                   # special hyphen check
        if chx == '-' and k > 1:
#           print 'look in  internal dictionary'
            if self.ptr.createPhrasesFromDictionary(chx,False,False):
#               print 'found!'
                to = ellyToken.EllyToken(chx)  # treat hyphen as token
                self.ctx.addTokenToListing(to) # add it to token list
                self.sbu.skip()                # remove from input
                return True

        to = self._extractToken(mx)    # single-word matching with analysis with lookup

#       print 'to=' , unicode(to)
        if to == None:                 # if no match, we are done and will return
            return False if mx == 0 else True  # still success if _scanText() found something
        self.ptr.lastph.lens = to.getLength()

#       print 'to=' , unicode(to) , 'len(s)=' , len(s) , s
#       posn = self.ctx.countTokensInListing()
#       print 'at', posn , 'in token list'
        self.ctx.addTokenToListing(to) # add token to listing for sentence
#       tol = self.ctx.getNthTokenInListing(-1)
#       print 'last token root=' , tol.root
        return True                    # successful lookup

    def _scanText ( self , k ):

        """
        try to match in buffer regardless of word boundaries
        using Elly vocabulary, pattern, amd template tables an
        also running Elly entity extractors

        arguments:
            self  -
            k     - length of first component in buffer

        returns:
            match parameters [ text span of match , vocabulary match , suffix removed ]

        exceptions:
            ParseOverflow
        """

#       print '_scanText k=' , k
        sb = self.sbu.buffer           # input buffer
        tr = self.ptr                  # parse tree for results

#       print '_scanText sb=' , sb
                                       # initialize match status
        nspan = 0                      #   total span of match
        vmchs = [ ]                    #   chars of vocabulary entry matched
        suffx = ''                     #   any suffix removed in match

        d = self.rul                   # grammar rule definitions

        m = d.ptb.match(sb,tr)         # try token by pattern match next
#       print 'pattern m=' , m
        if  nspan < m:
            nspan = m                  # on longer match, update maximum

        m = d.ctb.match(sb,tr)         # try multi-word template  match next
#       print 'template m=' , m
        if  nspan < m:
            nspan = m                  # on longer match, update maximum

        m = self.iex.run(sb)           # try entity extractors next
#       print 'extractor m=' , m
        if  nspan < m:
            nspan = m                  # on longer match, update maximum

#       lm = len(sb)                   # scan limit
#       print 'lm=' , lm , 'm=' , m
        capd = ellyChar.isUpperCaseLetter(sb[0])
#       print 'next component=' , sb[:k] , ', context=' , sb[k:lm]

        if self.vtb != None:           # look in external dictionary, if it exists
            ls = list(sb[:k])
#           print 'ls 0=' , ls
            ellyChar.toLowerCaseASCII(ls)
            ss = u''.join(ls)                   # where to start for vocabulary indexing
#           print 'ls 1=' , ls
            n = vocabularyTable.delimitKey(ss)  # get actual indexing
#           print 'delimiting n=' , n , '=' , '<' + ss[:n] + '>'
#           print vocabularyTable.listDBKeys(self.vtb.cdb)

            rl = self.vtb.lookUp(sb,n) # get list of the maximum text matches
#           print len(rl) , 'matches'
            if len(rl) > 0:            #
                r0 = rl[0]             # look at first record
#               print 'r0=' , r0
                vmln = r0.nspan        # should be same for all matches
                vchs = r0.vem.chs      #
                vsfx = r0.suffx        #
#               print 'nspan=' , vmln , vsfx

                if ( vmln > nspan or
                     vmln == nspan and vsfx == '' ):

                    nspan = vmln       # keep vocabulary matches
                    vmchs = vchs       #
                    suffx = vsfx       #

                    for r in rl:
                        ve = r.vem     # get vocabulary entry
#                       print 've=' , ve
#                       if ve.gen != None: print 've.gen=' , ve.gen
                        if tr.addLiteralPhraseWithSemantics(
                                ve.cat,ve.syf,ve.smf,ve.bia,ve.gen,len(suffx) > 0):
                            tr.lastph.lens = nspan  # char length of leaf phrase node
                                                    # needed for later selection
                            tr.lastph.krnl.cncp = ve.con
                            if capd:
                                tr.lastph.krnl.semf.set(0)
#                           print 'vocab phr=' , tr.lastph , 'len=' , tr.lastph.lens
                            if suffx != '':
                                if ellyChar.isApostrophe(suffx[1]):
                                    tr.lastph.krnl.usen = 0

#               print 'vocabulary m=' , vmln
#               print 'queue after table lookup:' , len(self.ptr.queue)

#           print 'sb=' , sb

#       print 'maximum match=' , nspan
#       print 'input=' , self.sbu.buffer[:nspan]

        if nspan > 0:                  # any matches at all?
            tr.requeue()               # if so, keep only longest of them
#       print 'queue after scan:' , len(self.ptr.queue)

#       print 'returns [' , nspan , ',' , vmchs , ',' , suffx , ']'
        return [ nspan , vmchs , suffx ]

    def _simpleTableLookUp ( self , ws , tree , spl=False , cap=False ):

        """
        simple external dictionary lookup

        arguments:
            self  -
            ws    - single-word string
            tree  - parse tree for putting matches
            spl   - splitting of token flag
            cap   - capitalization of token flag

        returns:
            count of matches found

        exceptions:
            ParseOverflow
        """

#       print 'look up [' + ws + '] externally'

        count = 0

        vs = self.vtb.lookUpSingleWord(ws)  # look up token as word externally
        lws = len(ws)
#       print len(vs) , 'candidates'
        for v in vs:                        # try to make phrases from vocabulary elements
#           print 'v=' , v
            if tree.addLiteralPhraseWithSemantics(
                v.cat,v.syf,v.smf,v.bia,v.gen,spl
            ):
                if cap:
                    tree.lastph.krnl.semf.set(0)
                tree.lastph.lens = lws
#               print 'vtb sbuf=' , self.sbu.buffer
                count += 1

        return count

    def _extractToken ( self , mnl ):

        """
        extract next token from input buffer and look up in grammar table

        arguments:
            self  -
            mnl   - minimum length for any previous match

        returns:
            ellyToken on success, otherwise None

        exceptions:
            ParseOverflow
        """

        d = self.rul                        # grammar rule definitions

        tree = self.ptr                     # parse tree
        buff = self.sbu                     # input source

#       print 'start extraction'
        try:
            w = buff.getNext()              # extract next token
#           print 'got token=' , w
            ws = u''.join(w.root)
        except ellyException.StemmingError as e:
            print >> sys.stderr , 'FATAL error' , e
            sys.exit(1)
#       print 'extracted' , '['+ ws + ']'
        wcapzn = w.isCapitalized()
        wsplit = w.isSplit()

        wl = len(ws)
        if wl > mnl:
            found = self._simpleTableLookUp(ws,tree,wsplit,wcapzn) > 0
#           print 'found in external table=' , found

        if wl >= mnl:
            if ws in self.rul.gtb.dctn:     # look up internally
#               print '"' + ws + '" in dictionary'
                if tree.createPhrasesFromDictionary(ws,wsplit,wcapzn):
                    found = True

#       print 'found in internal dictionary=' , found
        if found:                           # if any success, we are done
            return w
        if mnl > 0:
            return None                     # defer to previous lookup

#       print 'logic: ' , d.man.pref , d.man.suff
        dvdd = False
        if d.man.analyze(w):                # any analysis possible?
            root = u''.join(w.root)         # if so, get parts of analysis
            tan = w.pres + [ root ] + w.sufs
            if len(w.sufs) > 0:
                sx = w.sufs[-1]
                dvdd = not ellyChar.isApostrophe(sx[1])
#           print 'token analysis=' , tan
            while len(tan) > 0:             # and put back into input
                x = tan.pop()
                buff.prepend(x)
                buff.prepend(' ')
            w = buff.getNext()              # get token again with stemming and macros

            ws = u''.join(w.root)
            if len(ws) < mnl: return None   # external lookup?
            if self._simpleTableLookUp(ws,tree,False,wcapzn):  # external lookup
                found = True

            if ws in self.rul.gtb.dctn:     # internal lookup?
                if tree.createPhrasesFromDictionary(ws,wsplit,wcapzn):
                    found = True

        if found:                           # if any success, we are done
#           print 'token recognized'
            w.dvdd = dvdd
            return w

#       print 'still unrecognized token w=' , unicode(w)
        if self.pnc.match(w.root):          # check if next token is punctuation
#           print 'catg=' , self.pnc.catg , self.pnc.synf.hexadecimal()
            if tree.addLiteralPhrase(self.pnc.catg,self.pnc.synf):
                tree.lastph.lens = w.getLength()
                tree.lastph.krnl.semf.combine(self.pnc.semf)
#               print 'semf=' , self.pnc.semf
#               print 'lastph=' , tree.lastph
#           print 'punc w=' , unicode(w)
            return w

#       print 'must create UNKN leaf node'
        tree.createUnknownPhrase(w)     # unknown type as last resort
        tree.lastph.lens = len(ws)

        return w

    def symbolCheck ( self ):

        """
        show language definition symbols unused in grammar

        arguments:
            self
        """

        print ''
        print 'Unused Symbols'
        print '--------------'
        _show("grammar extras"              ,self.gundef)
        _show("external vocabulary"         ,self.vundef)
        _show("punctuation"                 ,self.pundef)
        _show("information extraction types",self.eundef)

def _show ( typm , syms ):

    """
    show unused symbols of particular type

    arguments:
        typm  - source of symbols
        syms  - list of symbols
    """

    if len(syms) == 0: return
    print >> sys.stderr , '  in' , typm + ':'
    m = 8
    n = 0
    for s in syms:
        print >> sys.stderr , '  {0:7s}'.format(s) ,
        n += 1
        if n%m == 0: print >> sys.stderr , ''
    print >> sys.stderr , ''

#
# unit and integration test
#

if __name__ == '__main__':

    import dumpEllyGrammar

    so = sys.stdout
    si = sys.stdin

#   print 'stdin=' , si.encoding , 'stdout=' , so.encoding

    try:
        syst = sys.argv[1] if len(sys.argv) > 1 else 'test'  # which rule definitions to run
        dpth = int(sys.argv[2]) if len(sys.argv) > 2 else -1 # depth of parse tree reporting
    except ValueError , e:
        print >> sys.stderr , e
        sys.exit(1)

    print 'release=' , 'PyElly' , release
    print 'system =' , syst
    try:
        eb = EllyBase(syst)
#       print 'eb=' , eb
    except ellyException.TableFailure:
        print >> sys.stderr , 'cannot initialize rules and vocabulary'
        sys.exit(1)

    if dpth >= 0: eb.ptr.setDepth(dpth)  # for parse trees

    print ""
    dumpEllyGrammar.dumpCategories(eb.rul.stb)
    eb.symbolCheck()
    dumpEllyGrammar.dumpExtensions(eb.rul.stb,eb.rul.gtb.extens,False)
    dumpEllyGrammar.dumpSplits(eb.rul.stb,eb.rul.gtb.splits,False)
    dumpEllyGrammar.dumpDictionary(eb.rul.stb,eb.rul.gtb.dctn,False)

    so.write('\n')

    print 'Extractors'
    print '----------'
    eb.iex.dump()

    so.write('\n')
    so.flush()
    sys.stderr.flush()

    while True:  # translate successive lines of text as sentences for testing

        so.write('> ')
        line = si.readline()
        l = line.decode('utf8')
        if len(l) == 0 or l[0] == '\n': break
#       print 'input:' , type(line) , '->' , type(l) , l
        txt = list(l.strip())
#       print 'txt=' , txt
        so.write('\n')
        lo = eb.translate(txt,True)
        eb.ptr.dumpAll()
        if lo == None:
            print >> sys.stderr , '????'
        else:
            so.write('=[' + u''.join(lo) + ']\n')

    so.write('\n')
