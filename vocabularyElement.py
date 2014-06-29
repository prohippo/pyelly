#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# vocabularyElement.py : 27jun2014 CPM
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
vocabulary element from external BdB table lookup
"""

import ellyBits
import ellyDefinitionReader
import generativeProcedure
import generativeDefiner
import unicodedata
import sys

gens = [ '*' ]      # define generative procedure for translation
geno = [ 'obtain' ] # default generative procedure

input = ellyDefinitionReader.EllyDefinitionReader(geno)
obtnp = generativeProcedure.GenerativeProcedure(None,input)

class VocabularyElement(object):

    """
    vocabulary term plus definition

    attributes:
        chs   - list of chars in term
        cat   - syntactic category
        syf   - syntactic flags
        smf   - semantic  flags
        bia   - initial plausibility score
        con   - associated concept
        gen   - generative procedure

        _nt   - number of translations
        _ln   - total char length of term
    """

    def __init__ ( self , tup ):

        """
        initialization of vocabulary object from BdB record

        arguments:
            self  -
            tup   - what BdB cursor get() returns
        """

        rec = tup[1].decode('utf8')      # what BdB found for search key
#       print >> sys.stderr , 'voc rec=' , rec
        r = rec.split(':')               # split off term in BdB results
        if len(r) <= 1: return           # the ':' is mandatory
        d = r[1].strip().split(' ')      # definition is right of ':'
#       print >> sys.stderr , 'VEntry: define as' , d
        if len(d) <  4: return           # it should have at least 4 parts
        ur = r[0].strip()                # term left of ':'
        self.chs = list(ur)              # save it
        self.cat = int(d.pop(0))         # syntactic category
#       print >> sys.stderr , '    full term=' , u''.join(self.chs)
        sy = d.pop(0)
        nb = len(sy)*4
        self.syf = ellyBits.EllyBits(nb) # allocate bits
        self.syf.reinit(sy)              # set syntactic features
        sm = d.pop(0)
        nb = len(sm)*4
        self.smf = ellyBits.EllyBits(nb) # allocate bits
        self.smf.reinit(sm)              # set semantic  features
        self.bia = int(d.pop(0))         # save initial plausibility
        if len(d) > 0:                   # any concept?
            self.con = d.pop(0)          # if so, save it
        else:
            self.con = '-'

#       print >> sys.stderr , '    translation=' , d

        if len(d) == 0:        # no further definition?
            self.gen = obtnp   # if so, then use default procedure
            self._nt = 0       #   i.e. no translation
        elif d[0][0] == '=':   # simple translation?
            pls = [ 'append ' + d[0][1:].strip() ]
            input = ellyDefinitionReader.EllyDefinitionReader(pls)
            self.gen = generativeProcedure.GenerativeProcedure(None,input)
            self._nt = 1
        elif d[0][0] == '(':   # get predefined procedure
            input = ellyDefinitionReader.EllyDefinitionReader([ d[0] ])
            self.gen = generativeProcedure.GenerativeProcedure(None,input)
            self._nt = 0
        else:                  # otherwise, set for selection of translation
            cm = 'pick LANG (' # construct instruction to select
            for p in d:
                cm += p + '#'  # build selection clauses
            cm += ')'
            gens[0] = cm       # replace action
#           print 'gens=' , gens
            input = ellyDefinitionReader.EllyDefinitionReader(gens)
            self.gen = generativeProcedure.GenerativeProcedure(None,input)
#           print 'vocabulary gen.logic'
#           generativeDefiner.showCode(self.gen.logic)
            self._nt = len(d)

        self._ln = len(self.chs)

    def __unicode__ ( self ):

        """
        Unicode string representation

        arguments:
            self

        returns:
            representation of vocabulary element on success, None otherwise
        """

        tm = u''.join(self.chs)

        df  = u'cat=' + unicode(self.cat) + u' '
        df += self.syf.hexadecimal() + u' ' + self.smf.hexadecimal() + u' '
        df += u'plaus=' + unicode(self.bia) + u' , '
        df += u'concp=' + self.con
        df += unicode(self._nt) + u' TRANSLATION'
        if self._nt != 1: df += u's'

#       print 'df=' , df

        return u'[' + tm + u'] ' + df

    def __str__ ( self ):

        """
        ASCII string representation

        arguments:
            self

        returns:
            representation of vocabulary element on success, None otherwise
        """

        return unicodedata.normalize('NFKD',unicode(self)).encode('ascii','ignore')

    def length ( self ):

        """
        get total length of any match

        arguments:
            self

        returns:
            char count
        """

        return self._ln
