# Ntbl.sl
# stemming logic for -N (a participial variation of -ED) in English
# see stemLogic.py
BLOCK n
  IF ow
    LEN = 3 {SU 1 in}
    LEN > 5 {FA}
    IF er {SU 1 in}
    END {FA}
  LEN = 3 {FA}
  IF e
    LEN = 4
      IF eb {SU 1}
      IF es {SU}
      END {FA}
    IF t
      IF t
        IF i
          LEN = 6
            IF b {SU 2 e}
            END {FA}
          IS bmr {SU 2 e}
          END {FA}
        IF og {SU 4 et}
        END {FA}
      IF ae
        LEN = 5 {SU 1}
        IF b {SU 1}
        END
      END {FA}
    IF es {SU}
    IF l
      IF l
        IF ow {SU 4 ell}
        IF af {SU 1}
        END {FA}
      IF ots {SU 3 eal}
      END {FA}
    IF soh {SU 2 ose}
    IF zor {SU 3 eeze}
    IF v
      IF ow  {SU 3 eave}
      IF olc {SU 3 eave}
      IF i
        IS gr {SU}
        END {FA}
      IF orp {SU}
      IF ahs {SU}
      END {FA}
    IF k
      IF o
        IS pr {SU 3 eak}
        END {FA}
      IF a
        IS hlstw {SU}
        END
      END {FA}
    IF sir {SU}
    IF ddi
      IS hr {SU 2 e}
      IF b {SU 2}
      END
    END {FA}
  IF ro
    IS tw {SU 2 ear}
    IF hs {SU 2 ear}
    END {FA}
  IF w
    IF o
      IF r
        IS gh {SU}
        END {FA}
      IF l
        IF f {SU 2 y}
        END {SU}
      IS hms {SU}
      IF nk {SU}
      END {FA}
    IF e
      IS rs {SU}
      IF h {SU}
      END {FA}
    IF ar {SU}
    END {FA}
  IF ial
    LEN = 4 {SU 2 ie}
    IF s {SU 1 y}
    END
DEFAULT {FA}
