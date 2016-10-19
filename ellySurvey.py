#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellySurvey.py : 18oct2016 CPM
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
running PyElly tokenization to classify tokens in a text data file
"""

import sys
import codecs
import ellyConfiguration
import ellyDefinition
import ellyToken
import ellyChar
import ellyException
import substitutionBuffer
import entityExtractor
import simpleTransform
import nameRecognition
import punctuationRecognizer
import vocabularyTable
import symbolTable

sys.stdout = codecs.getwriter('utf8')(sys.stdout) # redefine standard output and error
sys.stderr = codecs.getwriter('utf8')(sys.stderr) # streams for UTF-8 encoding

interact = sys.stdin.isatty()           # to check for redirection of stdin (=0)

rules = ellyDefinition.grammar          # for saving grammar rules
vocabulary = vocabularyTable.vocabulary # for saving compiled vocabulary

# source text files

_rules      = [ '.g.elly' , '.m.elly' , '.p.elly' , '.n.elly' , '.h.elly' ,
                '.stl.elly' , '.ptl.elly' ]
_vocabulary = [ vocabularyTable.source ]

#
# dummy classes for parseTree required by entityExtractor,
# vocabularyTable, and patternTable
#

class Tree(object):
    """
    support ParseTree attribute and method for
    pattern match and entity extraction

    attributes:
        lastph
    """

    class Phrase(object):
        """
        emulate parseTreeBase.Phrase

        attributes:
            lens
        """

        def __init__ ( self ):
            """
            initialization

            arguments:
                self
            """
            self.lens = 0

    def __init__ ( self ):
        """
        initialization

        arguments:
            self
        """
        self.lastph = Tree.Phrase()

    def addLiteralPhrase ( self , cat , fet , dvd=False , cap=False ):
        """
        required dummy method

        arguments:
            self
            cat
            fet
            dvd
            cap
        """
#       print >> sys.stderr , 'addLiteralPhrase cat=' , cat , 'fet=' , fet.hexadecimal(False)
        return

    def addLiteralPhraseWithSemantics (self,typ,sxs,sms,bia,gen=None,dvd=False,cap=False):
        """ dummy method
        """
        ph = Tree.Phrase()
        self.lastph = ph
        return True

#
# main class for processing text file to get tokens
#

class EllySurvey(object):

    """
    base class for token analysis of input data

    attributes:
        sbu  - input buffer with macro substitutions
        gtb  - grammar    table
        vtb  - vocabulary table
        rul  - grammar definitions
        pat  - pattern definitions:$
        iex  - entity extractors

        trs  - simple transformation
        pnc  - punctuation recognizer

        ptr  - dummy parse tree

        tks  - token list for output
    """

    def __init__ ( self , system ):

        """
        initialization of processing rules

        arguments:
            system   - root name for PyElly tables to load
        """

        nfail = 0          # error count for reporting

        self.rul = None

        self.tks = None    # token list for output

        self.ptr = Tree()

        try:
            self.rul = ellyDefinition.Grammar(system,True,None)
        except ellyException.TableFailure:
            nfail += 1

        d = self.rul  # language rules

        self.gtb = d.gtb if d != None else None

        mtb = d.mtb if d != None else None
        self.sbu = substitutionBuffer.SubstitutionBuffer(mtb)

        try:
            inflx = self.sbu.stemmer
        except AttributeError:
            inflx = None

        if d != None:
            d.man.suff.infl = inflx   # define root restoration logic

        stb = d.stb if d != None else symbolTable.SymbolTable()

        try:
            voc = ellyDefinition.Vocabulary(system,True,stb,inflx)
        except ellyException.TableFailure:
            nfail += 1

        if nfail > 0:
            print >> sys.stderr , 'exiting: table generation FAILures'
            sys.exit(1)

        self.vtb = voc.vtb

        self.pnc = punctuationRecognizer.PunctuationRecognizer(stb)

        self.iex = entityExtractor.EntityExtractor(self.ptr,stb) # set up extractors

        self.trs = simpleTransform.SimpleTransform()

        ntabl = d.ntb

        if ntabl != None and ntabl.filled():
            nameRecognition.setUp(ntabl)
            ellyConfiguration.extractors.append( [ nameRecognition.scan , 'name' ] )

    def survey ( self , text ):

        """
        Elly processing of text input for tokens only

        arguments:
            self  -
            text  - list of Unicode chars to extract tokens from
        """

        self.tks = [ ]                  # initialize token list

        if len(text) == 0:              # if no text, done
            return
        self.sbu.refill(text)           # put text to translate into input buffer

#       print self.sbu

        while self._lookUpNext():
#           print 'current text chars=' , self.sbu.buffer
            pass

#
# reworked local methods from ellyBase
#

    def _lookUpNext ( self ):

        """
        look up next segment in input buffer by various means

        arguments:
            self

        returns:
            True on success, False otherwise
        """

        self.sbu.skipSpaces()          # skip leading spaces
        s = self.sbu.buffer

        if len(s) == 0:                # check for end of input
            return False               # if so, done

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

        mr  = self._scanText(k)        # text matching
        mx  = mr[0]
        mty = mr[1]
        chs = mr[2]                    # any vocabulary element matched
        suf = mr[3]                    # any suffix removed in matching
        s = self.sbu.buffer
#       print 'mx=' , mx , 'len(s)=' , len(s), 'k=' , k
#       print 's=' , s

        if ( k < mx or
             k == mx and suf != '' ):  # next token cannot be as long as already seen?
            if len(chs) > 0:
                self.sbu.skip(mx)
                if suf != '':
                    self.sbu.prepend(suf)
            else:
                chs = self.sbu.extract(mx)
            to = ellyToken.EllyToken(u''.join(chs))
            self.tks.append([ mty , to ])
            return True

        wsk = self.sbu.buffer[:k]
#       print 'wsk=' , wsk
        rws = u''.join(wsk).lower()
        found = rws in self.gtb.dctn

        if found:
    #       print 'found internally'
            mty += 'Id'

        if found or mx > 0:
            self.sbu.skip(k)
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
            self.tks.append([ mty , to ])
            return True

#       print 'extract token'
        self._extractToken(mx,mty)     # single-word matching with analysis
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
            match parameters [ text span of match , match types , vocabulary match chars , suffix removed ]
        """

