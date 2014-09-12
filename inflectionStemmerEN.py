#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# inflectionStemmerEN.py : 10sep2014 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2012, Clinton Prentiss Mah
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

import stemLogic
import ellyToken
import ellyException
from ellyStemmer import *

"""
English inflectional stemmer
"""

class InflectionStemmerEN(EllyStemmer):

    """
    general English inflectional stemmer

    attributes:
        sLog  - -S   logic
        dLog  - -ED  logic
        gLog  - -ING logic
        rLog  - root restoration logic
        pLog  - special case check logic
        uLog  - undoubling final consonant logic
    """

    sTb = "Stbl.sl"     # table files to load if logic not defined for constructor
    dTb = "EDtbl.sl"    #
    gTb = "INGtbl.sl"   #
    rTb = "rest-tbl.sl" #
    pTb = "spec-tbl.sl" #
    uTb = "undb-tbl.sl" #

    def __init__ ( self , sLog=None , dLog=None , gLog=None , rLog=None , pLog=None , uLog=None ):

        """
        set up stemming logic blocks for English inflections

        arguments:
            self  -
            sLog  - -S   logic
            dLog  - -ED  logic
            gLog  - -ING logic
            rLog  - root restoration logic
            pLog  - special case check logic
            uLog  - undoubling final consonant logic

        exceptions:
            TableFailure on error
        """

        try:
            if sLog != None: self.sLog = sLog
            else: self.sLog = stemLogic.StemLogic(InflectionStemmerEN.sTb)
            if dLog != None: self.dLog = dLog
            else: self.dLog = stemLogic.StemLogic(InflectionStemmerEN.dTb)
            if gLog != None: self.gLog = gLog
            else: self.gLog = stemLogic.StemLogic(InflectionStemmerEN.gTb)

            if rLog != None: self.rLog = rLog
            else: self.rLog = stemLogic.StemLogic(InflectionStemmerEN.rTb)
            if pLog != None: self.pLog = pLog
            else: self.pLog = stemLogic.StemLogic(InflectionStemmerEN.pTb)
            if uLog != None: self.uLog = uLog
            else: self.uLog = stemLogic.StemLogic(InflectionStemmerEN.uTb)
        except ellyException.FormatFailure:
            print >> sys.stderr , 'bad inflectional stemming'
            raise ellyException.TableFailure

    def applyLogic ( self , logic , token ):

        """
        apply specified stemming logic for suffix plus restoration logic

        arguments:
            self  -
            logic - suffix logic to apply
            token - what to apply it on
        returns:
            boolean success flag
        """

#       print "try", logic.table[0]

        stax = logic.apply(token)
        if stax == stemLogic.doMORE:
            self.applyRest(token)
        elif stax != stemLogic.isMTCH:
            return False

        if logic.table[0] != "":
            token.addSuffix(logic.table[0][::-1]) # store unreversed suffix
        return True

    def applyRest ( self , token ):

        """
        apply root restoration logic

        arguments:
            self  -
            token - what to apply logic on
        returns:
            True just for consistency
        """

#       print 'applyRest to' , token
        if self.rLog.apply(token) == stemLogic.doMORE:
            w = token.getRoot()
            if w[-1] == w[-2]:
#               print 'double consonant' , w[-1]
                w.pop()
                self.uLog.apply(token,w[-1]) 
            else:
                self.pLog.apply(token)
        return True


    def apply ( self , token ):

        """
        remove English inflectional endings

        arguments:
            self  -
            token - input token to process

        returns:
            boolean success flag
        """

        sts = self.applyLogic(self.sLog,token)       # first try to remove -S
        stg = self.applyLogic(self.gLog,token)       # then try to remove -ING
        std = False
        if not sts and not stg:
            std = self.applyLogic(self.dLog,token)   # try to remove -ED only if no -S or -ING
                                                     # already removed
        return sts or std or stg

    def simplify ( self , strg ):

        """
        apply inflectional stemming to string

        arguments:
           self  -
           strg  - input Unicode string

        returns:
           stemmed Unicode string
        """

        if len(strg) < 4: return strg
        if strg[-1] == "s" and strg[-2] == "'":
            return strg[:-2]
        else:
            t = ellyToken.EllyToken(strg)
            self.apply(t)
            return t.toUnicode()

if __name__ == "__main__": # for unit testing

    import stemTest

    try:
        stemmer = InflectionStemmerEN()
    except ellyException.TableFailure:
        print >> sys.stderr , 'cannot initialize stemmer'
        sys.exit(1)

#   print stemmer.sLog
#   print stemmer.dLog
#   print stemmer.gLog
#   print stemmer.rLog
#   print stemmer.pLog
#   print stemmer.uLog

    stemTest.stemTest(stemmer)
