# Auto-generated pytest
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'src')))
from m_top_k_frequent_words_from_text import m_top_k_frequent_words_from_text


def test_m_top_k_frequent_words_from_text():
    assert m_top_k_frequent_words_from_text('a a b c a b', 2) == [
        ('a', 3), ('b', 2)]
