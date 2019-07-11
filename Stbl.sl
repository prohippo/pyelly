# Stbl.sl
# stemming logic for -S in English
# see stemLogic.py
BLOCK s
  IF ys {FA}
  LEN < 3 {FA}
  LEN = 3
    IF d
      IS ai {SU}
      END
    IF ah {SU 0 ve}
    END {FA}
  LEN = 4
    IF nel {FA}
    IF ai {FA}
    IS is {FA}
    IF exa {SU 1 is}
    IF u
      IF na {FA}
      IS mnpt {SU}
      END {FA}
    IF eog {SU 1}
    IF dus {FA}
    END {SU}
  IF ei
    IF tros {SU}
    IF koo {SU}
    if nwo {SU}
    IF vo {SU}
    IF rola {SU}
    IF ppuy {SU}
    IF htoo {SU}
    IF re
      IF s
        IF im {SU 2 y}
        END {FA}
      IF to {SU}
      END {SU 2 y}
    IF lak {SU 1}
    IF t
      IS iu {SU 2 y}
      LEN = 6 {SU}
      END
    END {SU 2 y}
  IF e
    IF o
      IF tev {SU 1}
      LEN = 5 {SU}
      IS dg {SU 1}
      IF na
        IF c {SU 1}
        END {SU}
      IF rh {SU}
      IF h
        IS ac {SU 1}
        END {SU}
      IF t
        IS aist {SU 1}
        END {SU}
      END {SU 1}
    IF s
      IF ag  {SU 1}
      IF s
        IF ag {SU 2}
        IF ub {SU 2}
        END {SU 1}
      IF ai  {SU 1}
      IF inep {SU 1}
      IF u
        IF c
          IS oru {SU 1}
          END {SU}
        IF r
          IS io {SU 1}
          END {SU}
        IF lp {SU 1}
        IS ipt {SU 1}
        IF na
          LEN = 6 {SU 1}
          END
        LEN = 5
          IF b {SU 1}
          END
        END {SU}
      IF ee {SU}
      IS ey {SU 1 is}
      IS sd {SU 1}
      IF irc {SU 1 is}
      IF a
        IF ts {SU 1 is}
        IF o  {SU 1 is}
        END
      IF ahpm {SU 1 is}
      IF nel {SU 1}
      IF o
        IF h
          IS cp {SU 1 is}
          END {SU}
        IF ru {SU 1 is}
        IF eh {SU 1 is}
        END
      IF p
        IF on {SU 1 is}
        IF an {SU 1 is}
        END
      IF ilop {SU 1}
      END {SU}
    IF h
      IS t {SU}
      IF c
        LEN = 5 {SU}
        LEN = 6
          IF ir  {SU 1}
          IS nrt {SU 1}
          END {SU}
        LEN = 7
          IF il {SU}
          IF er {SU}
          END
        IF a
          IS dhr {SU}
          END
        END
      END {SU 1}
    IS x {SU 1}
    IF z
      IF t {SU 1}
      IF z
        IF ef {SU 2}
        IF iu {SU 2}
        IF ih {SU 2}
        END
      END
    IF v
      IF ooh {SU 2 f}
      IF l
        IF ow {SU 2 f}
        IF o {SU}
        IF a
          IS ch {SU 2 f}
          END
        IF e
          IF d {FA}
          END {SU 2 f}
        END {FA}
      IF iw {SU 2 fe}
      IF ra
        IF cs {SU 2 f}
        IF hw {SU 2 f}
        IF wd {SU 2 f}
        END
      IF a
        IF ol {SU 2 f}
        IF eh {SU 2 f}
        END
      END
    END {SU}
  IF i
    IF nn {FA}
    IF me {SU}
    IF man {SU}
    IF st {SU}
    IF hc {SU}
    IF jo {SU}
    IS nzq {SU}
    IF lak {SU}
    IF dah {SU}
    IF dua {SU}
    IF lea {SU}
    IF tar {SU}
    IF x
      IF eh {FA}
      IF a
        IS lr {FA}
        END
      END {SU}
    END {FA}
  IF u
    IF n
      IF em {SU}
      END {FA}
    IF ae {SU}
    IF t
      IS acio {FA}
      END {SU}
    IF dn {SU}
    IF lu
      IS ltz {SU}
      END {FA}
    IF mu {SU}
    IF rug {SU}
    IF a
      IF lu {SU}
      IF u {SU}
      END {FA}
    END {FA}
  IS su {FA}
  IF a
    IS vx {FA}
    IF sn {FA}
    IF il {FA}
    IF lg {FA}
    IF m
      IS o {SU}
      IS me {SU}
      END {FA}
    END {SU}
  IF pec {FA}
  IF rm {FA}
DEFAULT {SU}
