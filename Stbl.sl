! Stbl.sl
! stemming logic for -S in English
! see stemLogic.py
BLOCK s
  IF ys {FA}
  LEN < 3 {FA}
  LEN = 3
    IF d
      IS ai {SU}
      END
    END {FA}
  LEN = 4
    IF nel {FA}
    IF ai {FA}
    IS is {FA}
    IF exa {SU 1 is}
    IF u
      IS mnpt {SU}
      END {FA}
    IF eog {SU 1}
    END {SU}
  IF ei
    IF tros {SU}
    IF koo {SU}
    IF vo {SU}
    IF rola {SU}
    IF ppuy {SU}
    IF re
      IF s
        IF im {SU 2 y}
        END {FA}
      IF to {SU}
      END {SU 2 y}
    IF t
      IS iu {SU 2 y}
      LEN = 6 {SU}
      END
    END {SU 2 y}
  IF e
    IF o
      LEN = 5 {SU}
      IS dg {SU 1}
      IF na {SU}
      IF rh {SU}
      IS h {SU}
      IF t
        IS aist {SU 1}
        END {SU}
      END {SU 1}
    IF s
      IF ag {SU 1}
      IF ai {SU 1}
      IF u
        IF c
          IS or {SU 1}
          END {SU}
        IF r
          IS io {SU 1}
          END {SU}
        IF lp {SU 1}
        IS ipt {SU 1}
        LEN = 5
          IF b {SU 1}
          END
        END {SU}
      IF ee {SU}
      IS ey {SU 1 is}
      IS sd {SU 1}
      IF irc {SU 1 is}
      IF ats {SU 1 is}
      IF ahpm {SU 1 is}
      IF nel {SU 1}
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
    IF zt {SU 1}
    END {SU}
  IF i
    IF nn {FA}
    IF me {SU}
    IF st {SU}
    IF hc {SU}
    IS nzq {SU}
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
  IF rm {FA}
DEFAULT {SU}
