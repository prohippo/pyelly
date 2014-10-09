# INGtbl.sl
# stemming logic for -ING in English
# see stemLogic.py
BLOCK ing
  LEN = 4 {FA}
  IS eo {SU}
  IF y
    IF tp {SU}
    IS t {SU 1 ie}
    IF d
      IS aou {SU}
      END {SU 1 ie}
    IF l
      IF eb {SU 1 ie}
      IS lfep {SU}
      END {SU 1 ie}
    IF v
      LEN = 5 {SU 1 ie}
      END
    IF my {SU 1 ie}
    END {SU}
  LEN = 5
    IF ke {SU 0 e}
    IS csukx {DO MORE}
    IF wo {SU 0 e}
    IF wa {SU 0 e}
    IF ga {SU 0 e}
    IF pa {SU 0 e}
    END {FA}
  IF h
    IF t
      IS yr {FA}
      IF on {FA}
      IF em {FA}
      END {SU 0 e}
    IF s
      IS dr {FA}
      END
    END {DO MORE}
  IF gn
    IF i
      IS hp {SU 0 e}
      IF rf {SU 0 e}
      IF rc {SU 0 e}
      IF wt {SU 0 e}
      LEN = 7
        IS t {SU 0 e}
        END
      END {SU}
    IF ah {SU 0 e}
    IF u {SU 0 e}
    END {SU}
  IF kep {FA}
  IF r
    IF reh {FA}
    IF rae {FA}
    IF ca {SU 0 e}
    IF yt {SU}
    IF ud
      LEN = 6 {FA}
      END {SU 0 e}
    IS pt {FA}
    END {DO MORE}
  IF wt {FA}
  IF nt {FA}
  IF nni
    LEN = 6 {FA}
    END {DO MORE}
  IF j {FA}
  IF l
    IF eg
      IF du {SU}
      END {FA}
    IF ra
      IF n {SU}
      END {FA}
    IF re {FA}
    IF ht {FA}
    IF bi {FA}
    IF pmu {FA}
    IF pas {FA}
    IF pirts {FA}
    IF dnuo {FA}
    IF dees {FA}
    IF kcud {FA}
    IF sog {FA}
    IF eri {FA}
    IF ta {FA}
    IF fl {FA}
    END
  IF sd {SU}
  IF vve {SU 1}
DEFAULT {DO MORE}
