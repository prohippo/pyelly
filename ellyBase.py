#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBase.py : 08apr2015 CPM
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

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

# binary files

rules      = '.rules.elly.bin'          # for saving compiled rules
vocabulary = vocabularyTable.vocabulary # for saving compiled vocabulary

_session = '.session.elly.bin'          # for saving session information

# source text files

_rules      = [ '.g.elly' , '.m.elly' , '.p.elly' , '.n.elly' , '.h.elly' ,
                '.stl.elly' , '.ptl.elly' ]
_vocabulary = [ vocabularyTable.source ]

# version ID

release = 'v1.2.1'                      # current version of PyElly software

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
# main class
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

        gundef - undefined symbols in *.p.elly
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

        self.gundef = [ ]  # initialize
        self.vundef = [ ]  #
        self.pundef = [ ]  #
        self.eundef = [ ]  #

#       print 'EllyBase.__init__()'
        sysf = system + rules
        redefine = not _isSaved(system,rules,_rules)
        if redefine:
            print "recompiling language rules"
            try:
                self.rul = ellyDefinition.Rules(system,release)
            except ellyException.TableFailure:
                nfail += 1
            if nfail == 0:
                self.gundef = self.rul.stb.findUnknown()
                save(self.rul,sysf)
        else:
            print "loading saved language rules from" , sysf
            self.rul = load(sysf)
            if self.rul.rls != release:
                print >> sys.stderr , 'inconsistent PyElly version for saved rules'
                sys.exit(1)

        if restore != None:
            self.ses = load(restore + '.' + system + _session)
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

        if nfail > 0:
            print >> sys.stderr , 'exiting: table generation FAILures'
            sys.exit(1)

        self.vtb = voc.vtb
        self.vundef = d.stb.findUnknown()

#       print '1:' , len(d.stb.ntname) , 'syntactic categories'

        self.ctx = interpretiveContext.InterpretiveContext(d.stb,d.gtb.pndx,s.globals,d.hry)

        for z in d.gtb.initzn:        # initialize global symbols for parsing
            self.ctx.glbls[z[0]] = z[1]

#       print '2:' , len(d.stb.ntname) , 'syntactic categories'

        self.pnc = punctuationRecognizer.PunctuationRecognizer(d.stb)
        self.pundef = d.stb.findUnknown()

#       print '3:' , len(d.stb.ntname) , 'syntactic categories'

        nto = len(d.stb.ntname)       # for consistency check

        if ellyConfiguration.treeDisplay:
            print "tree display on"
            self.ptr = parseTreeWithDisplay.ParseTreeWithDisplay(d.stb,d.gtb,d.ptb,self.ctx)
        else:
            print "tree display off"
            self.ptr = parseTree.ParseTree(d.stb,d.gtb,d.ptb,self.ctx)

        ntabl = d.ntb

        if ntabl != None and ntabl.filled():
            nameRecognition.setUp(ntabl)
            ellyConfiguration.extractors.append( [ nameRecognition.scan , 'name' ] )

        self.iex = entityExtractor.EntityExtractor(self.ptr,self.ctx) # set up extractors

        self.eundef = d.stb.findUnknown()

        if ellyConfiguration.rewriteNumbers:
            self.trs = simpleTransform.SimpleTransform()
        else:
            self.trs = None           # no automatic conversion of written out numbers

#       print '4:' , len(d.stb.ntname) , 'syntactic categories'

        ntn = len(d.stb.ntname)       # do consistency check on syntactic category count
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
        self.ptr.reset()            # empty out any previous parse tree
        self.ctx.tokns = [ ]        #       and its token list
        self.ctx.clearBuffers()     # clear out output buffer
        self.ctx.clearLocalStack()  # clear out local variables

        if len(text) == 0:          # if no text, done
            return ''
#       print 'list' , list(text)
        self.sbu.refill(text)       # put text to translate into input buffer

        while True:
#           print 'current text chars=' , self.sbu.buffer
            if len(self.sbu.buffer) == 0:
                break               # stop when sentence buffer is empty
            self.ptr.startUpX()     # for any initial ... grammar rule
            stat = self._lookUpNext()
            if not stat:
#               print 'lookup FAIL'
                return None         # if next token cannot be handled, quit
            if len(self.ptr.queue) == 0:
                break
            self.ptr.digest()       # process tokens to get all resulting phrases
            self.ptr.restartQueue() # for any leading zero production
