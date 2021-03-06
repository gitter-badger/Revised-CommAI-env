#!/usr/bin/env python3
#
# Copyright (c) 2017-, Stephen B. Hope
# All rights reserved.
#
# CommAI-env source files, Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the LICENSE file in the root directory of this
# source tree. An additional grant of patent rights can be found in the PATENTS file in the same directory.

# TODO fix imports revised_core
import unittest
from revised_core import serializer


class TestSerializer(unittest.TestCase):
    """

    """

    def testConsistency(self):
        """ greek letter alpha (not working in current ascii serialization)

        :return:
        """
        slzr = serializer.StandardSerializer()
        self.assertEqual('a', slzr.to_text(slzr.to_binary('a')))
        self.assertEqual(' ', slzr.to_text(slzr.to_binary(' ')))
        self.assertEqual(u"\u03B1", slzr.to_text(slzr.to_binary(u"\u03B1")))

    def testScramblingSerializerWrapper(self):
        """

        :return:
        """
        slzr = serializer.ScramblingSerializerWrapper(
            serializer.StandardSerializer())
        self.assertEqual(slzr.tokenize("a b"), [("a", "WORD"), (" ", 'SILENCE'), ('b', 'WORD')])
        self.assertEqual(slzr.tokenize("a  b"), [("a", "WORD"), (" ", 'SILENCE'), (" ", 'SILENCE'), ('b', 'WORD')])
        self.assertEqual(slzr.tokenize("a b "), [("a", "WORD"), (" ", 'SILENCE'), ('b', 'WORD'), (' ', 'SILENCE')])
        self.assertEqual(slzr.tokenize("a b, "), [("a", "WORD"), (" ", 'SILENCE'), ('b', 'WORD'),
                                                  (',', 'PUNCT'), (' ', 'SILENCE')])
        self.assertEqual(slzr.tokenize("a b ."), [("a", "WORD"), (" ", 'SILENCE'), ('b', 'WORD'), (' ', 'SILENCE'),
                                                  ('.', 'PUNCT')])


def main():
    """

    :return:
    """
    unittest.main()

if __name__ == '__main__':
    main()
