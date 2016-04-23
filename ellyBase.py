#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBase.py : 20apr2016 CPM
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
integrating PyElly components into a language processing tool
to handle a single sentence at a time
"""

import sys
import codecs
import ellySession
import ellyConfiguration
import ellyDefinition
import ellyPickle
import ellyToken
import ellyChar
import ellyException
import substitutionBuffer
import parseTree
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

sys.stdout = codecs.getwriter('utf8')(sys.stdout) # redefine standard output and error
sys.stderr = codecs.getwriter('utf8')(sys.stderr) # streams for UTF-8 encoding

# binary files

rules = ellyDefinition.grammar          # for saving grammar rules
vocabulary = vocabularyTable.vocabulary # for saving compiled vocabulary

_session = '.session.elly.bin'          # for saving session information

# source text files

_rules      = [ '.g.elly' , '.m.elly' , '.p.elly' , '.n.elly' , '.h.elly' ,
                '.stl.elly' , '.ptl.elly' ]
_vocabulary = [ vocabularyTable.source ]

# version ID

release = 'v1.3.12'                     # current version of PyElly software

def _timeModified ( basn , filn ):

    """
    get file modification time

    arguments:
        file  - pathname

    returns:
        integer number of seconds since base time

    exceptions:
        OSError
    """

    return int(os.path.getmtime(basn + filn))

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
        return False

    basn = ellyConfiguration.baseSource + '/'

    for f in srcs:
        try:
            d = _timeModified(basn,systm + f)
        except OSError:
            d = 0
        if d > date:
            return False
    return True

def _notToDate ( system ):

    """
    check vocabulary versus grammar time stamps

    arguments:
        system - application ID

    returns:
        True if vocabulary older, False otherwise
    """

    aid = './' + system
    return (_timeModified(aid,rules) >
            _timeModified(aid,vocabulary))

#
# main class for processing single sentences
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

        nultok - null token

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

        self.nultok = ellyToken.EllyToken()

        self.gundef = [ ]  # initialize
        self.vundef = [ ]  #
        self.pundef = [ ]  #
        self.eundef = [ ]  #

#       print 'EllyBase.__init__()'
        sysf = system + rules
        redefine = not _isSaved(system,rules,_rules)
        try:
            self.rul = ellyDefinition.Grammar(system,redefine,release)
        except ellyException.TableFailure:
            nfail += 1
        if nfail == 0:
            self.gundef = self.rul.stb.findUnknown()
            ellyPickle.save(self.rul,sysf)

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

        if not redefine:
            if not _isSaved(system,vocabulary,_vocabulary) or _notToDate(system):
                redefine = True

        stb = d.stb if d != None else symbolTable.SymbolTable()

        if redefine: print 'recompiling vocabulary'
        try:
            voc = ellyDefinition.Vocabulary(system,redefine,stb,inflx)
        except ellyException.TableFailure:
            nfail += 1

#       print self.rul.stb
#       print stb

        if nfail > 0:
            print >> sys.stderr , 'exiting: table generation FAILures'
            sys.exit(1)

#       print 'vundef=' , self.vundef
        self.vtb = voc.vtb
        self.vundef = stb.findUnknown()
#       print 'vundef=' , self.vundef

#       print '1:' , len(stb.ntname) , 'syntactic categories'

        self.ctx = interpretiveContext.InterpretiveContext(stb,d.gtb.pndx,s.globals,d.hry)

        for z in d.gtb.initzn:        # initialize global symbols for parsing
            self.ctx.glbls[z[0]] = z[1]

#       print '2:' , len(stb.ntname) , 'syntactic categories'

        self.pnc = punctuationRecognizer.PunctuationRecognizer(stb)
        self.pundef = stb.findUnknown()

#       print '3:' , len(stb.ntname) , 'syntactic categories'

        nto = len(stb.ntname)         # for consistency check

        if ellyConfiguration.treeDisplay:
            print "tree display ON"
            self.ptr = parseTreeWithDisplay.ParseTreeWithDisplay(stb,d.gtb,d.ptb,self.ctx)
        else:
            print "tree display OFF"
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

        ntn = len(stb.ntname)         # do consistency check on syntactic category count
        if nto != ntn:
            print >> sys.stderr , 'WARNING: grammar rules should predefine all syntactic categories'
            print >> sys.stderr , '         and features identified in other language definitions'

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
        Elly processing of text input

        arguments:
            self  -
            text  - list of Unicode chars to translate
            plsb  - flag to show plausibility score in output

        returns:
            rewritten input on success, None otherwise
        """

