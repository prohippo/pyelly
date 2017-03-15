#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyConfiguration.py : 08mar2017 CPM
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
define how to set up PyElly tables and processing
"""

import digraphEN

language = 'EN'               # English input expected
digraph = digraphEN.digrs     # English digraphs (set this to [ ] for none)

baseSource = './'             # get EllyBase language definitions from here
stemSource = './'             # get Elly stem logic from here

defaultSystem = 'default'     # where to get language definition, if unspecified

inflectionalStemming  = True  # whether to do inflectional stemming
morphologicalStemming = True  # whether to do morphological stemming

treeDisplay = True            # display parse tree?
longDisplay = False           # display all phrase nodes?
fullDump    = False           # display all tokens on failure?
inputEcho   = True            # echo input in showing output?

import extractionProcedure    # definition of procedures to extract entities

rewriteNumbers = True         # enable automatic rewriting of number expressions

extractors = [                # what entity extraction procedures to use
    [ extractionProcedure.date    , 'date' , '-'     ] ,
    [ extractionProcedure.time    , 'time' , '-' , 1 ] ,
    [ extractionProcedure.acronym , 'acro' , '-' , 1 ]
]

noteIndentation = True        # for reformatting free text

phraseLimit = 50000           # nominal limit for single sentence
