#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# compoundTable.py : 24sep2018 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2018, Clinton Prentiss Mah
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
for defining templates to identify multi-word expressions in English like
names of organizations, inflected idioms, and chemical nomenclature
"""

import sys
import ellyChar
import ellyWildcard
import ellyException
import syntaxSpecification
import featureSpecification
import deinflectedMatching

Catg = u'%'       # marker for template word class

nCat = Catg + 'n' # numeric substring
cCat = Catg + 'c' # capitalized alphabetic substring
uCat = Catg + 'u' # uncapitalized
xCat = Catg + 'x' # uncapitalized with exceptions
zCat = Catg + '*' # uncapitalized with suffix
bCat = Catg + 'b' # irregular form of TO BE
pCat = Catg + 'p' # common particle or preposition

Tdel = [ '.' , ' ' , '-' ] # delimiters for template elements

Stop = [                   # exception words
    'a' , 'about' , 'above' , 'after' , 'all' , 'also' , 'among' , 'an' , 'any' , 'as' ,
    'at' , 'be' , 'below' , 'both' , 'but' , 'by' , 'down' , 'each' , 'else' , 'even' ,
    'ever' , 'every' , 'few' , 'from' , 'he' , 'her' , 'here' , 'him' , 'his' , 'i' ,
    'into' , 'is' , 'it' , 'its' , 'many' , 'me' , 'more' , 'most' , 'much' , 'my' ,
    'never' , 'no' , 'none' , 'nor' , 'not' , 'of' , 'off' , 'on' , 'only' , 'other' ,
    'our' , 'out' , 'over' , 'own' , 'she' , 'since' , 'so' , 'some' , 'such' , 'than' ,
    'that' , 'the' , 'their' , 'them' , 'then' , 'there' , 'these' , 'they' , 'this' , 'those' ,
    'to' , 'too' , 'until' , 'up' , 'upon' , 'us' , 'we' , 'with' , 'you' , 'your'
]

#
# predefined classes of template elements
# (these are English only!)
#

preClass = {
    bCat : ['is','am','are','was','were','be','being','been'] ,
    pCat : ['in','of','on','for']
}

#
########

def numrc ( s ):
    """
    check that all chars are digits
    arguments:
        s  - list of chars
    returns:
        True if string is all digits, False otherwise
    """
#   print 'numerc s=' , s
    if len(s) == 0: return False
    for c in s:
#       print 'c=' , c , type(c)
        if c < '0' or c > '9': return False
    return True

def alphc ( s ):
    """
    check that all chars are letters
    arguments:
        s   - list of chars
    returns:
        True if string is all alphabetic, False otherwise
    """
#   print 'alphc s=' , s
    if len(s) == 0: return False
    for c in s:
#       print 'c=' , c , type(c) , len(c)
        if not ellyChar.isLetter(c): return False
    return True

def alphcuns ( s ):
    """
    check that all chars are letters and do not form a Stop
    arguments:
        s   - list of chars
    returns:
        True if string is all alphabetic and unstopped, False otherwise
    """
#   print 's=' , s
    return True if alphc(s) and not u''.join(s) in Stop else False

def alphcsuf ( s , x ):
    """
    check that all chars are letters and and end with specified suffix
    arguments:
        s   - list of chars
        x   - suffix as char list
    returns:
        True if string is all alphabetic and unstopped, False otherwise
    """

    lx = len(x)
    if lx > len(s) - 2 or not alphc(s):
        return False
    else:
        return True if s[-lx:] == x else False

def bound ( segm ):

    """
    get maximum limit on string for template matching
    (override this method if necessary)

    arguments:
        segm  - text segment to match against

    returns:
        char count
    """

#   print 'segm=' , segm
    lm = len(segm)   # limit can be up to total length of text for matching
    ll = 0
    while ll < lm:   # look for first break in text segment
        c = segm[ll]
        if c in [ ellyChar.ELLP , ellyChar.NDSH , ellyChar.MDSH ]:
            break
        if c == ',' and ll < lm - 1 and segm[ll+1] == ' ':
            break
        ll += 1
#   print 'll=' , ll , ', lm=' , lm
    ll -= 1
    while ll > 0:    # exclude trailing non-alphanumeric from matching
                     # except for '.' and '*' and bracketing
        c = segm[ll]
        if c in ellyWildcard.Trmls or c == '*' or ellyChar.isLetterOrDigit(c): break
        ll -= 1
#   print 'limit=' , ll + 1
    return ll + 1

Inter = [ ' ' , '-' , '.' , '_' ]

def divide ( segm , offs ):

    """
    get limit on next word in string for template matching
    (override this method if necessary)

    arguments:
        segm  - text segment to match against
        offs  - where to start matching

    returns:
        char count
    """

    lm = len(segm)
    ll = offs
    while ll < lm:
        if segm[ll] in Inter:
            break
        ll += 1
    return ll - offs

#
############ class definitions
#

class Template(object) :

    """
    a template to be matched by words in an input stream

    attributes:

        lstg  - elements to be matched
        catg  - for syntax
        synf  - syntactic features
        semf  - semantic features
        bias  - plausibility score

        _errcount - for reporting problems
    """

    def __init__ ( self , symtb , defr ):

        """
        initialization

        arguments:
            self  -
            symtb - symbol table for interpreting syntax
            defr  - definition input string
        """

        self._errcount = 0
#       print 'defr=' , defr
        ru = defr.split(' : ')
        if len(ru) != 2:
            self._err('incomplete template',defr)
            return
        [ elems , defns ] = ru
        rw = elems.split(' ')
        if len(rw) < 2:
            self._err('trivial template',defr)
            return
        le = [ ]
        for w in rw:
#           print 'w=' , w
            x = w.strip()
            lx = len(x)
            if lx == 0:
                self._err('null template element',defr)
                return
            if x[0] == '%':
                if lx > 1 and ellyChar.isLetter(x[1]):
                    if lx > 2:
                        if x[1] != '*':
                            self._err('bad class ID',defr)
                            return
                    x = x.lower()
            le.append(x)
        if self._errcount > 0: return
        self.listing = le

        de = defns.split(' ')
        lde = len(de)
        if lde != 1 and lde != 3:
            self._err('bad template definition',defr)
            return
        syns = de[0]
        sems = de[1] if lde > 1 else None
        try:
            spec = syntaxSpecification.SyntaxSpecification(symtb,syns)
            semf = featureSpecification.FeatureSpecification(symtb,sems,True)
        except ellyException.FormatFailure:
            self._err('bad definition' , defr)
            return

        self.lstg = le
        self.catg = spec.catg
        self.synf = spec.synf.positive
        self.semf = semf.positive
        self.bias = int(de[2]) if lde > 1 else 0
#       print 'err=' , self._errcount

    def _err ( self , msg , lns='' ):

        """
        report definition error

        arguments:
            self  -
            msg   - message string
            lns   - template definition
        """

        self._errcount += 1
        print >> sys.stderr , '** template ERROR:' , msg ,
        print >> sys.stderr , '' if len(lns) == 0 else 'at [' + lns + ']'

    def check ( self ):

        """
        check for error

        arguments:
            self

        returns:
            error count
        """
#       print 'check=' , self._errcount
        return self._errcount

class CompoundTable(deinflectedMatching.DeinflectedMatching):

    """
    templates for recognizing compound multi-word expressions

    attributes:
        tmpl      - an indexed list of templates
        cfns      - hashed recognizers for all element classes
        ucls      - user-defined classes

        syms      - symbol table

        _errcount - running input error count
     """

    def __init__ ( self , syms , dfls ):

        """
        initialization

        arguments:
            self  -
            syms  - Elly grammatical symbol table
            dfls  - definition elements in list

        exceptions:
            TableFailure on error
        """

        super(CompoundTable,self).__init__()

        self.tmpl = [ ]
        self.cfns = { }
        self.ucls = { }

        for cy in preClass.keys():
            self.cfns[cy] = None

        self.cfns[nCat] = numrc
        self.cfns[cCat] = alphc
        self.cfns[uCat] = alphc
        self.cfns[xCat] = alphcuns
        self.cfns[zCat] = alphcsuf

        self._errcount = 0

        self.load(syms,dfls)

        self.syms = syms

    def _err ( self , s='malformed definition' , l='' ) :

        """
        for error reporting

        arguments:
            self -
            s    - error message
        """

        self._errcount += 1
        print >> sys.stderr , '** template ERROR:' , s ,
        print >> sys.stderr , '' if l=='' else 'at ' + l

    def load ( self , stb , defn ):

        """
        get templates and user-defined word classes from input

        arguments:
            self  -
            stb   - Elly symbol table
            defn  - Elly definition reader for classes and templates

        exceptions:
            TableFailure on error
        """

        clss = [ ]                            # element classes
        while True:
            l = defn.readline()               # next definition line
            if len(l) == 0: break             # EOF check
            s = l.split(':=')                 # look for user-defined class
            if len(s) == 2:
                nme = s[0].strip()
                if len(nme) != 2 and not ellyChar.isLetterOrDigit(nme[1]):
                    self._err('improper class ID')
                    continue
                if nme in preClass:
                    self._err('cannot change predefined classes')
                    continue
                ls = s[1].split(',')             # list of words for class
                ls = list(w.strip() for w in ls) # just in case of extra spaces
#               print 'for class, ls=' , ls
                if not nme in self.ucls:      # define a new template category?
                    self.ucls[nme] = [ ]
                self.ucls[nme].extend(ls)     # add list of words to class
#               print 'class=' , self.ucls[nme]
                self.cfns[nme] = None
            else:
                tm = Template(stb,l)          # create a new template
                if tm.check() > 0:            # any problem here is fatal
#                   print 'template error'
                    self._errcount += 1
                    continue
                for elm in tm.lstg:           # get unique template categories
                    if elm[0] == Catg:
                        if not elm in clss:
                            clss.append(elm)
                self.tmpl.append(tm)          # add template to table

        missg = [ ]                           # to collect missing definitions
        for cx in clss:                       # check user-defined categories
            if not cx in self.cfns:
                if cx[1] != '*':
                    missg.append(cx)          # note if unsupported by class list
        lm = len(missg)
        if lm > 0:                            # this is a FATAL error
            print >> sys.stderr , lm , 'undefined template categories=' , missg
            self._errcount += lm
        if self._errcount > 0:
            print >> sys.stderr , 'table error count=' , self._errcount
            raise ellyException.TableFailure('templates')

    def fun ( self , cod , chs ):

        """
        element comparison with class for template matching

        arguments:
            self  -
            cod   - template class code, like %b
            chs   - list of chars to check

        returns:
            True on match, False otherwise
        """

#       print 'cod=' , cod , 'chs=' , chs
        if cod in self.cfns:
            f = self.cfns[cod]
#           print 'f=' , f
            if f != None:
                return f(chs)  # saved functions will scan char list
        if len(cod) > 2:
            cd = cod[:2]
            if not cd in self.cfns:
                return False
            else:
                f = self.cfns[cd]
                return f(chs,list(cod[2:]))

        chx = u''.join(chs)    # need string for lookup with "in"

        if cod in preClass:
            return chx in preClass[cod]
        elif cod in self.ucls:
            return chx in self.ucls[cod]
        else:
            return False

    def match ( self , txs , ptr ):

        """
        compare text segment against word templates

        arguments:
            self  -
            txs   - segment to match against
            ptr   - parse tree in which to put leaf nodes for final matches

        returns:
            maximum text length matched by any template
        """

#       print 'comparing' , txs

        if len(self.tmpl) == 0: return 0        # no matches if no templates

        if len(txs) == 0: return 0              # string is empty

        lim = bound(txs)                        # get limit for matching
        tx = list(x.lower() for x in txs[:lim]) # separate copy to scan

#       print 'tx=' , tx

#       self.dump()

        dv = [ ]
        it = 0
        while it < lim:
            lt = divide(tx,it)                  # predivide input for matching
            dv.append([ not txs[it].isupper() , tx[it:it+lt] ])
            it += lt
            if it < lim and tx[it] in [ '-' , '.' ]:
                dv.append( [ True , tx[it] ] )  # hyphen and period must be matched
            it += 1
        nd = len(dv)

#       print 'dv=' , dv

        nr = 0
        res = [ ]                               # listing of matches
                                                # with longest match length at start
#       print len(self.tmpl) , 'templates'
        for t in self.tmpl:
            tl = t.listing                      # next template to apply
#           print 'tl=' ,  tl
            ll = len(tl)
            if ll > nd:                         # enough text to match?
                continue
            m = -1                              # accumulating match length
            for i in range(ll):
                m += 1
#               print 'i=' , i , 'm=' , m
                dvt = dv[i]                     # align template with input
                elm = tl[i]
#               print 'dvt=' , dvt , 'elm=' , elm
                lt = len(dvt[1])
#               print 'lt=' , lt
                if elm[0] == Catg:              # category element?
#                   print 'elm=' , elm , dvt[0]
                    if elm[1] == 'c' and dvt[0]:
                        break
                    if elm[1] == 'u' and not dvt[0]:
                        break
#                   print 'Catg check=' , elm[1]
                    if not self.fun(elm,dvt[1]):
                        break
#                   print 'success'
                elif lt < len(elm):             # enough text to match?
                    break
                else:
                    n = self.doMatchUp(elm,dvt[1])
#                   print 'literal match n=' , n
                    if n == 0:
                        break
#               print 'm=' , m , 'lt=' , lt
                m += lt                         # accumulate total match length
#               print 'new m=' , m
            else:
#               print 'whole template matched'
                if m < nr:                      # new matches must be as long as old ones
                    continue
                elif m > nr:
                    res = [ ]                   # longer match means to discard older ones
                    nr = m
                res.append(t)                   # save new match
#           print 'end template match'

#       print 'nr=' , nr
        if nr == 0:
            return 0
        else:
            capd = txs[0].isupper()             # check original text
            for t in res:                       # result list should now be only templates
                if ptr.addLiteralPhraseWithSemantics(
                    t.catg,t.synf,t.semf,t.bias,cap=capd
                ):                              # make phrase for multiword compound
#                   print 'success!' , 'match length=' , nr
                    ptr.lastph.lens = nr        # save its length
            return nr

    def dump ( self ) :

        """
        show all templates

        arguments:
            self
        """

        print ''
        for ck in self.ucls:
            print ck , ':=' , self.ucls[ck]
        print '----------------'
        for t in self.tmpl:
            typn = self.syms.getSyntaxTypeName(t.catg)
            print t.lstg , 'typ=' + str(t.catg) , typn ,
            print '[' + t.synf.hexadecimal() + '] [' + t.semf.hexadecimal() + '] =' + str(t.bias)
        print '----------------'

#
# unit test
#

if __name__ == '__main__':

    import ellyConfiguration
    import ellyDefinitionReader
    import parseTest
    import stat
    import os

    mode = os.fstat(0).st_mode       # to check for redirection of stdin (=0)
    interact = not ( stat.S_ISFIFO(mode) or stat.S_ISREG(mode) )

    ctx = parseTest.Context()        # dummy interpretive context for testing
    tre = parseTest.Tree(ctx.syms)   # dummy parse tree for testing
    print ''

    basn = ellyConfiguration.baseSource + '/'
    filn = sys.argv[1] if len(sys.argv) > 1 else 'test' # which FSA definition to use
    ins = ellyDefinitionReader.EllyDefinitionReader(basn + filn + '.t.elly')

    print 'template test with' , '<' + filn + '>'

    if ins.error != None:
        print ins.error
        sys.exit(1)

    comp = None
    try:
        comp = CompoundTable(ctx.syms,ins) # load templates
    except ellyException.TableFailure:
        print 'no compound template table generated'
        sys.exit(1)

    comp.dump()

    print 'enter multiword compounds to recognize'

    while True: # try test examples

        if interact: sys.stdout.write('> ')
        te = sys.stdin.readline().strip()
        if len(te) == 0: break
        print 'text=' , '[' , te , ']'
        nma = comp.match(list(te),tre)
        print 'from <'+ te + '>' , nma , 'chars matched' , '| leaving <' + te[nma:] + '>'

    if interact: sys.stdout.write('\n')

    tre.showQueue()
