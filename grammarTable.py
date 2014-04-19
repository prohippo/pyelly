#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# grammarTable.py : 05apr2014 CPM
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
define syntax and semantics of language to read and process
"""

import syntaxSpecification
import cognitiveProcedure
import generativeProcedure
import derivabilityMatrix
import grammarRule
import ellyChar
import ellyBits
import ellyDefinitionReader
import definitionLine
import sys

def compile ( syms, clss , code ):

    """
    create cognitive or generative semantic procedure from code

    arguments:
        syms  - symbol table
        clss  - type of procedure: 'c'=cognitive, 'g'=generative
        code  - list of semantic commands

    returns:
        cognitive or generative procedure on success, None otherwise
    """

    inps = ellyDefinitionReader.EllyDefinitionReader(code)
    if   clss == 'c':
        return cognitiveProcedure.CognitiveProcedure(syms,inps)
    elif clss == 'g':
        return generativeProcedure.GenerativeProcedure(syms,inps)
    else:
        print >> sys.stderr , 'bad semantic procedure class'
        return None

NMAX = 64  # maximum number of syntactic types
FMAX = 16  # maximum number of feature names per set

def isNewRule ( s ):

    """
    check for start of new rule or procedure in processing input lines

    arguments:
        s   - input line as string

    returns:
        True if new rule or procedure, False otherwise
    """

    return (len(s) > 2 and ellyChar.isLetter(s[0]) and s[1] == ':')

class GrammarTable(object):

    """
    data structures for an Eliza grammar

    attributes:
        initzn - initialized globals
        dctn   - builtin dictionary
        pndx   - standalone named procedures
        extens - 1-branch rules
        splits - 2-branch rules 
        mat    - derivability matrix

        START  - start symbol for grammar (reserved)
        END    - end type - never used in any actual rule
        UNKN   - unknown category
        XXX    - for ... special category

        arbr   - ...->nil rule

        d1bp   - default semantics for 1-branch rule
        d2bp   -                       2-branch
    """

    def __init__ ( self , syms , defn=None ):

        """
        initialization

        arguments:
            self  -
            syms  - symbol table for grammar
            defn  - EllyDefinitionReader grammar definition
        """

        self.initzn = [ ] # preset global variables
        self.proc = { }   # named semantic procedures
        self.dctn = { }   # builtin words and semantics
        self.pndx = { }   # standalone procedures
        self.extens = [ ] # 1-branch rule
        self.splits = [ ] # 2-branch rule
        for i in range(NMAX):
            self.extens.append([ ]) # list of 1-branch rules for each syntax type
            self.splits.append([ ]) # list of 2-branch rules for each syntax type`

        self.mat = derivabilityMatrix.DerivabilityMatrix(NMAX)

        # coding of predefined syntax types

        self.START = syms.getSyntaxTypeIndexNumber('sent')
        self.END   = syms.getSyntaxTypeIndexNumber('end')
        self.UNKN  = syms.getSyntaxTypeIndexNumber('unkn')
        self.XXX   = syms.getSyntaxTypeIndexNumber('...')

        # special rule for ... type going to null

        fets = ellyBits.EllyBits(FMAX)
        self.arbr = grammarRule.ExtendingRule(self.XXX,fets)
        self.arbr.cogs = None
        self.arbr.gens = compile(syms,'g',[ ])

        # special rule for SENT->SENT END

        ru = grammarRule.SplittingRule(self.START,fets)
        ru.rtyp = self.END
        ru.ltfet = ru.rtfet = ellyBits.join(fets,fets)
        ru.cogs = None
        ru.gens = None
        self.splits[self.START].append(ru)

        # predefined generative semantic procedures

        self.pndx['defl']  = compile(syms,'g',['left'])
        self.pndx['defr']  = compile(syms,'g',['right'])
        self.pndx['deflr'] = compile(syms,'g',['left','right'])

        self.d1bp = self.pndx['defl']
        self.d2bp = self.pndx['deflr']

        if defn != None: self.define(syms,defn)

    def define ( self , syms , defn ):

        """
        process grammar rules from an EllyDefinitionReader

        arguments:
            self  -
            syms  - grammar symbol table
            defn  - rule definitions

        returns:
            True on success, False otherwise
        """

#       print "defining" , defn , len(defn.buffer) , "lines"

        nor = 0  # number of rules
        now = 0  # number dictionary entries
        nop = 0  # number of procedures

        lno = 0  # line number in definition input

        while True:

            line = defn.readline().lower()
            if len(line) == 0: break
            lno += 1

#           print 'line >' , lno , '[' + line + ']'

            if not isNewRule(line): continue

            c = line[0]
            line = line[2:].strip()

            cogn = [ ]  # for cognitive  semantics
            genr = [ ]  # for generative semantics
            p = cogn    # start with cognitive

            while c != 'i':          # parse semantics
                l = defn.readline()
                lno += 1
                if len(l) == 0:
                    print >> sys.stderr , 'unexpected EOF at' , lno
                    return False
                elif l[:2] == '__':  # end of semantic procedure?
                    break
                elif l[:1] == '_':   # end of cognitive procedure?
                    p = genr
                elif isNewRule(l):
                    defn.unreadline(l)
                    lno -= 1
                    print >> sys.stderr , 'no termination of semantic procedures'
                    print >> sys.stderr , 'line >' , lno , '[' + l + ']'
                    break
                else:
                    p.append(l)       # add line to accumulating procedure

            if c == 'g':
                nor += 1
                dl = definitionLine.DefinitionLine(line)
                first = dl.nextInTail()
                if dl.isEmptyTail():
                    ru = self._doExtend(syms,dl.left,first) # make 1-branch rule
                    ru.gens = self.d1bp                     # default 1-branch procedure
                else:
                    ru = self._doSplit (syms,dl.left,first,dl.nextInTail()) # 2-branch rule
                    ru.gens = self.d2bp                     # default 2-branch procedure
                ru.cogs = compile(syms,'c',cogn)            # compile semantics
                if len(genr) > 0:                           # generative procedure defined?
                    ru.gens = compile(syms,'g',genr)        # if so, replace default
                if ru.cogs == None or ru.gens == None:
                    print >> sys.stderr , 'FAIL g:' , ru.cogs , ru.gens , '[' + line + ']'
                    break
            elif c == 'd':
                now += 1
                dl = definitionLine.DefinitionLine(line);
                ss = syntaxSpecification.SyntaxSpecification(syms,dl.tail)
                if ss == None or ss.synf == None:
                    print >> sys.stderr , 'FAIL d:' , ss , 'tail=' , dl.tail , '[' + line + ']'
                    break
                ru = grammarRule.ExtendingRule(ss.catg,ss.synf.positive)
                ru.cogs = compile(syms,'c',cogn)
                if len(genr) > 0:                           # generative procedure defined?
                    ru.gens = compile(syms,'g',genr)        # if so, compile it
                else:
                    ru.gens = compile(syms,'g',['obtain'])  # otherwise, compile default
                if not dl.left in self.dctn:                # make sure word is in dictionary
                    self.dctn[dl.left] = [ ]                #
                self.dctn[dl.left].append(ru)               # add rule to dictionary
                if ru.cogs == None or ru.gens == None:
                    print >> sys.stderr , 'FAIL d:' , ru.cogs , ru.gens , '[' + line + ']'
                    break
            elif c == 'p':
                nop += 1
                k = line.find(' ')
                if k > 0: line = line[:k]
                self.pndx[line] = compile(syms,'g',genr)    # compile generative procedure
            elif c == 'i':
                k = line.find('=')
                if k <= 0:
                    print >> sys.stderr, 'FAIL: bad initialization:' , line
                    break
                vr = line[:k].strip().lower()
                va = line[k+1:].lstrip()
                self.initzn.append([ vr , va ])             # add initialization
            else:
                print >> sys.stderr, 'FAIL unknown rule type=' , c + ':' , '[' + line + ']'
                break

        print "added"
        print '{0:4} rules'.format(nor)
        print '{0:4} words'.format(now)
        print '{0:4} procedures'.format(nop)

    def _doExtend ( self , syms , s , t ):

        """
        define a 1-branch grammar rule

        arguments:
            self  -
            syms  - grammar symbol table
            s     - left  part of rule
            t     - right part of rule

        returns:
            1-branch extending rule
        """

#       print "extend=",s,'->',t
        ss = syntaxSpecification.SyntaxSpecification(syms,s)
        ns = ss.catg
        fs = ss.synf
        st = syntaxSpecification.SyntaxSpecification(syms,t)
        nt = st.catg
        ft = st.synf
        if ns >= NMAX or nt >= NMAX:
            print >> sys.stderr , s , '->' , t
            print >> sys.stderr , 'too many syntactic categories'
            print >> sys.stderr , ' ns id=' , ns , 'nt id=' , nt
            sys.exit(1)
        if ns < 0 or nt < 0:
            print >> sys.stderr , s , '->' , t
            print >> sys.stderr , 'bad syntax specification'
            sys.exit(1)
        ru = grammarRule.ExtendingRule(ns,fs.positive)
        ru.gens = self.d1bp
        ru.utfet = ft.makeTest()       # precombined positive and negative features for testing
        if s != '...' or t != '...':
            self.extens[nt].append(ru) # add rule to grammar table
            self.mat.join(ns,nt)
        return ru

    def _doSplit ( self , syms , s, t, u ):

        """
        define a 2-branch grammar rule

        arguments:
            self  -
            syms  - grammar symbol table
            s     - left  part of rule
            t     - first half of right part of rule
            u     - second

        returns:
            2-branch splitting rule on success, None otherwise
        """

#       print "split=",s,'->',t,u
        ss = syntaxSpecification.SyntaxSpecification(syms,s)
        ns = ss.catg
        fs = ss.synf
        st = syntaxSpecification.SyntaxSpecification(syms,t)
        nt = st.catg
        ft = st.synf
        su = syntaxSpecification.SyntaxSpecification(syms,u)
        nu = su.catg
        fu = su.synf
        if ns >= NMAX or nt >= NMAX or nu >= NMAX:
            print >> sys.stderr , s , '->' , t , u
            print >> sys.stderr , 'too many syntactic categories'
            print >> sys.stderr , ' ns id=' , ns , 'nt id=' , nt , 'nu id=' , nu
            sys.exit(1)
        if ns < 0 or nt < 0 or nu < 0:
            print >> sys.stderr , s , '->' , t , u
            print >> sys.stderr , 'bad syntax specification'
            sys.exit(1)
        ru = grammarRule.SplittingRule(ns,fs.positive)
        ru.gens = self.d2bp
        ru.ltfet = ft.makeTest()       # precombine positive and negative features for testing
        ru.rtfet = fu.makeTest()       # precombine positive and negative features for testing
        ru.rtyp  = nu
        if nt == self.XXX:
            if nu == self.XXX:
                return None            # cannot have a rule of the form X->... ...
            else:
                self.mat.join(ns,nu)   # for rule of form X->... Y, we can have X->Y
        if t != '...' or u != '...':
            self.splits[nt].append(ru) # add rule to grammar table
            self.mat.join(ns,nt)
        return ru

#
# unit test
#

if __name__ == '__main__':
    import ellyConfiguration
    import dumpEllyGrammar
    import symbolTable

    file = sys.argv[1] if len(sys.argv) > 1 else 'test'
    sym = symbolTable.SymbolTable()
#   print sym
    base = ellyConfiguration.baseSource + '/'
    inp = ellyDefinitionReader.EllyDefinitionReader(base + file + '.g.elly')
    print 'loading' , '[' + file + ']' , len(inp.buffer) , 'lines'
    gtb = GrammarTable(sym,inp)
#   print gtb

    dumpEllyGrammar.dumpAll(sym,gtb,5)
