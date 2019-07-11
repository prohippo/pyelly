#!/usr/bin/python
# PyElly - tool for testing stemmers
#
# stemTest.py : 01nov2014 CPM
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
shared unit test code for Elly stemming modules
"""

import sys
import ellyToken
import ellyException

def stemTest( stemmer , suffix=None ):

    """
    test stemmer with examples from standard input

    arguments:
        stemmer - must be of class with apply(x) method
        suffix  - suffix to report in output
    """

    out = ''

    print "testing ", stemmer
    if suffix != None:
        out = '[-' + suffix + ']'
        print 'suffix' , out
    print "enter words to stem:"

    while True:
        try:
            print "> ",
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            break

        w = line.rstrip()
        if len(w) == 0: break            # stop upon empty line for EOF
        print '"%s"' % w ,               #
        tok = ellyToken.EllyToken(w)     # make new token
        try:
            sta = stemmer.apply(tok)     # apply stemmer
        except ellyException.StemmingError:
            print >> sys.stderr , 'stemming error!'
            sys.exit(1)
        print "-->>", ''.join(tok.root), # stemming result
        if suffix == None:
            print tok.getSuffixes() ,    # list of suffixes removed
        else:
            print out ,
        print " success code= ", sta
