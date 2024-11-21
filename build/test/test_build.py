import unittest
from src.build import *


def test_detect_compiler():
    assert detect_compiler(2, 3) == 5