#       print 'EllyBase.translate()'
        self.ptr.reset()                # empty out any previous parse tree
        self.ctx.tokns = [ ]            #       and its token list
        self.ctx.clearBuffers()         # clear output buffer
        self.ctx.clearLocalStack()      # clear local variables

        if len(text) == 0:              # if no text, done
            return ''
#       print 'list' , list(text)
        self.sbu.refill(text)           # put text to translate into input buffer

        try:
            while True:
#               print 'current text chars=' , self.sbu.buffer
                if len(self.sbu.buffer) == 0:
                    break               # stop when sentence buffer is empty
                self.ptr.startUpX()     # for any initial ... grammar rule
                tokn = self._lookUpNext()
                if tokn == None:
#                   print 'lookup FAIL'
                    return None         # if next token cannot be handled, quit
                if len(self.ptr.queue) == 0:
                    break
                self.ptr.digest()       # process queue to get all ramifications
                self.ptr.restartQueue() # for any leading zero production
#               print len(self.ctx.tokns) , 'tokens after digestion'

            self.ptr.finishUpX()        # for any trailing ... grammar rule
        except ellyException.ParseOverflow:
            print >> sys.stderr , 'parse FAILed! overflow'
            return None

        if not self.ptr.evaluate(self.ctx):
            return None                 # translation fails

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
        look up next segment in input buffer by various means

        arguments:
            self

        returns:
            ellyToken on successful lookup, None otherwise

        exceptions:
            ParseOverflow
        """

        self.sbu.skipSpaces()          # skip leading spaces
        s = self.sbu.buffer

        if len(s) == 0:                # check for end of input
            return self.nultok         # if so, done

        if self.trs != None:           # preanalysis of number expressions
            self.trs.rewriteNumber(s)

        self.sbu.expand()              # apply macro substitutions

        s = self.sbu.buffer

#       print 'expanded len=' , len(s)

        if len(s) == 0: return True    # macros can empty out buffer

#       print unicode(self.sbu)
        k = self.sbu.findBreak()       # try to find first component for lookup
        if k == 0:
            k = 1                      # must have at least one char in token

#       print 'break at k=' , k
        kl = len(s)
        if  k + 1 < kl and s[k] == '+' and s[k+1] == ' ':
            k += 1                     # recognize possible prefix

#       print 'len(s)=' , kl , 'k=' , k , 's=', s

        mr = self._scanText(k)         # text matching in various ways
        mx  = mr[0]                    # overall maximum match length
        chs = mr[1]                    # any vocabulary element matched
        suf = mr[2]                    # any suffix removed in matching
        s = self.sbu.buffer
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
            to = ellyToken.EllyToken(chs)
#           print 'long token=' , unicode(to)
            self.ctx.tokns.append(to)
            if suf != '':
                if not ellyChar.isApostrophe(suf[1]):
                    to.dvdd = True     # must note suffix removal for token!
#           print 'queue:' , len(self.ptr.queue)
            return to

        wsk = self.sbu.buffer[:k]
        cap = ellyChar.isUpperCaseLetter(wsk[0])
#       print 'wsk=' , wsk
#       print 'queue before=' , len(self.ptr.queue)
        rws = u''.join(wsk)
        found = self.ptr.createPhrasesFromDictionary(rws.lower(),False,cap)
        if found or mx > 0:
#           print 'found internally'
            self.sbu.skip(k)
#           print 'next=' , self.sbu.buffer[self.sbu.index:]
#           print 'queue after =' , len(self.ptr.queue)
            to = ellyToken.EllyToken(rws)
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
            self.ctx.tokns.append(to)  # add token to parse tree
            return to

#       print '[' + rws + ']' , 'not found in dictionary'

        to = self._extractToken(mx)    # single-word matching with analysis

#       print 'to=' , unicode(to)
        if to == None: return False if mx == 0 else True

#       print 'to=' , unicode(to) , 'len(s)=' , len(s) , s
#       print 'at', len(self.ctx.tokns) , 'in token list'
        self.ctx.tokns.append(to)

#       posn = len(self.ctx.tokns) - 1 # put token into sentence sequence
#       print 'posn=' , posn
#       print 'token=' ,  self.ctx.tokns[posn].root
        return to

    def _scanText ( self , k ):

        """
        try to match in buffer regardless of word boundaries
        using Elly vocabulary and pattern tables and also
        running Elly entity extractors

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

                                       # initialize match status
        nspan = 0                      #   total span of match
        vmchs = [ ]                    #   chars of vocabulary entry matched
        suffx = ''                     #   any suffix removed in match

        lm = len(sb)                   # scan limit
        capd = ellyChar.isUpperCaseLetter(sb[0])
        vmx = 0                        # external vocabulary match maximum
