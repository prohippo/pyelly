#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# parseTreeWithDisplay.py : 01mar2016 CPM
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
parse tree with formatted tree dump for debugging
"""

import sys
import codecs
import ellyBits
import parseTree
import symbolTable
import conceptualHierarchy

mark = 256       # distinct flag for tree node already dumped

DPTH = 32        # maximum stack depth for tree traversal

BRN  = u'\u252C' # '+' branch  Unicode box-drawing characters for drawing tree
DWN  = u'\u2500' # '-' down
CNN  = u'\u2502' # '|' connect
ANG  = u'\u2514' # '\' ell angle
NBSP = u'\u00A0' # non-breaking space

SPCG = NBSP+NBSP+NBSP+NBSP+NBSP+NBSP+NBSP+NBSP+NBSP # for indentation

out  = codecs.getwriter('utf8')(sys.stderr) # must do this for any redirection to work

L =  4           # maximum syntax type name length for output
N = 24           # maximum number of phrase nodes to report for rule

def _idbias ( ph ):

    """
    format phrase sequence number and cognitive bias

    arguments:
        ph   - given phrase

    returns:
        string for sequence number and bias
    """

    if ph == None:
        return "         "
    else:
        return "{:4d}".format(ph.krnl.seqn) + " ={:3d}".format(ph.krnl.bias)

class ParseTreeWithDisplay(parseTree.ParseTree):

    """
    parse tree with methods for formatted dumping

    attributes:
        stb  - symbol table for syntactic types
        ctx  - context for parsing
        dlm  - depth limit for displaying parse tree
    """

    def __init__ ( self , stb , gtb , ptb , ctx , dpth=DPTH ):

        """
        initialization

        arguments:
            self -
            stb  - symbol table
            gtb  - grammar table
            ptb  - patterns for syntax categorization
            ctx  - interpretive context
            dpth - depth limit for tree display
        """

        super(ParseTreeWithDisplay,self).__init__(stb,gtb,ptb,ctx)
        self.ctx = ctx
        self.stb = stb
        self.dlm = dpth - 1

    def dumpAll ( self ):

        """
        dump all tree fragments (overrides superclass method)

        arguments:
            self  -
        """

#       print ' all depth=' , self.dlm + 1
        if self.dlm < 0:
            return
        tks = self.ctx.tokns       # token list for parse
        out.write('dump all\n\n')
        n = self.phlim - 1         # index of last node created
        while n >= 0:              # process until oldest node at n=0
            ph = self.phrases[n]   # get phrase
            if ph.dump:            # if not already dumped
                self.dumpTree(ph)  # dump subtree starting at current phrase
            n -= 1

        out.write('rules invoked and associated phrases\n')
        hr = { }                   # association of rules with phrase nodes
        lm = N                     # maximum number phrase nodes to report
        for k in range(self.phlim):
            ph = self.phrases[k]
            rs = ph.krnl.rule.seqn
            if not rs in hr: hr[rs] = [ ]
            hr[rs].append(ph)      # make association
        for rs in hr.keys():       # iterate on sequence numbers for rules found
            ls = hr[rs]
            if len(ls) > lm: ls = ls[:lm]
            rssn = 'rule {:4d}:'.format(rs)
            out.write(rssn)        # report up to lm phrase nodes for rule
                                   # with this sequence number
            for ph in ls:
                out.write(' ')
                out.write(str(ph.krnl.seqn))
            out.write('\n')
        out.write('\n')

        wn = len(self.ctx.tokns)   # set to last parse position in input
        while wn > 0 and len(self.goal[wn]) == 0:
            wn -= 1
        gs = self.goal[wn]         # goals at end of parsed input
        gl = len(gs)               # number of goals at last position

        out.write(str(gl) + ' final goals at position= ' + str(wn) + '\n')
        for g in gs:
            fs = '{:4.4s}'.format(self.stb.getSyntaxTypeName(g.cat))
            grs = str(g)
            kn = grs.find(':') + 1
            out.write(NBSP + grs[:kn] + ' ' + fs + grs[kn:] + '\n')
        out.write("\n")
        out.write(str(self.phlim) + ' phrases altogether\n')
        out.write('\nambiguities\n')

        nph = self.phlim                     # number of phrases allocated in parse
        phx = ellyBits.EllyBits(nph)         # to keep track of phrases listed as ambiguous
        nam = 0                              # ambiguity count

        for i in range(nph):                 # scan all phrases for ambiguities
            ph = self.phrases[i]
            if ph.alnk == None or phx.test(i): continue # is this a new ambiguity?
            s = self.stb.getSyntaxTypeName(ph.krnl.typx)     # if so, show phrase info
            f = ph.krnl.synf.hexadecimal(False)              # convert to packed hexadecimal
            out.write("{0:<5.5s} {1}: ".format(s,f))         # show syntax type of ambiguity
            nam += 1
            while ph != None:
                phx.set(ph.krnl.seqn)                        # mark phrase as scanned
                out.write("{:2d} ".format(ph.krnl.seqn))     # show its sequence number
                bx = '-' if ph.krnl.rule.bias < 0 else '0'   # show rule bias in effect
                out.write("({0:+2d}/{1}) ".format(ph.krnl.bias,bx))
                ph = ph.alnk                                 # next phrase in ambiguity list
            out.write('\n')
        if nam == 0: out.write('NONE\n')
        out.write('\n')
        out.write(str(len(tks)))
        out.write(' raw tokens=')
        for tk in tks:
            if tk == None:
                out.write(' [[NONE]]')
            else:
                if len(tk.root) < len(tk.orig):
                    tstr = ''.join(tk.root)
                else:
                    tstr = tk.orig
                out.write(' [[' + tstr + ']]')          # original tokens for parse tree

        out.write('\n')
        ng = self.glim
        out.write(str(nph) + ' phrases, ' + str(ng) + ' goals\n')
        out.flush()

    def dumpTree ( self , ph ):

        """
        dump subtree from given phrase node, overriding superclass method

        arguments:
            self  -
            ph    - given phrase
        """

        sys.stdout.flush()
        if ph == None:
            out.write('no phrase given' + '\n')
            return
#       print 'tree depth=' , self.dlm + 1
        if self.dlm < 0:
            return
        out.write('dumping from ' + str(ph) + '\n')
        tks = self.ctx.tokns

        trunc = False                                  # flag that display was truncated

        stk = [ ]                                      # stack for tree traversal

        out.write(NBSP)
        while True:                                    # traverse subtree from given phrase
            ph.dump = False                            # mark phrase node as being displayed

            sb = self.stb.getSyntaxTypeName(ph.krnl.typx)   # syntactic type name
            if len(sb) > L: sb = sb[:L]                # limit to L chars
            l = len(sb)
            while l < L:
                out.write(DWN)                         # pad out
                l += 1
            out.write(sb)                              # write out for subtree display
            out.write(':')
            out.write(ph.krnl.synf.hexadecimal(False)) # syntactic features as packed hexadecimal
            phl = ph.krnl.lftd                         # get left  descendant
            phr = ph.krnl.rhtd                         # get right descendant
            if len(stk) == self.dlm:                   # reached depth limit?
                if phl != None:
                    phl = None
                    if phr != None:
                        phr = None
                        out.write(BRN)                 # indicate truncated branching path
                    else:
                        out.write(DWN)                 # indicate truncated downward  path
                    out.write('   ')
                    trunc = True

            if phl != None:                            # at non-leaf node?
                cc = BRN if phr != None else DWN
                out.write(cc)                          # if so, add appropriate connector
                stk.append([ ph , phr ])               # save any right descendant for recursion
                ph = ph.krnl.lftd                      # do left descendant next
            else:
                out.write(' @' + str(ph.krnl.posn))    # at leaf of tree, show input position
                if ph.krnl.posn < 0 or ph.krnl.posn >= len(tks):
                    tok = '--'
                elif ph.krnl.rule != self.gtb.arbr:
                    if tks[ph.krnl.posn] == None:
                        tok = 'NONE'                   # anomalous situation
                    else:
                        tok = ''.join(tks[ph.krnl.posn].root)   # leaf token string
                else:
                    tok = ''                           # null string
                out.write(' [' + tok + ']')            # write it out
                if ph.krnl.cncp != conceptualHierarchy.NOname:
                    out.write(' ' + ph.krnl.cncp)
                out.write('\n')                        # end of output line
                out.write(NBSP)

                for sr in stk:                         # show phrase IDs and biases in next line
                    if sr == None:                     # already shown?
                        out.write(_idbias(None))       # if so, just add spaces for alignment
                    else:
                        out.write(_idbias(sr[0]))      # if no, show phrase info
                        sr[0] = None                   # and indicate they have been shown
                    cc = CNN if sr != None and sr[1] != None else u' '
                    out.write(cc)
                out.write(_idbias(ph))                 # add phrase info for current phrase
                out.write('\n')
                out.write(NBSP)

                while True:                            # have to back up in tree
                    if len(stk) == 0:                  # if stack empty, done
                        out.write('\n')
                        if trunc:
                            out.write('\nTree truncated at depth ' +
                                      str(self.dlm + 1) + '\n')
                        out.flush()
                        return
                    srn = stk.pop()                    # otherwise, get next phrase
                    if srn != None:
                        ph = srn[1]                    # get previously saved right descendant
                        if ph == None:                 # if none, continue backing up
                            continue
                        for sr in stk:                 # fill out connections before phrase
                            out.write(SPCG)
                            out.write(CNN if sr != None and sr[1] != None else ' ')
                        out.write(SPCG)                #
                        out.write(ANG)                 # connector to next phrase node
                        stk.append(None)               # for alignment
                        break

        sys.exit(1) # should never reach this statement!

    def setDepth ( self , dpth ):

        """
        change tree display depth limit

        arguments:
            self  -
            dpth  - new depth
        """

        self.dlm = dpth - 1

#
# unit test
#

if __name__ == '__main__':

    import ellyToken
    import ellyDefinitionReader
    import ellyConfiguration
    import grammarTable

    class Wtg(object):  # dummy conceptual weighting
        """ dummy weighting class
        """
        def __init__ ( self ):
            """ dummy method
            """
            self.cxc = None
        def relateConceptPair ( self , cna , cnb ):
            """ dummy method
            """
            self.cxc = cna + cnb
            return 0
        def interpretConcept ( self , cn ):
            """ dummy method
            """
            self.cxc = cn
            return 0
        def getIntersection ( self ):
            """ dummy method
            """
            self.cxc = None
            return '--'

    class Ctx(object):  # dummy interpretive context
        """ dummy interpretive context class
        """
        def __init__ ( self ):
            """ dummy method
            """
            self.tokns = [ ]
            self.wghtg = Wtg()

    name = sys.argv[1] if len(sys.argv) > 1 else 'test'
    deep = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    base = ellyConfiguration.baseSource + '/'
    rdr = ellyDefinitionReader.EllyDefinitionReader(base + name + '.g.elly')
    if rdr.error != None:
        print >> sys.stderr , rdr.error
        sys.exit(1)
    print 'loading' , '[' + base + name + '.g.elly]' , len(rdr.buffer) , 'lines'

    stbu = symbolTable.SymbolTable()
    gtbu = grammarTable.GrammarTable(stbu,rdr)
    ctxu = Ctx()
    tksu = ctxu.tokns

    tree = ParseTreeWithDisplay(stbu,gtbu,None,ctxu)
    print tree
    print dir(tree)

    cat = stbu.getSyntaxTypeIndexNumber('num')
    fbs = ellyBits.EllyBits(symbolTable.FMAX)
    tree.addLiteralPhrase(cat,fbs)
    tree.digest()
    tksu.append(ellyToken.EllyToken('66'))
    tree.restartQueue()

    ws = [ u'nn' , u'b' , u'aj' ]  # more input to test rules from test.g.elly

    for w in ws:

        tree.createPhrasesFromDictionary(w,False,False)
        print '****' , tree.phlim , tree.lastph
        tree.digest()
        print '****' , tree.phlim , tree.lastph
        tksu.append(ellyToken.EllyToken(w))
        tree.restartQueue()

    print tksu

    print 'limits=' , tree.phlim , tree.glim

    print "------"
    print "------ dump all"
    tree.dumpAll()
    print "------"
    print "------ dump tree (should repeat some of the above output)"
    tree.dumpTree(tree.lastph)
    print "------"
    sys.stdout.flush()
    sys.stderr.flush()
    print "------ disable parse tree"
    tree.setDepth(0)
    tree.dumpTree(tree.lastph)
    print "------"
