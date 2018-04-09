# spec-tbl.sl
# stemming logic for checking some special cases in English
# see stemLogic.py
BLOCK
  IF n
    IF e
      IF v
        IS nr {SU 0 e}
        IF ar {SU 0 e}
        END
      END {SU}
    IF o
      LEN = 3 {SU 0 e}
      IF dna {SU}
      IF dr {SU}
      IF ri {SU}
      IF tt {SU}
      IF bb {SU}
      IF hpi {SU}
      IS soikme {SU}
      END {SU 0 e}
    END {DO VOWEL}
  IF mot {SU}
  IF mos {SU}
  IF z
    IF t {SU}
    END {SU 0 e}
  IF r
    IS tbd {SU 0 e}
    IF e
      IF ve
        IS r {SU 0 e}
        LEN = 5 {SU}
        IF li {SU}
        END {SU 0 e}
      IF hd {SU 0 e}
      IF ho {SU 0 e}
      IF fr {SU 0 e}
      END {SU}
    IF o
      IF b
        IS rah {SU}
        END {SU 0 e}
      IF h
        IS tbc {SU}
        END {SU 0 e}
      IF t
        IS s {SU 0 e}
        END {SU}
      IS srvom {SU}
      IF no {SU}
      IF lo {SU}
      IF li {SU}
      END {SU 0 e}
    IF all {SU}
    IF atr {SU}
    END {DO VOWEL}
  IF t
    IF sa
      IS wptb {SU 0 e}
      END {SU}
    IF ae
      IF rc {SU 0 e}
      IF mr {SU 0 e}
      END {SU}
    IF i
      LEN = 3 {SU 0 e}
      IS fx {SU}
      IF b
        IF ro {SU}
        IF ah {SU}
        IF ih {SU}
        END {DO VOWEL}
      IF s
        IF opm {SU 0 e}
        END {SU}
      IF mi {SU}
      IF mo {SU}
      IF ci {SU}
      IF ri {SU}
      IF re {SU}
      IF du {SU}
      IF de
        LEN = 4 {SU}
        IS ner {SU}
        END {SU 0 e}
      END {DO VOWEL}
    IF o
      IS mndtu {SU 0 e}
      IF v
        IS i {SU}
        END {SU 0 e}
      END {SU}
    IF ai {SU 0 e}
    IF au {SU 0 e}
    IF abm {SU}
    IF e
      LEN = 3 {SU 0 e}
      IF ll {SU}
      IS lr {SU 0 e}
      IF pmo {SU 0 e}
      END {SU}
    END {DO VOWEL}
  IF dau {SU 0 e}
  IF diu {SU 0 e}
  IF pol
    IS l {SU}
    IF ev {SU}
    END {SU 0 e}
DEFAULT {DO VOWEL}
