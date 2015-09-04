#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBits.py : 03sep2015 CPM
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
define bit operations on byte arrays required by Elly parsing
"""

import array

hxh = { '0':0 , '1':1 , '2':2 , '3':3 , '4':4 ,  # convert hex digit to integer
        '5':5 , '6':6 , '7':7 , '8':8 , '9':9 ,  #
        'A':10 , 'B':11 , 'C':12 ,               #
        'D':13 , 'E':14 , 'F':15                 #
      }

hxd = u'0123456789ABCDEF'  # for converting to hexadecimal

sel = [ 0200, 0100, 0040, 0020, 0010, 0004, 0002, 0001 ] # define bits in byte

N   = len(sel)                                           # bit-count in byte
nB  = 2                                                  # default byte count for bit string

def _com(x): return(255-x)  # hack to get complement of unsigned byte x
                            # should NOT have to do this!

def getByteCountFor ( nbc ):

    """
    set default byte count from bit count wanted

    arguments:
        nbc   - bit count wanted

    returns:
        number of bytes
    """

    n , m = divmod(nbc,N)
    if m > 0: n += 1
    return n

def join ( a , b ):

    """
    combine pair of EllyBits to compare against compound bits

    arguments:
        a   - EllyBits object
        b   - EllyBits object

    returns:
        merged array of bytes for comparison
    """

    return a.data + b.data

def check ( bs , ps ):

    """
    check for match of compounded bits with positive and negative bits

    arguments:
        bs  - compounded bits as btye array
        ps  - positive and negative pattern bits as btye array

    returns:
        True on match, False otherwise
    """

    n = len(bs)
    for i in range(n):
        if (bs[i] & ps[i]) != 0: return False
    return True

def show ( bs ):

    """
    convert join'ed bits into hexadecimal

    arguments:
        bs - bit string as array of bytes

    returns:
        hexadecimal representation
    """

    try:
        return ' '.join(map(lambda b: '{:02x}'.format(b),bs))
    except ValueError:
        return '--'

class EllyBits(object):

    """
    bit string as Python array of byte values

    attributes:
        data  - array for bits
    """

    def __init__ ( self , nob=nB*N ):
        """
        initialize
        arguments:
            self  -
            nob   - number of bits in string
        """
#       print 'nob=' , nob
        n = getByteCountFor(nob)
        self.data = array.array('B',(0,)*n)  # want unsigned char as array element = 'B'

    def __str__ ( self ):
        """
        represent bit data
        arguments:
            self
        returns:
            hexadecimal string for bits
        """
        return 'EllyBits: ' + show(self.data)

    def set ( self , k ):
        """
        set kth bit by OR'ing
        arguments:
            self  -
            k     - which bit
        """
        n , m = divmod(k,N)
        if n >= len(self.data): return
        self.data[n] |= sel[m]

    def test ( self , k ):
        """
        test kth bit
        arguments:
            self  -
            k     - which bit
        returns:
            True if kth bit == 1, False otherwise
        """
        n , m = divmod(k,N)
        if n >= len(self.data): return False
        return (self.data[n] & sel[m]) != 0

    def match ( self , r ):
        """
        compare bits with reference
        arguments:
            self  -
            r     - bit string to compare with
        returns:
            True if ON bits include all reference ON bits, False otherwise
        """
        m = len(self.data)
        n = len(r.data)
        if n > m: n = m
        for i in range(n):
            if _com(self.data[i]) & r.data[i] != 0: return False
        return True

    def equal ( self , r ):
        """
        check that bits are the same as reference
        arguments:
            self  -
            r     - bit string in byte array to compare with
        returns:
            True if all bits the same, False otherwise
        """
        for i in range(len(r.data)):
            if self.data[i] != r.data[i]: return False
        return True

    def intersect ( self , r ):
        """
        intersect bits with reference
        arguments:
            self  -
            r     - bit string in byte array to compare with
        returns:
            True if bits intersect, False otherwise
        """
        m = len(self.data)
        n = len(r.data)
        if n > m: n = m
        for i in range(n):
            if self.data[i] & r.data[i] != 0: return True
        return False

    def zeroed ( self ):
        """
        check if all bits zero
        arguments:
            self
        returns:
            True if all zero, False otherwise
        """
        for i in range(len(self.data)):
            if self.data[i] != 0: return False
        return True

    def clear ( self ):
        """
        reset all bits to zero
        arguments:
            self
        """
        for i in range(len(self.data)): self.data[i] = 0

    def complement ( self ):
        """
        set all bits to their complement
        arguments:
            self
        """
        for i in range(len(self.data)): self.data[i] = _com(self.data[i])

    def combine ( self , r ):
        """
        form disjunction with other bit string
        arguments:
            self  -
            r     - bit string in byte array to OR with
        """
        m = len(self.data)
        n = len(r.data)
        if n > m: n = m
        for i in range(n):
            self.data[i] |= r.data[i]  # disjunction

    def reset ( self , r ):
        """
        reset selected bits
        arguments:
            self  -
            r     - = 1 for bits to keep
        """
        m = len(self.data)
        n = len(r.data)
        if n > m: n = m
        for i in range(n):
            self.data[i] &= r.data[i]  # conjunction

    def compound ( self ):
        """
        build compound representation for positive and negative bit testing
        arguments:
            self
        returns:
            combination of complemented bits as byte array
        """
        cm = map(lambda x:_com(x),self.data)   # complement current bits
        return array.array('B',cm) + self.data # combine with uncomplemented

    def hexadecimal ( self , divide=True ):
        """
        convert bits to hexadecimal
        arguments:
            self   -
            divide - flag to split output into 2-char segments
        returns:
            hexadecimal string
        """
        bs = [ ]
        for b in self.data:
            n , m = divmod(b,16)
            bs.append(hxd[n])
            bs.append(hxd[m])
            if divide:
                bs.append(' ')
        return ''.join(bs).rstrip()

    def reinit ( self , hexb ):
        """
        reset bits to hexadecimal specification
        arguments:
            self  -
            hexb  - hexadecimal bit specification
        """
        ln = len(self.data)
        if len(hexb)//2 != ln: return
        for i in range(ln):
            bs = hexb[:2]
            hexb = hexb[2:]
            self.data[i] = 16*hxh[bs[0]] + hxh[bs[1]]

    def count ( self ):
        """
        get byte length of data
        arguments:
            self
        returns:
            integer coutn
        """
        return len(self.data)

#
# unit test
#

if __name__ == "__main__":

    K = 12  # nominal bit count to support in testing (should be > 8)

    bbs = EllyBits(K)
    bbs.set(0)
    bbs.set(6)
    bbs.set(11)

    print 'bbs=' , bbs

    print "bbs before:" , bbs.data , "hex=" , bbs.hexadecimal()
    bbt = EllyBits(K)
    bbt.set(9)
    print "bbt before:" , bbt.data , "hex=" , bbt.hexadecimal()
    bbs.combine(bbt)
    print "bbs combined with bbs:" , bbs.data , "hex=" , bbs.hexadecimal()

    print "test bit  9 of bbs" , bbs.test(9)
    print "test bit 10 of bbs" , bbs.test(10)
    print "test bit 11 of bbs" , bbs.test(11)

    cbs = bbs.compound()
    print "compound bbs=" , type(cbs) , show(cbs)
    pbs = EllyBits(K)
    nbs = EllyBits(K)
    pbs.set(6)
    nbs.set(7)
    print 'pbs=' , pbs.hexadecimal()
    print 'nbs=' , nbs.hexadecimal()
    tbs = join(pbs,nbs)
    print "join pbs, nbs=" , type(tbs) , show(tbs)

    print 'check compound versus join=' , check(cbs,tbs)

    print "current   bbs" , bbs.data , "hex=" , bbs.hexadecimal()
    bbs.complement()
    print "complemented " , bbs.data , "hex=" , bbs.hexadecimal()
    bbs.clear()
    print "cleared   bbs" , bbs.data , "hex=" , bbs.hexadecimal()

    pbs.set(7)
    print 'comparing x=' , pbs.hexadecimal() , 'and y=' , nbs.hexadecimal()
    print 'x equal y:' , pbs.equal(nbs)
    print 'x match y:' , pbs.match(nbs)
    print 'y match x:' , nbs.match(pbs)
    nbs.set(6)
    print 'z=' , nbs.hexadecimal()
    print 'x match z:' , pbs.equal(nbs)

    bbs.reinit('FFEE')
    print 'set bbs to FFEE'
    print "bbs:" , bbs.data , "hex=" , bbs.hexadecimal()

    bbs.reinit('FF12')
    print 'set bbs to FF12'
    print '=' , bbs.hexadecimal(False)
    print 'resetting with EEEE'
    rbs = EllyBits(K)
    rbs.reinit('EEEE')
    bbs.reset(rbs)
    print '=' , bbs.hexadecimal(False)

    bbs.reinit('0000')
    print '=' , bbs , 'zeroed=' , bbs.zeroed()
    bbs.set(1)
    print '=' , bbs , 'zeroed=' , bbs.zeroed()
