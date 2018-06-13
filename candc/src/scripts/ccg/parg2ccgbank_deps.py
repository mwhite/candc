# C&C NLP tools
# Copyright (c) Universities of Edinburgh, Oxford and Sydney
# Copyright (c) James R. Curran
#
# This software is covered by a non-commercial use licence.
# See LICENCE.txt for the full text of the licence.
#
# If LICENCE.txt is not included in this distribution
# please email candc@it.usyd.edu.au to obtain a copy.

import sys
import re

def die(msg):
  print >> sys.stderr, msg
  sys.exit(1)

if len(sys.argv) != 2:
  die("""usage: parg2ccgbank_deps parg_file
where:
  parg_file is a predicate argument file from the CCGbank LDC cdrom
            or a concatenated version from the $GOLD directory""")

PARG_FILENAME = sys.argv[1]
COMMAND_LINE = ' '.join(sys.argv)

PREFACE = """# this file was generated by the following command(s):
# %s
""" % COMMAND_LINE

print PREFACE

for line in open(PARG_FILENAME):
  if line.startswith('<s '):
    continue
  if line.startswith('<\\s>'):
    print
    continue

  # convert the actual dependency to the new format
  fields = line.split()
  (arg_index, pred_index, cat, slot, arg, pred) = fields[:6]
  arg_index = int(arg_index) + 1
  pred_index = int(pred_index) + 1
  print "%s_%d %s %s %s_%d" % (pred, pred_index, cat, slot, arg, arg_index)
