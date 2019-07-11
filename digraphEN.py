#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# digraphEN.py : 10mar2015 CPM
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
common alphabetic digraphs in the 900 most frequent male and 1000 most frequent female
given names collected by the U.S. Census in 2010.

for other languages, define separate files like digraphFR.py or digraphDE.py; the total
number of digraphs does not matter as long as they are fairly extensive

there is no excutable logic in this sourc file!
"""

digrs = [
    'ab','ac','ad','ae','ag','ah','ai','ak','al','am','an','ap','ar','as','at','au','av',
    'aw','ax','ay','ba','bb','be','bi','bl','bo','br','bu','by','ca','ce','ch','ci','ck',
    'cl','co','cq','cr','ct','cu','cy','da','dd','de','dg','di','dn','do','dr','ds','du',
    'dw','dy','ea','eb','ec','ed','ee','ef','eg','ei','ek','el','em','en','eo','ep','er',
    'es','et','eu','ev','ew','ex','ey','fa','fe','ff','fi','fl','fo','fr','ga','ge','gg',
    'gh','gi','gl','go','gr','gu','ha','he','hi','hl','hn','ho','hr','hu','hy','ia','ic',
    'id','ie','if','ig','ik','il','im','in','io','ip','iq','ir','is','it','iu','iv','iz',
    'ja','je','ji','jo','ju','ka','ke','ki','kr','ky','la','lb','ld','le','lf','li','ll',
    'lm','lo','lp','ls','lt','lu','lv','ly','ma','mb','me','mi','mm','mo','mu','my','na',
    'nc','nd','ne','ng','ni','nk','nn','no','nr','ns','nt','nu','ny','nz','oa','ob','oc',
    'od','oe','of','og','oh','oi','ok','ol','om','on','oo','op','or','os','ot','ou','ov',
    'ow','oy','pa','pe','ph','pr','qu','ra','rb','rc','rd','re','rg','rh','ri','rk','rl',
    'rm','rn','ro','rr','rs','rt','ru','rv','rw','ry','sa','sc','se','sh','si','sl','sm',
    'so','sp','ss','st','su','sy','ta','tc','te','th','ti','tl','tn','to','tr','tt','tu',
    'ty','ua','ub','uc','ud','ue','ug','ui','ul','um','un','up','ur','us','ut','uz','va',
    've','vi','vo','wa','we','wi','wn','wo','xa','xi','ya','yc','yd','ye','yl','ym','yn',
    'yo','yr','ys','za','ze'
]
