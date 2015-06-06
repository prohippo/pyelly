#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# treeLogic.py : 05jun2015 CPM
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
basic finite automata for morphological analysis
"""

import sys
import ellyChar
import ellyException
import unicodedata

                 # predefined restoration options
Fail    = u'?!'  # fail
RestorE = u'e?'  # conditionally restore with inflectional stemming method
Add     = u'+'   # unconditionally restore with specified string

Bound   = u'|'   # match word boundary

class Node(object):

    """
    tree node for automaton logic

    attributes:
        condn - match constraint
        actns - actions on match
        contn - where to go on successful match
        id    - node ID
    """

    Ni = 1 # node labeling for debugging

    def __init__ ( self ):
        """
        initialization
        arguments:
            self
        """

        self.condn = -1   # initally no condition specified
        self.actns = None # no actions
        self.contn = { }  # no continuations for match
        self.id = 0       # no rule number

    def __unicode__ ( self ):
        """
        how to show Node instance for debugging
        arguments:
            self
        returns:
            Unicode string
        """

        if self.id == 0:
            return u'empty Node'
        else:
            return u'Node for rule ' + unicode(self.id)

    def __str__ ( self ):
        """
        ASCII string representation

        arguments:
            self

        returns:
            string representation
        """

        return unicodedata.normalize('NFKD',unicode(self)).encode('ascii','ignore')

    def delta ( self , left ):
        """
        get expected change in token length after action
        arguments:
            self  -
            left  - chars left after matching
        returns:
            integer change in length
        """

#       print 'left=' , left
        if self.actns == None:
            return 0
        else:
            rest = self.actns.resto
            if len(rest) == 0:
                nrest = 0
            elif rest[0] == 'e?':
                nrest = 0 if left < 4 else 1
            else:
                nrest = len(rest)
#           print 'nsave=' , self.actns.nsave
#           print 'nrest=' , nrest , rest , list(rest)
            return self.actns.nsave + nrest

    def tag ( self ):
        """
        assign label to node for debugging
        arguments:
            self
        """

        self.id = Node.Ni
        Node.Ni += 1

class Action(object):

    """
    action to take on making a match in tree logic

    attributes:
        tree  - TreeLogic reference
        nsave - number of matched chars to keep
        resto - what to append to root after adding back any matched chars
        recur - flag to look for yet another match
        ndrop - what to remove for an affix
        amod  - what to prepend to affix after removal of extra matched chars
    """

    def __init__ ( self , tree , nsave , resto , recur=False , post='' ):
        """
        initialization
        arguments:
            self  -
            tree  - logic tree containing node with action
            nsave - how many matched chars to keep in root
            resto - how to restore root after keeping
            recur - recursive matching to look for more affixes?
            post  - how to define a removed affix
        """

        self.tree  = tree
        self.nsave = nsave
        self.resto = resto
        self.recur = recur
        self.ndrop = 0      # default
        if post != '':      # no specification
            if ellyChar.isDigit(post[0]):
                self.ndrop = int(post[0]) # expect only single digit here, if any
                post = post[1:]           # rest of action string
        self.amod = post

    def __unicode__ ( self ):
        """
        how to show Action instance for debugging
        arguments:
            self
        returns:
            Unicode string
        """

        hdr   = u'Action: len +'
        rst   = u'root' + self.resto[0] + u'[' + ''.join(self.resto[1:]) + u']'
        mod   = u', len -' + unicode(self.ndrop) + u' + [' + self.amod + u']'
        recur = u' recur' if self.recur else u' stop'
        return hdr + unicode(self.nsave) + ' ' + rst + mod + recur

    def __str__ ( self ):
        """
        ASCII string representation

        arguments:
            self

        returns:
            string representation
        """

        return unicodedata.normalize('NFKD',unicode(self)).encode('ascii','ignore')

    def applyRVS ( self , token , count , tree ):
        """
        apply action to the end of char sequence
        arguments:
            self  -
            token - list of chars
            count - how many matched
            tree  - tree logic involved
        returns:
            True on success, False otherwise
        """

#       print "applyRVS" , token
#       print self
        o = self.resto[0]      # type of action
        if o == Fail: return False

#       print 'oprn=' , o
        r = self.resto[1:]     # chars to append to root
#       print 'rstr=' , r
        n = count - self.nsave # computed suffix length
#       print 'count=' , count , 'nsave=' , self.nsave , 'ndrop=' , self.ndrop , 'n=' , n
        lst = token.root

        k = n - self.ndrop     # adjusted suffix length
#       print 'k=' , k
        x = u''.join(lst[-k:]) if k > 0 else u''
        sfx = u'-' + self.amod + x
        if len(sfx) > 1:
#           print 'sfx=' , sfx
            token.addSuffix(sfx)
#           print 'sufs=' , token.getSuffixes()

#       print 'org' , token
        if n > 0: token.root = lst[:-n]
#       print 'adj' , token
        lst = token.root

#       print 'lst=' , lst

        if o == Add:
#           print 'Add' , r
            if len(r) > 0:
                lst.extend(r)
            return True
        elif o == RestorE and tree.infl != None:
#           print 'prerest token=' , token.root
            try:
                sta = tree.infl.applyRest(token)
                return ( sta != 0 )
            except ellyException.StemmingError as e:
                print >> sys.stderr , '** WARNING:' , e
                return False
        else:
#           print 'fail'
            return False

    def applyFWD ( self , token , count ):
        """
        apply action to the end of char sequence
        arguments:
            self  -
            token - list of chars
            count - how many matched
        returns:
            True on success, False otherwise
        """

        o = self.resto[0]
#       print 'o=' , o
        if o == Fail: return False

        r = self.resto[1:]
        n = count - self.nsave
        lst = token.root
#       print 'lst=' , lst , 'n=' , n , 'r=' , r

        pfx = u''.join(lst[:n]) + u'+'
#       print 'pfx=' , pfx
        token.addPrefix(pfx)

        token.root = lst[n:]
        lst = token.root

        if o == Add:
#           print 'add' , r
            r = r[::-1]         # reverse chars
            for c in r:
                lst.insert(0,c) # insert into root
            return True
        else:
            return False

class TreeLogic(object):

    """
    automaton defined as binary decision tree
    (This is a base class that does nothing.
     You must define a subclass with the sequence()
     and rewrite() methods overridden)

    attributes:
        indx - first-level nodes of tree by matching char
        infl - inflection stemmer for any root restoration
        addn - special addition for root modification
        rest - restoration to apply
    """

    addn = None  # nothing unless overridden

    def __init__ ( self , inp=None ):
        """
        set up for tree logic
        arguments:
            self  -
            inp   - definition reader
        exceptions:
            TableFailure on error
        """

        self.indx = { }
        self.rest = None
        if inp != None: self.build(inp)
#       print rest

    def sequence ( self , lstg ):
        """
        get a list of chars for matching
        arguments:
            self  -
            lstg  - original char list
        returns:
            sequenced char list on success, None otherwise
        """

        print >> sys.stderr , "sequence DUMMY"
        return [ ]  # dummy code to be overridden in subclass

    def rewrite ( self , token , leng , node ):
        """
        rewrite an Elly token according to node match
        arguments:
            self  -
            token - Elly token
            leng  - how many chars matched
            node  - actual match made
        returns:
            True on success, False otherwise
        """

        print >> sys.stderr , "rewrite DUMMY"
        return True  # dummy code to be overridden in subclass

    def match ( self , token ):
        """
        compare an Elly token against a tree
        and possibly modify that token after a match
        arguments:
            self  -
            token - input Elly token
        returns:
            True on match, False otherwise
        """

#       print token

        rec = True      # recursion flag
        suc = False     # success   flag

        while rec:      # continue comparisons recursively while flag is True

            if len(token.root) < 3: break               # stop if token root is too short

            seq = self.sequence(token.root) + [ Bound ] # token sequence plus sentinel

#           print type(self).__name__ ,'seq=' , seq

            chs = seq[0]    # first char in sequence to match
            if not chs in self.indx:
                return suc

            nod = self.indx[chs] # starting node in tree
#           print 'start nod.id=' , nod.id , '/' , (Node.Ni - 1)
            lvl = 0         # level in tree
            mst = [ ]       # match stack
            lmt = len(seq)  # sequence length = maximum possible match
#           print 'lmt=' , lmt , 'seq=' , seq

            while True:
#               print 'nod=' , nod
                if nod.actns != None:          # at node with action?
                    mst.append([ nod , lvl ])  # if so, save it on stack
                lvl += 1
#               print 'lvl=' , lvl
                if lvl == lmt: break           # continue comparing to end of token
                ch = seq[lvl]
#               print 'ch=' , ch , 'contn=' , nod.contn.keys()
                if not ch in nod.contn: break  # quit on mismatch
                nod = nod.contn[ch]            # go down to next node in tree

#           for mr in mst:
#               print ' |' , mr[0].id , mr[1]

            while len(mst) > 0:                # match stack empty?

                mr = mst.pop()                 # if not, get most recent match
                nod = mr[0]
                nom = mr[1] + 1

                uch = seq[nom] if nom < lmt else u'_' # first unmatched char

                con = nod.condn                # node condition for accepting  match

                nln = lmt - nom
                nln += nod.delta(nln)          # how chars expected after action
#               print 'lmt=' , lmt , 'nom=' , nom
#               print 'check rule=' , nod.id
#               print 'con=' , con , 'nln=' , nln
#               print 'uch=' , uch

                if con != 0 and nln < 3:       # this must leave at least 2 letters
                    continue                   #   plus sentinel!

#               print 'condition'
                if con == 0:                   # accept match with no action?
#                   print '0 condition'
                    return suc                 # if so, done

                elif con == 1:                 # unconditionally accept?
                    break                      # if so, act on this match

                elif con == 2:                 # first unmatched is consonant?
                    if uch != '|' and not ellyChar.isVowel(uch):
                        break                  # if so, act on match

                elif con == 3:                 # first unmatched is consonant or U?
                    if not ellyChar.isStrictVowel(uch)  :
                        break                  # if so, act on match

            else: ## if loop NOT terminated by break, no acceptable match
#               print 'suc=' , suc , '@'
                return suc                     # we are done

            suc = True                         # note acceptable match

#           print 'nod.id=' , nod.id , '/' , (Node.Ni - 1)

            #
            # take action for longest accepted match
            #

#           print '1 token=' , token
            self.rewrite(token,nom,nod)        # take action for node
            rec = nod.actns.recur              # update recursion flag

#           print '2 token=' , token
#           print 'rec=' , rec

#       print 'suc=' , suc
        return suc

    def build ( self , inp ):

        """
        build tree logic from definition reader input

        arguments:
            self  -
            inp   - definition text for logic

        exceptions:
            TableFailure on error
        """

        if inp == None:
            return

        nerr = 0                   # error count

        # read in affixes and associated actions

        while True:

            line = inp.readline()  # next input line
            if line == u'':        # check for EOF
                break

            modf = ''
            elem = line.strip().lower().split(' ')
#           print 'elem=' , elem
            le = len(elem)
            if le < 4:
                nerr += 1
                print >> sys.stderr , "** affix error: incomplete input"
                print >> sys.stderr , "*  at: [" , line , "]"
                continue                  # skip incomplete line
            if le > 4:                    # affix mod specified?
                modf = elem.pop()         # if so, get it
#               print elem[0] , modf
            do = elem.pop()               # note main action

            # get affix within definition line

            aff = list(elem.pop(0))       # affix as list of chars

            # check for proper form

            aff = self.sequence(aff)      # backward or forward  matching?
#           print 'aff=' , aff

            c = aff[0]                    # get first char to compare with
            aff = aff[1:]

            if not ellyChar.isLetter(c):  # affix starts with letter?
                nerr += 1
                print >> sys.stderr , "** affix error: must start with letter"
                print >> sys.stderr , "*  at: [" , line , "]"
                continue                  # ignore line

            if not c in self.indx:        # node not already in tree index?
                self.indx[c] = Node()     # add new node

            node = self.indx[c]

            for a in aff:                 # now check each successive char in affix
                if a in node.contn:
                    node = node.contn[a]  # go to existing node if found
                else:
                    new = Node()          # otherwise make new node
                    node.contn[a] = new   # and insert into tree
                    node = new            # and move down

            # at final node in tree logic

            node.condn = int(elem.pop(0)) # condition for match

            try:
                nsave = 0 if len(elem) == 0 else int(elem.pop())
            except ValueError , e:
                print >> sys.stderr , e
                print >> sys.stderr , "*  at: [" , line , "]"
                continue                  # ignore line

            resto = [ Add ]               # set to defaults
            recur = False                 #

            mode  = do[-1]                # kind of recursion
            rest  = do[:-1]               # added chars to fill out root
#           print 'mode=' + '<' + mode + '>' , 'rest=' , rest
            if mode == u'?':
                node.condn = 1
                resto = [ Fail ]          # will generate fatal error
            else:
                if mode == ',':           # allow recursion?
                    recur = True          # if so, change default
                if len(rest) == 1 and rest[0] == '&':
                    resto = [ RestorE ]
                else:
                    resto += list(rest)

            if self.addn != None:
                resto.insert(1,self.addn) # insert AFTER first char of list
#           print 'resto=' , resto

            # insert action

            node.actns = Action(self,nsave,resto,recur,modf)
            node.tag()

#           if modf != '': print node , node.actns

        if nerr > 0:
            print >> sys.stderr , "**" , nerr , "affix errors in all"
            raise ellyException.TableFailure

#
# unit test
#

s = [ ]                     # traversal stack

def dumpLT ( dic ):
    """ recursive tree logic dump
    """

    for d in dic:           # look at all subtrees
        s.append(d)         # add to node chain for current path

        node = dic[d]       # current node

        if node.actns != None:
            fs = '{0:12s}'.format('>'.join(s))
            print '@ ' + fs , node , node.actns

        ndic = node.contn   # its continuations
        if len(ndic) > 0:   # if non-empty,
            dumpLT(ndic)    # continue down in tree
        else:               # otherwise,
            print "____"    # show node is leaf

        s.pop()

if __name__ == '__main__':

    import ellyDefinitionReader

    print 'testing tree logic generation only'

    indta = [                   # nonsense logic for testing
        'xyz 3 2 ab. 1' ,
        'wxyz 2 1 abc.' ,
        'rst 2 0 &.'    ,
        'lmno 0 0 .'    ,
        'wx 1 1 k,'     ,
        '|wxe 0 0 .'    ,
        'def 2 0 . 1x'  ,
        'ef 1 0 ,'
    ]

    class TL(TreeLogic):        # have to override dummy methods
        """ subclass to override sequence()
        """
        def __init__ ( self , inp):
            """ initialize
            """
            super(TL,self).__init__(inp)
        def sequence ( self , x ):
            """ reverse a sequence
            """
            return x[::-1]

    rdr = ellyDefinitionReader.EllyDefinitionReader(indta)
    tre = TL(rdr)               # create tree with nonsense logic

    n1 = Node()                 # put something in tree to test the unit test itself
    n1.id = 10001
    n2 = Node()
    n2.id = 10002
    n3 = Node()
    n3.id = 10003
    n4 = Node()
    n4.id = 10004
    tre.indx[u'A'] = n1         # note that real tree will have only lowercase!
    n1.contn[u'B'] = n2
    n2.contn[u'C'] = n3
    n2.contn[u'D'] = n4
    n3.actns = 'Act: -- 3'      # fake actions
    n4.actns = 'Act: -- 4'      #

    topdic = tre.indx

    print 'index dump'
    for cx in topdic:
        print cx + ' : ' + str(topdic[cx])

    print "tree dump"
    dumpLT(topdic)
