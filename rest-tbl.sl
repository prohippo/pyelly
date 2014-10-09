# rest-tbl.sl
# stemming logic for root restoration in English
# this is separate logic because it has to run after both -ED and -ING removal
# see stemLogic.py
BLOCK
  IF s
    IF s
      IF ag {SU 1}
      end {SU}
    IF ub
      LEN = 3 {SU}
      END
    IF uco {SU}
    IF ai {SU}
    IF du {SU}
    END {SU 0 e}
  IF g
    IS aedlriu {SU 0 e}
    IS g {SU 1}
    IF n
      IF o
        IS p {SU 0 e}
        END {SU}
      IF a
        IS r {SU 0 e}
        LEN = 4 {SU}
        IF lc {SU}
        END
      END {SU 0 e}
    END {SU}
  IF terp {SU}
  IF kc
    IF alle {SU 1}
    IF auov {SU 1}
    IF i
      IF n
        IS ac {SU 1}
        END {FA}
      IF lo {SU 1} 
      IF ff {SU 1}
      IF ti {SU 1}
      IF mi {SU 1}
      END
    END {SU}
  IS tnrdbmpkz {DO MORE}
  IS cvu {SU 0 e}
  IF l
    IF l
      IF otx {SU 1}
      IF ort
        IF s {SU}
        LEN = 5 {SU}
        END {SU 1}
      IF unn {SU 1}
      IF e
        IF p
          LEN = 5 {SU}
          IF ss {SU}
          END {SU 1}
        IS g {SU 1}
        LEN > 4
          IS cdbv {SU 1}
          END
        END {SU}
      IF a
        IF n {SU 1}
        IF hs {SU 1}
        IF to {SU 1}
        END
      END {SU}
    IS tsdgbpcfkz {SU 0 e}
    IF e {SU}
    IF i
      LEN < 5 {DO VOWEL}
      IF re {SU}
      IF ug {SU 0 e}
      IF v
        IF ia {SU}
        END {SU 0 e}
      END {DO VOWEL}
    IF a
      IS tvnd {SU}
      IF uq {SU}
      IF hs {SU}
      END {DO VOWEL}
    END {DO VOWEL}
  IF fa
    IS rh {SU 0 e}
    END {SU}
  IF wa
    IF nu {SU 0 e}
    IF re {SU 0 e}
    END {SU}
  IF h
    IF c
      IF a
        LEN < 5 {SU 0 e}
        END {SU}
      IF i
        LEN < 6 {SU 0 e}
        END
      END {SU}
    IF t
      IS aeio {SU 0 e}
      END
    END
DEFAULT {SU}
