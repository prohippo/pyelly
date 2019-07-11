# undb-tbl.sl
# stemming logic for final consonant undoubling in English
# see stemLogic.py
BLOCK
  LEN = 2
    IS p {SU}
    END {SU -1}
  LEN = 3
    IF z
      IS au {SU -1}
      IF if {SU -1}
      END {SU}
    IF ru
      IS f {SU}
      END {SU -1}
    IF tub {SU -1}
    END
  IF tocyo {SU -1}
DEFAULT {SU}
