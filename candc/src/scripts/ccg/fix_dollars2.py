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

TAGS = re.compile(r"\|[^ ]*")
QUOTES = re.compile(r"""''?\|''|``?\|``""")

PTB = {}

def load_ptb(filename, ptb):
  for line in file(filename):
    ptbank = line[:-1]
    ccgbank = ptbank
    ccgbank = QUOTES.sub('', ccgbank)
    ccgbank = TAGS.sub('', ccgbank)
    ccgbank = ' '.join(ccgbank.split())
    ccgbank = ccgbank.replace('(', '-LRB-').replace(')', '-RRB-')
    ccgbank = ccgbank.replace('[', '-LSB-').replace(']', '-RSB-')
    ccgbank = ccgbank.replace('{', '-LCB-').replace('}', '-RCB-')
    ptb[ccgbank] = ptbank
    print >> sys.stderr, 'CCG', ccgbank
    print >> sys.stderr, 'PTB', ptbank

for filename in sys.argv[1:]:
  load_ptb(filename, PTB)

class Node:
  def __init__(self, orig):
    self.orig = orig
  def __str__(self):
    return self.orig

class TNode(Node):
  def __init__(self, orig):
    Node.__init__(self, orig)
    fields = orig[4:-1].split(' ')
    (self.cat, self.head, self.nchildren) = fields
    self.head = int(self.head)
    self.nchildren = int(self.nchildren)
    self.left = None
    self.right = None
  def sentence(self):
    if self.right:
      return self.left.sentence() + self.right.sentence()
    else:
      return self.left.sentence()

class LNode(Node):
  def __init__(self, orig):
    Node.__init__(self, orig)
    orig.startswith('(<L ')
    assert orig.endswith('>)')
    fields = orig[4:-2].split(' ')
    (self.cat, self.new_pos, self.old_pos, self.word, self.pred_arg) = fields
  def sentence(self):
    return [ self.word ]

class Tree:
  def __init__(self, line):
    line = line.replace('> ', '>\n').replace(' )', ')\n').replace('>)', '>)\n')
    lines = map(lambda x: x.strip(), line.split('\n'))
    lines.reverse()
    self.root = self.parse(lines)

  def parse(self, lines):
    if lines[-1].startswith('(<T'):
      node = TNode(lines.pop())
      node.left = self.parse(lines)
      if node.nchildren == 2:
        node.right = self.parse(lines)      
      if lines[-1] != ')':
        raise 'expected closing parenthesis'
      lines.pop()
    elif lines[-1].startswith('(<L'):
      node = LNode(lines.pop())
    else:
      raise 'unexpected line "%s"' % lines[-1]

    return node

  def sentence(self):
    return self.root.sentence()

for line in sys.stdin:
  if line.startswith('ID'):
    continue
  tree = Tree(line[:-1])
  ccgbank = ' '.join(tree.sentence())
  if ccgbank not in PTB:
    print ccgbank
