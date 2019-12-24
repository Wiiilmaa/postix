import pytest

from postix.core.templatetags.dotdecimal import dotdecimal
from postix.core.templatetags.urlreplace import _urlreplace


@pytest.mark.parametrize(
    "pairs,expected",
    (
        ({"pairs": ["a", "b"]}, {"a": "b", "b": "b", "c": "c"}),
        ({"pairs": ["b", ""]}, {"a": "a", "c": "c"}),
    ),
)
def test_core_urlreplace(pairs, expected):
    assert _urlreplace({"a": "a", "b": "b", "c": "c"}, *pairs["pairs"]) == expected


@pytest.mark.parametrize("expected,value", ((".", ","), ("1.2", "1,2"), ("1.2", 1.2)))
def test_dotdecimal(value, expected):
    assert dotdecimal(value) == expected
