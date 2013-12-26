! EDtbl.sl
! stemming logic for -ED in English
! see stemLogic.py
BLOCK ed
  IF i
    LEN = 4 {SU -1}
    IS xk {SU}
    IF t
      IS p {SU 1 y}
      END {SU -1}
    END {SU 1 y}
  IF e
    IF r
      LEN = 4  {FA}
      LEN > 4
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
      IS rwk {SU}
      END
    END {SU -1}
  IF h
    IF s
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
  IF lsi {SU -1 ad}
  IF fre {SU -1 ed}
  IF mh {FA}
  IF f
    IS afio {DO MORE}
    END {SU -1 ed}
  IF r
    IS fthd {FA}
    IF ar {FA}
    IF c
      IF ass {SU -1}
      END {FA}
    IF bn {SU -1 ed}
    IF yt {SU}
    END
DEFAULT {DO MORE}
