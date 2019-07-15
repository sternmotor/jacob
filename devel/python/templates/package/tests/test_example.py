#!/usr/bin/env python3
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import example


class TestJoke(unittest.TestCase):
    def test_is_string(self):
        s = example.joke()
        self.assertTrue(isinstance(s, basestring))
