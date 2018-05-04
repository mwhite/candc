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

class Node:
  def __init__(self, orig):
    self.orig = orig
    self.cat = None
  def __str__(self):
    return self.orig
  def paren(self):
    if '/' in self.cat or '\\' in self.cat:
      return '(' + self.cat + ')'
    else:
      return self.cat

class TNode(Node):
  def __init__(self, orig):
    Node.__init__(self, orig)
    fields = orig[4:-1].split(' ')
    (self.head, self.cat, self.pos, self.tmp, self.nchildren) = fields
    if self.cat.endswith('[conj]'):
      self.cat = self.cat[:-6]
      self.cat = "%s\\%s" % (self.paren(), self.paren())

    self.tmp = int(self.tmp)
    self.nchildren = int(self.nchildren)
    self.left = None
    self.right = None

  def sentence(self):
    if self.right:
      return self.left.sentence() + self.right.sentence()
    else:
      return self.left.sentence()

  def count_rules(self, rules):    
    if self.left:
      self.left.count_rules(rules)
    if self.right:
      key = "%s %s" % (self.left.paren(), self.right.paren())
      rules[key] = rules.get(key, 0) + 1
      self.right.count_rules(rules)

class LNode(Node):
  def __init__(self, orig):
    Node.__init__(self, orig)
    fields = orig[4:-1].split(' ')
    (self.head, self.cat, self.pos, self.word) = fields

  def sentence(self):
    return [ self.word ]

  def count_rules(self, rules):
    return

class Tree:
  def __init__(self, lines):
    lines.reverse()
    self.root = self.parse(lines)

  def parse(self, lines):
    if lines[-1].startswith('(<T'):
      node = TNode(lines.pop())
      node.left = self.parse(lines)
      if node.nchildren == 2:
        node.right = self.parse(lines)      
    elif lines[-1].startswith('(<L'):
      node = LNode(lines.pop())
    else:
      raise 'unexpected line "%s"' % lines[-1]

    if lines[-1] != ')':
      raise 'expected closing parenthesis'
    lines.pop()

    return node

  def sentence(self):
    return self.root.sentence()

  def count_rules(self, rules):
    self.root.count_rules(rules)

print "# this file was generated by the following command(s):"
print "# " + ' '.join(sys.argv)
print

rules = {}
lines = []
for line in open(sys.argv[1]):
  if len(line) == 1:
    tree = Tree(lines)
    tree.count_rules(rules)
    lines = []
    continue

  line = line[:-1]
  if line == '###':
    continue

  lines.append(line)

rules = rules.items()
rules.sort(lambda x, y: cmp(y[1], x[1]))

for (pair, count) in rules:
  print pair