#       print '_scanText k=' , k
        sb = self.sbu.buffer           # input buffer

                                       # match status
        nspan = 0                      #   total span of match
        mtype = ''                     #   no match type yet
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
            n = vocabularyTable.delimitKey(ss)  # get actual indexing
#           print 'n=' , n
            rl = self.vtb.lookUp(sb,n) # get list of the longest matches
            if len(rl) > 0:            #
#               print 'len(rl)=' , len(rl)
                r0 = rl[0]             # look at first record
                nspan = r0.nspan       # should be same for all matches
                mtype = 'Vt'
                vmchs = r0.vem.chs     #
                suffx = r0.suffx       #

#       print 'vocabulary m=' , nspan

        d = self.rul                   # grammar rule definitions

        m = d.ptb.match(sb,self.ptr)   # try entity by pattern match next
#       print 'pattern m=' , m
        if  nspan < m:
            nspan = m                  # on longer match, update maximum
            mtype = 'Fa'
        elif m > 0 and nspan == m:
            mtype = 'VtFa'

#       print 'mtype=' , mtype

        m = self.iex.run(sb)           # try entity extractors next
#       print 'extractor m=' , m
        if  nspan < m:
            nspan = m                  # on longer match, update maximum
            mtype = 'Ee'
        elif m > 0 and nspan == m:
            mtype += 'Ee'               # unchanged match length, add type

#       print 'maximum match=' , nspan
#       print 'mtype=' , mtype
#       print 'input=' , self.sbu.buffer[:nspan]

        return [ nspan , mtype , vmchs , suffx ]

    def _simpleTableLookUp ( self , ws ):

        """
        simple external dictionary lookup

        arguments:
            self  -
            ws    - single-word string

        returns:
            True if matches found, False otherwise
        """

#       print 'look up [' + ws + '] externally'
        vs = self.vtb.lookUpSingleWord(ws)  # look up token as word externally
#       print len(vs) , 'candidates'

        return len(vs) > 0

    def _extractToken ( self , mnl , mty ):

        """
        extract next token from input buffer and look up in grammar table

        arguments:
            self  -
            mnl   - minimum match
            mty   - matches already made
        """

        d = self.rul                        # grammar rule definitions

        buff = self.sbu                     # input source

        try:
            w = buff.getNext()              # extract next token
            ws = u''.join(w.root)
        except ellyException.StemmingError as e:
            print >> sys.stderr , 'FATAL error' , e
            sys.exit(1)

#       print 'token ws=' , ws
        if len(ws) >= mnl:
            if len(mty) == 0 or mty[0] != 'V':
                if self._simpleTableLookUp(ws) > 0:
                    mty += 'Vt'

            if ws in self.rul.gtb.dctn:     # look up internally regardless
                mty += 'Id'

        if len(mty) > 0:                    # if any success, we are done
            self.tks.append([ mty , w ])
            return
        if mnl > 0:                         # go no further if we had matches at start
            return

        dvdd = False
        if d.man.analyze(w):                # any analysis possible?
            root = u''.join(w.root)         # if so, get parts of analysis
            tan = w.pres + [ root ] + w.sufs
            dvdd = len(w.pres) > 0 or len(w.sufs) > 0
#           print 'token analysis=' , tan
            while len(tan) > 0:             # and put back into input
                xs = tan.pop()
                buff.prepend(xs)
                buff.prepend(' ')
            w = buff.getNext()              # get token again with stemming and macros

            ws = u''.join(w.root)
            if len(ws) < mnl: return
            if self._simpleTableLookUp(ws): # external lookup
                mty  = 'Vt'

            if ws in self.rul.gtb.dctn:     # internal lookup
                mty += 'Id'

        if len(mty) > 0:                    # if any success, we are done
            w.dvdd = dvdd
            self.tks.append([ mty , w ])
            return

        if self.pnc.match(w.root):          # check if next token is punctuation
            mty = 'Pu'
        else:
            mty = 'Un'

        self.tks.append([ mty , w ])

#
# unit test
#

if __name__ == '__main__':

    so = sys.stdout
    si = sys.stdin

    try:
        syst = sys.argv[1] if len(sys.argv) > 1 else 'test'  # which rule definitions to run
    except ValueError , e:
        print >> sys.stderr , e
        sys.exit(1)

    try:
        es = EllySurvey(syst)
    except ellyException.TableFailure:
        print >> sys.stderr , 'cannot initialize rules and vocabulary'
        sys.exit(1)
    so.write('\n')

    while True:  # translate successive lines of text as sentences for testing

        if interact: so.write('> ')
        line = si.readline()
        l = line.decode('utf8')
        if len(l) == 0: break
        if l[0] == '\n': continue
        es.survey(l)
        ltok = es.tks
        if ltok == None:
            print >> sys.stderr , '????'
        else:
            for x in ltok:
                so.write(x[0] + ' ')
                wx = x[1]
                wr = ''.join(wx.getRoot())
                wo = wx.getOrig()
                so.write(wr)
                if wr != wo:
                    so.write('/' + wx.getOrig())
                so.write('\n')
