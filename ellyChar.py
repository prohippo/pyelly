#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PyElly - scripting tool for analyzing natural language
#
# ellyChar.py : 24jun2017 CPM
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
for handing ASCII plus Latin-1 chars as Unicode
"""

DOT = u'.'         # Unicode period
COM = u','         # Unicode comma
COL = u':'         # Unicode colon
AST = u'*'         # Unicode asterix
APO = unichr(39)   # Unicode apostrophe
APX = u'\u2019'    # Unicode formatted apostrophe
USC = u'_'         # Unicode underscore
LBR = u'['         # Unicode left bracket
RBR = u']'         # Unicode right bracket
SLA = u'/'         # Unicode slash
BSL = u'\\'        # Unicode backslash
SPC = u' '         # Unicode space
AMP = u'&'         # Unicode ampersand
NBS = u'\u00A0'    # Unicode no-break space
TAB = u'\u0009'    # ASCII horizontal tab
RS  = u'\u001E'    # ASCII record separator with special significance for parsing

LSQm = u'\u2018'   # left  single quote
RSQm = u'\u2019'   # right single quote (same as APX)
LDQm = u'\u201C'   # left  double quote
RDQm = u'\u201D'   # right double quote
PRME = u'\u2032'   # prime
ELLP = u'\u2026'   # horizontal ellipsis

Apd = [ u'*' , u'+' , u'-' ]                                    # marks appending to token

Pnc = [ u'“' , u'”' , u'‘' , u'’' , u'–' , u'—' , u'…' , u'™' ] # special punctuation

Opn = [ u'“' , u'‘' , u'"' , u"'" , u'[' , u'(' ]
Cls = [ u'”' , u'’' , u'"' , u"'" , u']' , u')' ]

Grk = [            # small Greek letters, not treated as alphabetic
    u'α',u'β',u'γ',u'δ',u'ε',u'ζ',u'η',u'θ',
    u'ι',u'κ',u'λ',u'μ',u'ν',u'ξ',u'ο',u'π',
    u'ρ',u'σ',u'τ',u'υ',u'φ',u'χ',u'ψ',u'ω'
]

Lim = u'\u01D5'    # main limit of Unicode chars recognized

LaS = 0x0100       # start of Latin supplement
LaT = 0x0120       # end of supplement control chars

######## The full alphabet currently defined for PyElly is ASCII plus Latin-1
######## Supplement and Latin Extended A plus parts of Latin Extended B. These
######## are in the first four blocks of Unicode as follows:

##00  . . . . . . . . . . . . . . . .     . . . . . . . . . . . . . . . .
##20    ! " # $ % & ' ( ) * + , - . /     0 1 2 3 4 5 6 7 8 9 : ; < = > ?
##40  @ A B C D E F G H I J K L M N O     P Q R S T U V W X Y Z [ \ ] ^ _
##60  ` a b c d e f g h i j k l m n o     p q r s t u v w x y z { | } ~

##00  . . . . . . . . . . . . . . . .     . . . . . . . . . . . . . . . .
##20    ¡ ¢ £ ¤ ¥ ¦ § ¨ © ª « ¬   ® ¯     ° ± ² ³ ´ µ ¶ · ¸ ¹ º » ¼ ½ ¾ ¿
##40  À Á Â Ã Ä Å Æ Ç È É Ê Ë Ì Í Î Ï     Ð Ñ Ò Ó Ô Õ Ö × Ø Ù Ú Û Ü Ý Þ ß
##60  à á â ã ä å æ ç è é ê ë ì í î ï     ð ñ ò ó ô õ ö ÷ ø ù ú û ü ý þ ÿ

##00  Ā ā Ă ă Ą ą Ć ć Ĉ ĉ Ċ ċ Č č Ď ď     Đ đ Ē ē Ĕ ĕ Ė ė Ę ę Ě ě Ĝ ĝ Ğ ğ
##20  Ġ ġ Ģ ģ Ĥ ĥ Ħ ħ Ĩ ĩ Ī ī Ĭ ĭ Į į     İ ı Ĳ ĳ Ĵ ĵ Ķ ķ ĸ Ĺ ĺ Ļ ļ Ľ ľ Ŀ
##40  ŀ Ł ł Ń ń Ņ ņ Ň ň ŉ Ŋ ŋ Ō ō Ŏ ŏ     Ő ő Œ œ Ŕ ŕ Ŗ ŗ Ř ř Ś ś Ŝ ŝ Ş ş
##60  Š š Ţ ţ Ť ť Ŧ ŧ Ũ ũ Ū ū Ŭ ŭ Ů ů     Ű ű Ų ų Ŵ ŵ Ŷ ŷ Ÿ Ź ź Ż ż Ž ž ſ

##00  . . . . . . . . . . . . . . . .     . . . . . . . . . . . . . . . .
##20  . . . . . . . . . . . . . . . .     . . . . . . . . . . . . . . . .
##40  . . . . . . . . . . . . . Ǎ ǎ Ǐ     ǐ Ǒ ǒ Ǔ ǔ

def isStrongConsonant ( x ):
    """
    test whether char is consonant, not including Y

    arguments:
        x - the char
    returns:
        True if non-Y consonant, False otherwise
    """
    if not isConsonant(x) or x == u'Y' or x == u'y':
        return False
    else:
        return True

def isConsonant ( x ):
    """
    test whether char is consonant, including Y

    arguments:
        x - the char
    returns:
        True if consonant, False otherwise
    """
    if not isLetter(x) or isVowel(x):
        return False
    else:
        return True

## ASCII plus Latin-1 vowels

T = True
F = False

Vowel = [
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,T,F,F,F,T,F,F,F,T,F,F,F,F,F,T, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,T,F,F,F,T,F,F,F,T,F,F,F,F,F,T, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,

    F,F,F,F,F,F,F,F,F,F,F,F,T,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,T,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    T,T,T,T,T,T,T,F,T,T,T,T,T,T,T,T, F,F,T,T,T,T,T,F,T,T,T,T,T,T,F,T,
    T,T,T,T,T,T,T,F,T,T,T,T,T,T,T,T, F,F,T,T,T,T,T,F,T,T,T,T,T,F,F,F,

    T,T,T,T,T,T,F,F,F,F,F,F,F,F,F,F, F,F,T,T,T,T,T,T,T,T,T,T,F,F,F,F,
    F,F,F,F,F,F,F,F,T,T,T,T,T,T,T,T, T,T,T,T,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,T,T,T,T, T,T,T,T,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,

    F,F,F,F,F,F,T,T,F,F,F,F,F,F,T,T, T,F,F,F,F,F,T,T,F,F,F,F,F,F,F,T,
    T,T,T,T,F,F,F,F,F,F,F,F,F,F,F,T, T,T,T,T,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,T,T,T, T,T,T,T,T
]

Uindex = ord('u') - ord('a') + 1

def isStrictVowel ( x ):
    """
    test whether char is vowel, not including U

    arguments:
        x - the char
    returns:
        True if non-U vowel, False otherwise
    """
    return x < Lim and Vowel[ord(x)]

def isVowel ( x ):
    """
    test whether char is lowercase vowel, including U

    arguments:
        x - the char
    returns:
        True if vowel, False otherwise
    """
    return isStrictVowel(x) or toIndex(x) == Uindex

## chars allowed in tokens

def isCombining ( x ):
    """
    test whether char can be in multi-char token

    arguments:
        x - the char
    returns:
        True if a most general token char, False otherwise
    """
    return isLetterOrDigit(x) or x in [ USC , APO , APX , SLA , BSL , NBS ]

def isEmbeddedCombining ( x ):
    """
    test whether punctuation char can be embedded in token

    arguments:
        x - the char
    returns:
        True if char can be in the middle of a token, False otherwise
    """
    return x in [ DOT , COM , COL , APO , APX , AST , AMP , SLA ]

def isPureCombining ( x ):
    """
    test whether char is token char, not punctuation nor apostrophe

    arguments:
        x - the char
    returns:
        True if strictest kind of token char, False otherwise
    """
    return isLetterOrDigit(x) or x == USC or x == NBS

def isSpace ( x ):
    """
    tests whether char is space

    arguments:
        x - the char
    returns:
        True if strictest kind of token char, False otherwise
    """
    return x in [ SPC , NBS , USC , TAB ]

## for replacing standard library char typing and case conversion

Letter = [
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,F,F,F,F,F,
    F,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,F,F,F,F,F,

    F,F,F,F,F,F,F,F,F,F,T,F,T,F,T,F, F,F,F,F,F,F,F,F,F,F,F,F,T,F,T,T,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,F,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,F,T,T,T,T,T,T,T,T,

    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,

    T,T,T,T,F,F,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,F,F,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,F,F,F,F,
    F,F,F,F,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T
]

LetterOrDigit = [
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, T,T,T,T,T,T,T,T,T,T,F,F,F,F,F,F,
    F,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,F,F,F,F,F,
    F,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,F,F,F,F,F,

    F,F,F,F,F,F,F,F,F,F,T,F,T,F,T,F, F,F,F,F,F,F,F,F,F,F,F,F,T,F,T,T,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,F,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,F,T,T,T,T,T,T,T,T,

    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,

    T,T,T,T,F,F,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,
    T,T,T,T,T,T,T,F,F,T,T,T,T,T,T,T, T,T,T,T,T,T,T,T,T,T,T,T,F,F,F,F,
    F,F,F,F,T,T,T,T,T,T,T,T,T,T,T,T, T,T,T,T,T
]

def isLetterOrDigit ( x ):
    """
    check for ASCII or Latin-1 letter or digit

    arguments:
        x - the char
    returns:
        True if letter or digit, False otherwise
    """
    return x != '' and x < Lim and LetterOrDigit[ord(x)]

def isNotLetterOrDigit ( x ):
    """
    check for nonalphanumeric

    arguments:
        x - the char
    returns:
        True if not letter or digit, False otherwise
    """
    return not isLetterOrDigit(x)

def isLetter ( x ):
    """
    check for ASCII or Latin-1 letter

    arguments:
        x - the char
    returns:
        True if letter, False otherwise
    """
    return x != '' and x < Lim and Letter[ord(x)]

def isDigit ( x ):
    """
    check for ASCII or Latin-1 digit

    arguments:
        x - the char
    returns:
        True if digit, False otherwise
    """
    return x <= '9' and x >= '0'

Space = [
    T,F,F,F,F,F,F,F,F,T,T,T,T,T,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    T,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,

    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,

    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,

    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F, F,F,F,F,F
]

def isWhiteSpace ( x ):
    """
    check for white space (but NOT no-break space)

    arguments:
        x - the char
    returns:
        True if Unicode space, False otherwise
    """
    return x != '' and x != None and x < Lim and Space[ord(x)]

def isApostrophe ( x ):
    """
    check for variations of apostrophes

    arguments:
        x - the char
    returns:
        True if apostrophe space, False otherwise
    """
    return x == APO or x == APX or x == PRME

## for equating PyElly Unicode with 26 ASCII letters when indexing

Mapping = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   27,28,29,30,31,32,33,34,35,36, 0, 0, 0, 0, 0, 0,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,
   16,17,18,19,20,21,22,23,24,25,26, 0, 0, 0, 0, 0,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,
   16,17,18,19,20,21,22,23,24,25,26, 0, 0, 0, 0, 0,

    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,19, 0,15, 0,26, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,19, 0,15, 0,26,25,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 3, 5, 5, 5, 5, 9, 9, 9, 9,
   20,14,15,15,15,15,15, 0,15,21,21,21,21,25,20,19,
    1, 1, 1, 1, 1, 1, 1, 3, 5, 5, 5, 5, 9, 9, 9, 9,
   20,14,15,15,15,15,15, 0,15,21,21,21,21,25,20,25,

    1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4,
    4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7,
    7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9,
    9, 9, 9, 9,10,10,11,11,11,12,12,12,12,12,12,12,
   12,12,12,14,14,14,14,14,14,14,14,14,15,15,15,15,
   15,15, 1, 1,18,18,18,18,18,18,19,19,19,19,19,19,
   19,19,20,20,20,20,20,20,21,21,21,21,21,21,21,21,
   21,21,21,21,23,23,25,25,25,26,26,26,26,26,26,19,

    2, 2, 2, 2, 0, 0,15,15, 3, 4, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 7, 7, 8, 9, 9,11,11,12,12,13,14,14,15,
   15,15,15,15,16,16,18, 0, 0,19,19,20,20,20,20,21,
   21,21,22,25,25,26,26,26,26,26,26,20, 0, 0, 0, 0,
    0, 0, 0, 0,10,10,10,12,12,12,14,14,14, 1, 1, 9,
    9,15,15,21,21
]

## letters for codes

Unmapping = " abcdefghijklmnopqrstuvwxyz01234356789"  # ASCII string!

Max  = 0       # maximum mapping defined (=pure alphabetic count)

for m in Mapping:
    if Max < m: Max = m

DigB = Max + 1 # starting index for digits after alphabetic

def toIndex ( x ):
    """
    map alphanumic Unicode Latin-1 to equivalent ASCII for indexing

    arguments:
        x - the char
    returns:
        index value for char
    """
    if u'0' <= x <= u'9':
        return ord(x) - ord('0') + DigB
    elif isLetter(x):
        return Mapping[ord(x)]
    else:
        return 0

def toChar ( k ):
    """
    unmap index value to base ASCII letter or digit

    arguments:
        k - numerical index
    returns:
        letter represented by index
    """

    if k > Max + 10 or k <= 0:
        return '-'
    elif k > Max:
        return unichr(ord('0') + k - DigB)
    else:
        return Unmapping[k]

Lower = [
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,     F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,     F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,     F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,     T,T,T,T,T,T,T,T,T,T,T,F,F,F,F,F,

    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,     F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,     F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,
    F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,     F,F,F,F,F,F,F,F,F,F,F,F,F,F,F,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,     T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,

    F,T,F,T,F,T,F,T,F,T,F,T,F,T,F,T,     F,T,F,T,F,T,F,T,F,T,F,T,F,T,F,T,
    F,T,F,T,F,T,F,T,F,T,F,T,F,T,F,T,     F,T,F,T,F,T,F,T,T,F,T,F,T,F,T,F,
    T,F,T,F,T,F,T,F,T,T,F,T,F,T,F,T,     F,T,F,T,F,T,F,T,F,T,F,T,F,T,F,T,
    F,T,F,T,F,T,F,T,F,T,F,T,F,T,F,T,     F,T,F,T,F,T,F,T,F,F,T,F,T,F,T,T,

    T,F,F,T,F,F,F,F,F,T,F,F,F,F,F,F,     F,F,T,F,F,F,F,F,F,T,F,F,F,F,F,F,
    F,T,F,T,F,T,F,F,F,F,F,F,F,F,F,F,     T,F,F,F,T,F,T,F,F,T,F,F,F,F,F,F,
    T,T,F,F,F,F,T,F,F,T,F,F,T,F,T,F,     T,F,T,F,T
]

def toLowerCaseListASCII ( ls , num=True ):
    """
    convert a list of chars to lowercase ASCII alphanumeric or alphabetic
    depending on num argument

    arguments:
        ls  - a Unicode list
        num - True is alphanumeric, otherwise alphabetic only
    """

    if len(ls) == 0: return

    ll = len(ls)
    for i in range(ll):
        c = ls[i]
        if c >= Lim:
            c = '_'
        elif not isLetterOrDigit(c):
            c = '.'
        elif not num and isDigit(c):
            c = '_'
        else:
            c = Unmapping[Mapping[ord(c)]]
        ls[i] = c

def isLowerCaseLetter ( x ):
    """
    check for no capitalization

    arguments:
        x - the char
    returns:
        True if lower case letter, False otherwise
    """
#   print 'x=' , x
    return x != '' and x < Lim and Lower[ord(x)]

def isUpperCaseLetter ( x ):
    """
    check for capitalization

    arguments:
        x - the char
    returns:
        True if lower case letter, False otherwise
    """
    no = ord(x) if x != '' and x < Lim else 0
    return Letter[no] and not Lower[no]

def isText ( x ):
    """
    check for ASCII text or Latin-1 or special punctuation

    arguments:
        x - the char
    returns:
        True if ASCII or Latin or punctuation , False otherwise
    """
    if x == '' or isPureControl(x):
        return False
    else:
        return x < Lim or x in Pnc or x in Grk

control = [
    T,T,T,T,T,T,T,T,T,F,F,T,T,F,T,T,
    T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T
]

def isPureControl ( x ):
    """
    identify ASCII non-text control char

    arguments:
        x - the char
    returns:
        True if non-text control, False otherwise
    """
    if ord(x) < LaS:
        return x < SPC and control[ord(x)]
    else:
        return x < LaT

termina = [ COL , COM ]

def findBreak ( text , offset=0 , nspace=0 ):

    """
    look for next break in text from given offset

    arguments:
        text   - what to scan
        offset - starting offset
        nspace - how many spaces can be non-breaking
    returns:
        remaining char count in text if no break is found
        otherwise, count of chars to next break if nonzero, but 1 if zero,
    """

    k = offset
    n = len(text)
#   print 'find break k=' , k , 'n=' ,n
    while k < n:
        x = text[k]                                # iterate on next chars in input
#       print 'char=' , x , '@' , k
        if not isPureCombining(x):                 # check if not ordinary token char
#           print 'special checking needed'
            if x == '-' or isEmbeddedCombining(x): # check if embeddable punctuation
                if k + 1 < n:
                    c = text[k+1]                  # look at next char in input
#                   print 'next char=' , c
                    if isApostrophe(c) or isLetterOrDigit(c) or c == AMP or c == '-':
                        k += 2
                        continue
                    if isSpace(c):                 # if next char is space, is it expected?
#                       print 'is space, nspace=' , nspace
                        if nspace > 0:
                            k += 2                 # allow for space in token
                            nspace -= 1
                            continue
                        elif not x in termina:     # look for a token break
#                           print 'non breaking' , x
                            k += 1                 # if none, continue scan
                            break
                elif not x in termina:             # the above code must be repeated
#                   print 'non breaking' , x       # since the elif code is paired
                    k += 1                         # with a different if
                    break
            elif k == offset and x in Opn:
#               print 'look for short bracketed segment'
                j  = k + 1
                jl = k + 4
                if jl > n: jl = n
#               print 'j=' , j , 'jl=' , jl
#               print 'input=' , text[k:]
                while j < jl:
                    if text[j] in Cls: break
                    j += 1
#               print 'j=' , j , 'jl=' , jl
                if j < jl:
#                   print 'segment found'
                    k = j
                k += 1
                break

#           print 'space check, nspace=' , nspace
            if nspace > 0 and isSpace(x):
                k += 1
                nspace -= 1
                continue
            if k == offset:
                k += 1      # if immediate break, take 1 char anyway
            break
        elif x in Pnc:
#           print 'punctuation break'
            break
        k += 1
#   print 'break=' , k , 'offset=' , offset
    return k - offset

############################ special CJK  ############################

def isCJK ( x ):

    """
    check for CJK Unicode - only the 20,950 most common characters!

    arguments:
        x   - char to check
    returns:
        True if CJK, otherwise False
    """

    xo = ord(x)
    return 0xA000 > xo and xo >= 0x4E00

############################ unit testing ############################

if __name__ == "__main__":

    chr1 = u"pqrstuvwxyz{|}~."
    chr2 = u"ðñòóôõö÷øùúûüýþÿ"
    chr3 = u"ŰűŲųŴŵŶŷŸŹźŻżŽžſ"
    chr4 = u"ǀǁǂǃǄǅǆǇǈǉǊǋǌǍǎǏǐǑǒǓǔ"
    chr5 = u"ßÿĸŉŸſ"
    chr6 = u"αβγδεζ"
    chrs = chr1 + chr2 + chr3 + chr4 + chr5 + chr6

    for cx in list(chrs):
        ko = ord(cx)
        mp = toChar(toIndex(cx))
        vo = 'vowel' if isVowel(cx) else ''
        cy = cx.lower()
        print u'<' + cx + cy + u'> ord=' , '{:3d}'.format(ko) , 'map=' , mp , vo

    print isCJK(u'寶')
    print isCJK(u'譽')
    print isCJK(u'禮')