#       print 'next component=' , sb[:k] , ', context=' , sb[k:lm]

        if self.vtb != None:           # look in external dictionary first, if it exists
            if  k > 1:                 # is first component a single char?
                ks = k                 # if not, use this for indexing
            else:
                ks = 1                 # otherwise, add on any following alphanumeric
                while ks < lm:         #
                    if not ellyChar.isLetterOrDigit(sb[ks]):
                        break
                    ks += 1
            ss = u''.join(sb[:ks])     # where to start for indexing
#           print 'ss=' , ss , sb[:ks]
            n = vocabularyTable.delimitKey(ss)  # get actual indexing
#           print 'n=' , n
            rl = self.vtb.lookUp(sb,n) # get list of the longest matches
#           print len(rl) , 'matches'
            if len(rl) > 0:            #
                r0 = rl[0]             # look at first record
#               print 'r0=' , r0
                nspan = r0.nspan       # should be same for all matches
                vmchs = r0.vem.chs     #
                suffx = r0.suffx       #

                vmx = nspan

                for r in rl:
                    ve = r.vem         # get vocabulary entry
#                   print 've=' , ve
#                   if ve.gen != None: print 've.gen=' , ve.gen
                    if tr.addLiteralPhraseWithSemantics(
                            ve.cat,ve.syf,ve.smf,ve.bia,ve.gen,len(suffx) > 0):
                        tr.lastph.lens = nspan  # set char length of leaf phrase node
                                                # just added for later selection
                        tr.lastph.krnl.cncp = ve.con
                        if capd:
                            tr.lastph.krnl.semf.set(0)
#                       print 'vocab phr=' , tr.lastph , 'len=' , tr.lastph.lens
                        if suffx != '':
                            if ellyChar.isApostrophe(suffx[1]):
                                tr.lastph.krnl.usen = 0

#       print 'vocabulary m=' , nspan

        d = self.rul                   # grammar rule definitions

        m = d.ptb.match(sb,tr)         # try entity by pattern match next
#       print 'pattern m=' , m
        if  nspan < m:
            nspan = m                  # on longer match, update maximum

        m = self.iex.run(sb)           # try entity extractors next
#       print 'extractor m=' , m
        if  nspan < m:
            nspan = m                  # on longer match, update maximum

#       print 'maximum match=' , nspan
#       print 'input=' , self.sbu.buffer[:nspan]

        if nspan > 0:                  # any matches at all?
            tr.requeue()               # if so, keep only longest of them

        if vmx > 0 and nspan > vmx:    # any longer match than vocabulary table?
            vmchs = ''                 # if so, remove vocabulary info in result
            suffx = ''
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
#       print len(vs) , 'candidates'
        for v in vs:                        # try to make phrases from vocabulary elements
#           print 'v=' , v
            if tree.addLiteralPhraseWithSemantics(
                v.cat,v.syf,v.smf,v.bia,v.gen,spl
            ):
                if cap:
                    tree.lastph.krnl.semf.set(0)
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
# unit test
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

    print 'version=' , release
    print 'system =' , syst
    try:
        eb = EllyBase(syst)
#       print 'eb=' , eb
    except ellyException.TableFailure:
        print >> sys.stderr , 'cannot initialize rules and vocabulary'
        sys.exit(1)

    if dpth >= 0: eb.ptr.setDepth(dpth)

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
        so.write('\n')
        lo = eb.translate(txt,True)
        if lo == None:
            print >> sys.stderr , '????'
        else:
            eb.ptr.dumpAll()
            so.write('=[' + u''.join(lo) + ']\n')

    so.write('\n')
