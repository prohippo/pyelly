#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# grammarTable.py : 03dec2015 CPM
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

import symbolTable
import syntaxSpecification
import cognitiveProcedure
import generativeProcedure
import derivabilityMatrix
import grammarRule
import ellyChar
import ellyBits
import ellyDefinitionReader
import ellyException
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
        cp = cognitiveProcedure.CognitiveProcedure(syms,inps)
        return cp if cp.logic != None else None
    elif clss == 'g':
        gp = generativeProcedure.GenerativeProcedure(syms,inps)
        return gp if gp.logic != None else None
    else:
        print >> sys.stderr , 'bad semantic procedure class'
        return None

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

        exceptions:
            TableFailure on error
        """

        self.initzn = [ ] # preset global variables
        self.proc = { }   # named semantic procedures
        self.dctn = { }   # builtin words and semantics
        self.pndx = { }   # standalone procedures
        self.extens = [ ] # 1-branch rule
        self.splits = [ ] # 2-branch rule
        for _ in range(symbolTable.NMAX):
            self.extens.append([ ]) # list of 1-branch rules for each syntax type
            self.splits.append([ ]) # list of 2-branch rules for each syntax type`

        self.mat = derivabilityMatrix.DerivabilityMatrix(symbolTable.NMAX)

        # coding of predefined syntax types

        self.START = syms.getSyntaxTypeIndexNumber('sent')
        self.END   = syms.getSyntaxTypeIndexNumber('end')
        self.UNKN  = syms.getSyntaxTypeIndexNumber('unkn')
        self.SEPR  = syms.getSyntaxTypeIndexNumber('sepr')
        self.XXX   = syms.getSyntaxTypeIndexNumber('...')

        # special rule for ... type going to null

        fets = ellyBits.EllyBits(symbolTable.FMAX)
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

        # special rule for RS (ASCII record separator)

        ru = grammarRule.ExtendingRule(self.SEPR,fets)
        ru.cogs = None
        ru.gens = None
        self.dctn[ellyChar.RS] = [ ru ] # should be only rule here ever

        # predefined generative semantic procedures

        self.pndx['defl']  = compile(syms,'g',['left'])
        self.pndx['defr']  = compile(syms,'g',['right'])
        self.pndx['deflr'] = compile(syms,'g',['left','right'])

        self.d1bp = self.pndx['defl']  # default 1-branch generative semantics
        self.d2bp = self.pndx['deflr'] # default 2-branch

        if defn != None:
            if not self.define(syms,defn):
                print >> sys.stderr , 'grammar table definition FAILed'
                raise ellyException.TableFailure

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

        skp = 0  # skipped lines

        nor = 0  # number of rules
        now = 0  # number dictionary entries
        nop = 0  # number of procedures

        lno = 0  # line number in definition input

        eno = 0  # error count

        while True:

            line = defn.readline().lower()
            if len(line) == 0: break
            lno += 1

#           print 'after line' , lno , '[' + line + ']'

            if not isNewRule(line):
                print '*  skipped: [' , line , ']'
                skp += 1
                continue

            c = line[0] # single char indicating type of rule to define
            line = line[2:].strip()

            cogn = [ ]  # for cognitive  semantics
            genr = [ ]  # for generative semantics
            p = cogn    # start with cognitive

            if c != 'i':                 # not global variable initialization?
                dl = line
                dlno = lno
                while True:
                    l = defn.readline()  # if so, parse semantics
                    lno += 1
                    if len(l) == 0:
                        print >> sys.stderr , '** unexpected EOF at' , lno
                        return False
                    elif l[:2] == '__':  # end of semantic procedure?
                        break
                    elif l[:1] == '_':   # end of cognitive procedure?
                        p = genr
                    elif isNewRule(l):
                        defn.unreadline(l)
                        lno -= 1
                        print >> sys.stderr , '** no termination of semantic procedures'
                        print >> sys.stderr , '*  after line' , dlno , '[' + dl + ']'
                        eno += 1
                        c = '?'
                        break
                    else:
                        p.append(l)       # add line to accumulating procedure

            if c == 'g':                  # grammar rule?
                nor += 1
                dl = definitionLine.DefinitionLine(line)
                first = dl.nextInTail()
                if dl.isEmptyTail():
                    ru = self._doExtend(syms,dl.left,first) # make 1-branch rule
                    if ru == None:
                        print >> sys.stderr , '*  after line' , lno , '[' , line , ']'
                        eno += 1
                        continue
                    ru.gens = self.d1bp                     # default 1-branch procedure
                else:
                    ru = self._doSplit (syms,dl.left,first,dl.nextInTail()) # 2-branch rule
                    if ru == None:
                        print >> sys.stderr , '*  after line' , lno , '[' , line , ']'
                        eno += 1
                        continue
                    ru.gens = self.d2bp                     # default 2-branch procedure
                ru.cogs = compile(syms,'c',cogn)            # compile semantics
                if len(genr) > 0:                           # generative procedure defined?
                    ru.gens = compile(syms,'g',genr)        # if so, replace default
                if ru.cogs == None or ru.gens == None:
                    print >> sys.stderr , '** ERROR g: [' , line , ']'
                    eno += 1
                    continue
            elif c == 'd':            # internal dictionary entry?
                now += 1
                dl = definitionLine.DefinitionLine(line)
                try:
                    ss = syntaxSpecification.SyntaxSpecification(syms,dl.tail)
                except ellyException.FormatFailure:
                    print >> sys.stderr , '** ERROR d: [' , line , ']'
                    eno += 1
                    continue
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
                    print >> sys.stderr , '** ERROR d: [' , line , ']'
                    eno += 1
                    continue
            elif c == 'p':            # semantic subprocedure?
                k = line.find(' ')    # name should have no spaces
                if k > 0 or len(genr) == 0:
                    print >> sys.stderr , '** ERROR p: bad format [' , line , ']'
                    eno += 1
                    continue
                if line in self.pndx:
                    print >> sys.stderr , '** ERROR p: subprocedure' , line , 'redefined'
                    eno += 1
                    continue
                nop += 1
                self.pndx[line] = compile(syms,'g',genr)    # compile generative procedure
            elif c == 'i':            # global variable initialization?
                k = line.find('=')
                if k <= 0:
                    print >> sys.stderr, '** bad initialization:' , '[' + line + ']'
                    eno += 1
                    continue
                vr = line[:k].strip().lower()
                va = line[k+1:].lstrip()
                self.initzn.append([ vr , va ])             # add initialization
            else:
                print >> sys.stderr, '** unknown rule type=' , c + ':'
                print >> sys.stderr, '*  after line' , lno , '[' + line + ']'
                eno += 1
                continue

#       print 'SKIP' , skp
        if skp > 0:
            print >> sys.stderr , '**' , skp , 'uninterpretable input lines skipped'
            eno += skp

        if eno > 0:
            print >> sys.stderr , '**' , eno , 'grammar errors in all'
            return False

        print "added"
        print '{0:4} rules'.format(nor)
        print '{0:4} words'.format(now)
        print '{0:4} procedures'.format(nop)
        return True

    def _doExtend ( self , syms , s , t ):

        """
        define a 1-branch grammar rule

        arguments:
            self  -
            syms  - grammar symbol table
            s     - left  part of rule
            t     - right part of rule

        returns:
            1-branch extending rule on success, otherwise None
        """

#       print "extend=",s,'->',t
        if t == None or len(t) == 0:
            print >> sys.stderr , '** incomplete grammar rule'
            return None
        try:
            ss = syntaxSpecification.SyntaxSpecification(syms,s)
            ns = ss.catg
            fs = ss.synf
            st = syntaxSpecification.SyntaxSpecification(syms,t)
            nt = st.catg
            ft = st.synf
        except ellyException.FormatFailure:
            print >> sys.stderr , '** bad syntactic category or features'
            return None
        if ns >= symbolTable.NMAX or nt >= symbolTable.NMAX:
            print >> sys.stderr , 'too many syntactic categories'
            return None
        if ns < 0 or nt < 0:
            print >> sys.stderr , '** bad syntax specification'
            return None
        fs.negative.complement()
        ru = grammarRule.ExtendingRule(ns,fs.positive,fs.negative)
#       print 'extd rule=' , unicode(ru)
        ru.gens = self.d1bp
        ru.utfet = ft.makeTest()       # precombined positive and negative features for testing
        if s != '...' or t != '...':
            self.extens[nt].append(ru) # add rule to grammar table
            self.mat.join(ns,nt)
            return ru
        else:
            print >> sys.stderr , '** bad type 0 rule'
            return None

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

#       print 'split=' , s , '->' , t , u
        if t == None or len(t) == 0 or u == None or len(u) == 0:
            print >> sys.stderr , '** incomplete grammar rule'
            return None
        try:
#           print 's=' , s
            ss = syntaxSpecification.SyntaxSpecification(syms,s)
            ns = ss.catg
            fs = ss.synf
#           print 'fs=' , fs
            st = syntaxSpecification.SyntaxSpecification(syms,t)
            nt = st.catg
            ft = st.synf
            su = syntaxSpecification.SyntaxSpecification(syms,u)
            nu = su.catg
            fu = su.synf
        except ellyException.FormatFailure:
            return None
        if ns >= symbolTable.NMAX or nt >= symbolTable.NMAX or nu >= symbolTable.NMAX:
            print >> sys.stderr , 'too many syntactic categories'
            return None
        if ns < 0 or nt < 0 or nu < 0:
            print >> sys.stderr , '** bad syntax specification'
            return None
        fs.negative.complement()
        ru = grammarRule.SplittingRule(ns,fs.positive,fs.negative)
#       print 'splt rule=' , unicode(ru)
        ru.gens = self.d2bp
        ru.ltfet = ft.makeTest()       # combine positive and negative features for testing
        ru.rtfet = fu.makeTest()       # combine positive and negative features for testing
        ru.rtyp  = nu
        if t == '...':
            if u == '...':
                print >> sys.stderr , '** bad type 0 rule'
                return None            # cannot have a rule of the form X->... ...
            else:
                self.mat.join(ns,nu)   # for rule of form X->... Y, we see X->Y
        else:
            self.mat.join(ns,nt)       # otherwise, treat as normal 2-branch
        self.splits[nt].append(ru)     # add rule to grammar table
        return ru

#
# unit test
#

if __name__ == '__main__':

    import ellyConfiguration
    import dumpEllyGrammar

    filn = sys.argv[1] if len(sys.argv) > 1 else 'test'
    sym = symbolTable.SymbolTable()
#   print sym
    base = ellyConfiguration.baseSource + '/'
    inp = ellyDefinitionReader.EllyDefinitionReader(base + filn + '.g.elly')
    if inp.error != None:
        print inp.error
        sys.exit(1)
    print 'loading' , '[' + filn + ']' , len(inp.buffer) , 'lines'
    try:
        gtb = GrammarTable(sym,inp)
#       print gtb
        dumpEllyGrammar.dumpAll(sym,gtb,5)
    except ellyException.TableFailure:
        print >> sys.stderr , 'exiting'
