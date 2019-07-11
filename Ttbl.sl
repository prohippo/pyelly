# Ttbl.sl
# stemming logic for -T (a variation of -ED) in English
# see stemLogic.py
BLOCK t
  LEN = 3
    IF il {SU 0 ght}
    IF ib {SU -1 e}
    IF as {SU 1 it}
    IF em {SU 0 et}
    IF og {SU 1 et}
    END {FA}
  IF p
    IF e
      IS wlkr {SU 1 ep}
      END {FA}
    IF ae {SU}
    END {FA}
  LEN = 4
    IF rig {SU 0 d}
    IF lig {SU 0 d}
    IF ne
      IS bs {SU 0 d}
      IF w  {SU 3 go}
      END
    IF sol {SU 0 e}
    IF ohs {SU 0 ot}
    IF fer {SU 1 ave}
    END {FA}
  IF l
    IF i
      IF op {SU}
      IF ub {SU 0 d}
      IF ps {SU 0 l}
      END {FA}
    IF aed {SU}
    IF e
      IF w  {SU 0 l}
      IF ps {SU 0 l}
      IF nk {SU 1 el}
      END
    END {FA}
  IF fe
    IF lc {SU 1 ave}
    IF r  {SU 1 ave}
    END {FA}
  IF hgu
    IF o
      IF f {SU 4 ight}
      IF ht {SU 4 ink}
      IF s {SU 4 eek}
      IF b {SU 4 uy}
      IF rb {SU 4 ing}
      END {FA}
    IF a
      IF t {SU 4 each}
      IF c {SU 4 atch}
      END {FA}
    END {FA}
  IF s
    LEN = 5
       IF elb {SU 0 s}
       IF ruc {SU 0 e}
       END
    END {FA}
  IF m {SU}
  IF n
    IF eps {SU 0 d}
    IF r
      IS au {SU}
      END {FA}
    IF e
      IF b
        IF r {FA}
        end {SU 0 d}
      IF w {SU 3 go}
      END {FA}
    IF aem {SU}
    END {FA}
  IF ohs {SU 0 ot}
  IF og
    IS er {SU 1 et}
    END
DEFAULT {FA}