#           print len(self.ctx.tokns) , 'tokens after digestion'

        self.ptr.finishUpX()        # for any trailing ... grammar rule

        if not self.ptr.evaluate(self.ctx):
            return None             # translation fails

        if plsb:                    # show plausibility in output if requested
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
            True on successful lookup, False otherwise
        """

        self.sbu.skipSpaces()          # skip leading spaces
        s = self.sbu.buffer

        if len(s) == 0: return True    # check for end of input

        if self.trs != None:           # preanalysis of number expressions
            self.trs.rewriteNumber(s)

        self.sbu.expand()              # apply macro substitutions

        s = self.sbu.buffer

#       print 'expanded len=' , len(s)

        if len(s) == 0: return True    # macros can empty out buffer

        k = self.sbu.findBreak()       # try to find first component for lookup
        if k == 0:
            k = 1                      # must have at least one char in token

        kl = len(s)
        if  k + 1 < kl and s[k] == '+' and s[k+1] == ' ':
            k += 1                     # recognize possible prefix

#       print 'len(s)=' , kl , 'k=' , k , 's=', s

        mr = self._scanText(k)         # text matching
        mx = mr[0]
        s = self.sbu.buffer
#       print 'mx=' , mx , 'len(s)=' , len(s) , 's=' , s

        if k < mx:                    # next word cannot produce token as long as already seen?
            chs = mr[1]               # any vocabulary element matched
            suf = mr[2]               # any suffix removed in matching
            if len(chs) > 0:
                self.sbu.skip(mx)
                if suf != '':
                    self.sbu.prepend(suf)
            else:
                chs = self.sbu.extract(mx)
            to = ellyToken.EllyToken(u''.join(chs))
#           print 'long token=' , to
            self.ctx.tokns.append(to)
            return True

        wsk = self.sbu.buffer[:k]

        to = self._extractToken((mx > 0),wsk) # single-word matching with analysis

        if to == None: return False if mx == 0 else True

#       print 'to=' , to , 'len(s)=' , len(s) , s
#       print 'at', len(self.ctx.tokns) , 'in token list'
        self.ctx.tokns.append(to)

#       posn = len(self.ctx.tokns) - 1 # put token into sentence sequence
#       print 'posn=' , posn
#       print 'token=' ,  self.ctx.tokns[posn].root
        return True

    def _scanText ( self , k ):

        """
        try to match in buffer regardless of word boundaries
        using Elly vocabulary and pattern tables and also
        running Elly entity extractors

        arguments:
            self  -
            k     - length of first component in buffer

        returns:
            match parameters [ text span of match , suffix removed ]
        """

#       print '_scanText k=' , k
        sb = self.sbu.buffer           # input buffer
        tr = self.ptr                  # parse tree for results

                                       # match status
        nspan = 0                      #   total span of match
        vmchs = [ ]                    #   chars of vocabulary entry matched
        suffx = ''                     #   any suffix removed in match

        lm = len(sb)                   # scan limit
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
#           print 'ss=' , ss
            n = vocabularyTable.toIndex(ss)  # get actual indexing
#           print 'n=' , n
            rl = self.vtb.lookUp(sb,n) # get list of the longest matches
            if len(rl) > 0:            #
                r0 = rl[0]             # look at first record
                nspan = r0.nspan       # should be same for all matches
                vmchs = r0.vem.chs     #
                suffx = r0.suffx       #

#               print len(rl) , 'matching vocabulary entries'
                for r in rl:
                    ve = r.vem         # get vocabulary entry
#                   print 've=' , ve
#                   if ve.gen != None: print 've.gen=' , ve.gen
                    if tr.addLiteralPhraseWithSemantics(
                            ve.cat,ve.syf,ve.smf,ve.bia,ve.gen):
                        tr.lastph.lens = nspan  # set char length of leaf phrase node
                                                # just added for later selection
                        tr.lastph.cncp = ve.con

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

        return [ nspan , vmchs , suffx ]

    def _tableLookUp ( self , ws , tree ):

        """
        simple external dictionary lookup

        arguments:
            self  -
            ws    - single-word string
            tree  - parse tree for putting matches

        returns:
            count of matches found
        """

#       print 'look up [' + ws + '] externally'

        count = 0

        vs = self.vtb.lookUpSingleWord(ws)  # look up token as word externally
#       print len(vs) , 'candidates'
        for v in vs:                        # try to make phrases from vocabulary elements
            if tree.addLiteralPhraseWithSemantics(
                v.cat,v.syf,v.smf,v.bia,v.gen
            ):
#               print 'vtb sbuf=' , self.sbu.buffer
                count += 1

        return count

    def _extractToken ( self , found , wso ):

        """
        extract next token from input buffer and look up in grammar table

        arguments:
            self  -
            found - true if token not yet identified by scanning
            wso   - what was looked up already

        returns:
            token on success, otherwise None
        """

#       print 'extract: found=' , found , 'wso=' , wso

        d = self.rul                        # grammar rule definitions

        tree = self.ptr                     # parse tree
        buff = self.sbu                     # input source

        try:
            if found:
                w = buff.getNextSimple()    # next token must be taken without changes
            else:
                w = buff.getNext()          # extract next token
            ws = u''.join(w.root)
#           print 'extract' , ws
        except ellyException.StemmingError as e:
            print >> sys.stderr , 'FATAL error' , e
            sys.exit(1)

        if not found:                       # look up externally if no success yet
            if ws != wso:
                if self._tableLookUp(ws,tree) > 0:
                    found = True

        if ws in self.rul.gtb.dctn:         # look up internally regardless
#           print '"' + ws + '" in dictionary'
            if tree.createPhrasesFromDictionary(ws,w.isSplit()):
                found = True

        if found:                           # if any success, we are done
            return w

#       print 'logic: ' , d.man.pref , d.man.suff
        if d.man.analyze(w):                # any analysis possible?
            root = u''.join(w.root)         # if so, get parts of analysis
            tan = w.pres + [ root ] + w.sufs
#           print 'token analysis=' , tan
            while len(tan) > 0:             # and put back into input
                x = tan.pop()
                buff.prepend(x)
                buff.prepend(' ')
            w = buff.getNext()              # get token again with stemming and macros

            ws = u''.join(w.root)
            if self._tableLookUp(ws,tree):  # external lookup
                found = True

            if ws in self.rul.gtb.dctn:     # internal lookup
                if tree.createPhrasesFromDictionary(ws,w.isSplit()):
                    found = True

        if found:                           # if any success, we are done
            return w

        if self.pnc.match(w.root):          # check if next token is punctuation
            if tree.addLiteralPhrase(self.pnc.catg,self.pnc.synf):
                tree.lastph.lens = w.getLength()
            found = True

        if not found:
#           print 'must create UNKN leaf node'
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

################################
# serialization of definitions #
################################

import pickle

def save ( ob , nm ):

    """
    save an Elly object

    arguments:
        ob  - the object
        nm  - destination file name

    returns:
        True on success, False otherwise
    """

    try:
        outs = open(nm,'wb')
        pickle.dump(ob,outs)
        outs.close()
        return True
    except IOError:
        return False

def load ( nm ):

    """
    load an Elly object

    arguments:
        nm  - source file name

    returns:
        symbol table on success, None on failure
    """

    try:
        ins = open(nm,'rb')
        ob = pickle.load(ins)
        ins.close()
        return ob
    except IOError:
        return None

#
# unit test
#

if __name__ == '__main__':

    import dumpEllyGrammar

    so = sys.stdout
    si = sys.stdin

#   print 'stdin=' , si.encoding , 'stdout=' , so.encoding

    syst = sys.argv[1] if len(sys.argv) > 1 else 'test'  # which rule definitions to run
    dpth = sys.argv[2] if len(sys.argv) > 2 else -1      # depth of parse tree reporting

    print 'system=' , syst
    try:
        eb = EllyBase(syst)
#       print 'eb=' , eb
    except ellyException.TableFailure:
        print >> sys.stderr , 'cannot initialize rules and vocabulary'
        sys.exit(1)

    if dpth >= 0: eb.ptr.setDepth(dpth)

    print ""
    dumpEllyGrammar.dumpCategories(eb.rul.stb)
    dumpEllyGrammar.dumpExtensions(eb.rul.stb,eb.rul.gtb.extens,False)
    dumpEllyGrammar.dumpSplits(eb.rul.stb,eb.rul.gtb.splits,False)
    dumpEllyGrammar.dumpDictionary(eb.rul.stb,eb.rul.gtb.dctn,False)

    eb.symbolCheck()

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
        lo = eb.translate(txt,True)
        if lo == None:
            print >> sys.stderr , '????'
        else:
            so.write('=[' + u''.join(lo) + ']\n')
        eb.ptr.dumpAll()

    so.write('\n')
