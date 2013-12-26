#!/usr/bin/python
# PyElly - scripting tool for analyzing natural language
#
# ellyBits.py : 22oct2013 CPM
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
define bit operations required by Elly parsing
"""

import array

hxh = { '0':0 , '1':1 , '2':2 , '3':3 , '4':4 ,  # convert hex digit to integer
        '5':5 , '6':6 , '7':7 , '8':8 , '9':9 ,  #
        'A':10 , 'B':11 , 'C':12 ,               #
        'D':13 , 'E':14 , 'F':15                 #
      }

hex = u'0123456789ABCDEF'  # for converting to hexadecimal

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

    n,m = divmod(nbc,N)
    if m > 0: n += 1
    return n

def join ( a , b ):

    """
    combine two lists of EllyBits to compare against compound bits

    arguments:
        a   - EllyBits object
        b   - EllyBits object

    returns:
        merged lists of bytes for comparison
    """

    return a.data + b.data

def check ( bs , ps ):

    """
    check for match against compounded bits and positive and negative pattern

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
    except:
        return '--'

class EllyBits(object):

    """
    bit string as Python array of byte values

    attributes:
        data  - array for bits
    """

    def __init__ ( self , nbs=nB*N ):
        """
        initialize
        arguments:
            self  -
            nbs   - number of bits in string
        """
#       print 'nbs=' , nbs
        n = getByteCountFor(nbs)
        self.data = array.array('B',(0,)*n)  # want unsigned char as array element = 'B'

    def set ( self , k ):
        """
        set kth bit by OR'ing
        arguments:
            self  -
            k     - which bit
        """
        n,m = divmod(k,N)
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
        n,m = divmod(k,N)
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
            r     - bit string to compare with
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
            r     - bit string to compare with
        returns:
            True if bits intersect, False otherwise
        """
        m = len(self.data)
        n = len(r.data)
        if n > m: n = m
        for i in range(n):
            if self.data[i] & r.data[i] != 0: return True
        return False
            
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
            r     - bit string to OR with
        """
        m = len(self.data)
        n = len(r.data)
        if n > m: n = m
        for i in range(n):
            self.data[i] |= r.data[i]  # disjunction

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
            n,m = divmod(b,16)
            bs.append(hex[n])
            bs.append(hex[m])
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

    bs = EllyBits(K)
    bs.set(0)
    bs.set(6)
    bs.set(11)

    print "bs before:",bs.data,"hex=",bs.hexadecimal()
    bt = EllyBits(K)
    bt.set(9)
    print "bt before:",bt.data,"hex=",bt.hexadecimal()
    bs.combine(bt)
    print "bs combined with bs:",bs.data,"hex=",bs.hexadecimal()

    print "test bit  9 of bs",bs.test(9)
    print "test bit 10 of bs",bs.test(10)
    print "test bit 11 of bs",bs.test(11)

    cbs = bs.compound()
    print "compound bs=",type(cbs),show(cbs)
    ps = EllyBits(K)
    ns = EllyBits(K)
    ps.set(6)
    ns.set(7)
    print 'ps=', ps.hexadecimal()
    print 'ns=', ns.hexadecimal()
    tbs = join(ps,ns)
    print "join ps, ns=",type(tbs),show(tbs)

    print 'check compound versus join=' , check(cbs,tbs)

    print "current   bs",bs.data,"hex=",bs.hexadecimal()
    bs.complement()
    print "complemented",bs.data,"hex=",bs.hexadecimal()
    bs.clear()
    print "cleared   bs",bs.data,"hex=",bs.hexadecimal()

    ps.set(7)
    print 'comparing x=' , ps.hexadecimal() , 'and y=' , ns.hexadecimal()
    print 'x equal y:' , ps.equal(ns)
    print 'x match y:' , ps.match(ns)
    print 'y match x:' , ns.match(ps)
    ns.set(6)
    print 'z=' , ns.hexadecimal()
    print 'x match z`:' , ps.equal(ns)

    bs.reinit('FFEE')
    print 'set bs to FFEE'
    print "bs:",bs.data,"hex=",bs.hexadecimal()
