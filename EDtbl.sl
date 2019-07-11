# EDtbl.sl
# stemming logic for -ED in English
# see stemLogic.py
BLOCK ed
  IF i
    LEN = 4 {SU -1}
    IS xk {SU}
    IF t
      IS mpr {SU 1 y}
      END {SU -1}
    END {SU 1 y}
  IF e
    IF r
      LEN = 4  {FA}
      LEN > 4
        IF ga {SU -1}
        if ce {SU -1}
        IS bcg {FA}
        END
      END {SU -1}
    IF tn {SU -1}
    LEN = 4
      IS pt {SU -1}
      END
    END {FA}
  IS u {SU -1}
  IF gni
    LEN = 6
      IS drwk {SU}
      END
    END {SU -1}
  IF h
    IF s
      LEN = 4 {FA}
      IS rdk {FA}
      IF lo {FA}
      END
    END {DO MORE}
  IF b
    IF ma {FA}
    IS ioulmb {DO MORE}
    IF r
      IS e {FA}
      END {SU}
    END {FA}
  IF wn {FA}
  LEN = 4
    IS cwoksgy {SU -1}
    IS x {SU}
    IF rb {SU -1 ed}
    IF ps {SU -1 ed}
    IF lp {SU -1 ad}
    IS h {FA}
    IF l
      IS s {FA}
      IS f {SU -1 e}
      END {SU -1 ed}
    END {FA}
  LEN = 3
    IS f {SU -1 ed}
    IS l {SU -1 ad}
    END {FA}
  IF l
    IF si {SU -1 ad}
    IF ived {SU}
    IF ari {SU}
    END {DO MORE}
  IF fre {SU -1 ed}
  IF m
    IF h {FA}
    IF aho {FA}
    IF m
      IF aho {FA}
      end {SU 1}
    IF e
      IS e {SU}
      END {SU -1}
    IF i
      IS au {SU}
      END {SU -1}
    IS lr {SU}
    IF a
       IS eo {SU}
       END {SU -1}
    IS u {SU -1}
    IF osn {SU}
    IF oo {SU}
    IF o {SU -1}
    end {SU 1} 
  IF f
    IF f
      IF ioc {SU 1}
      END {SU}
    IF ei {SU}
    IF l {SU}
    IF ee {SU}
    IS aio {DO MORE}
    END {SU -1 ed}
  IF vve {SU 1}
  IF r
    IS fthd {FA}
    IF ar {FA}
    IF c
      IF ass {SU -1}
      END {FA}
    IF b
      IS norts {SU 0 eed}
      END {SU}
    IF yt {SU}
    END
DEFAULT {DO MORE}
