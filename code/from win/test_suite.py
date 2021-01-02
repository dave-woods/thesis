import string_functions
import pytest

@pytest.mark.parametrize('string_length_string, string_length_length', [
    ('', 1),
    ('|', 2),
    ('||', 3),
    ('a|b', 2),
    ('|a|a,b|c|', 5)
])
def test_string_length(string_length_string, string_length_length):
    assert string_functions.string_length(string_length_string) == string_length_length