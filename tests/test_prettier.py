import string
import sys
from collections import OrderedDict, namedtuple
from unittest.mock import MagicMock

import numpy
import pytest

from devtools.ansi import strip_ansi
from devtools.prettier import PrettyFormat, env_true, pformat, pprint

try:
    from multidict import CIMultiDict, MultiDict
except ImportError:
    CIMultiDict = None
    MultiDict = None


def test_dict():
    v = pformat({1: 2, 3: 4})
    print(v)
    assert v == (
        '{\n'
        '    1: 2,\n'
        '    3: 4,\n'
        '}')


def test_print(capsys):
    pprint({1: 2, 3: 4})
    stdout, stderr = capsys.readouterr()
    assert stdout == (
        '{\n'
        '    1: 2,\n'
        '    3: 4,\n'
        '}\n')
    assert stderr == ''


def test_colours():
    v = pformat({1: 2, 3: 4}, highlight=True)
    assert v.startswith('\x1b'), repr(v)
    v2 = strip_ansi(v)
    assert v2 == pformat({1: 2, 3: 4}), repr(v2)


def test_list():
    v = pformat(list(range(6)))
    assert v == (
        '[\n'
        '    0,\n'
        '    1,\n'
        '    2,\n'
        '    3,\n'
        '    4,\n'
        '    5,\n'
        ']')


def test_set():
    v = pformat(set(range(5)))
    assert v == (
        '{\n'
        '    0,\n'
        '    1,\n'
        '    2,\n'
        '    3,\n'
        '    4,\n'
        '}')


def test_tuple():
    v = pformat(tuple(range(5)))
    assert v == (
        '(\n'
        '    0,\n'
        '    1,\n'
        '    2,\n'
        '    3,\n'
        '    4,\n'
        ')')


def test_generator():
    v = pformat((i for i in range(3)))
    assert v == (
        '(\n'
        '    0,\n'
        '    1,\n'
        '    2,\n'
        ')')


def test_named_tuple():
    f = namedtuple('Foobar', ['foo', 'bar', 'spam'])
    v = pformat(f('x', 'y', 1))
    assert v == ("Foobar(\n"
                 "    foo='x',\n"
                 "    bar='y',\n"
                 "    spam=1,\n"
                 ")")


def test_generator_no_yield():
    pformat_ = PrettyFormat(yield_from_generators=False)
    v = pformat_((i for i in range(3)))
    assert v.startswith('<generator object test_generator_no_yield.<locals>.<genexpr> at ')


def test_str():
    pformat_ = PrettyFormat(width=12)
    v = pformat_(string.ascii_lowercase + '\n' + string.digits)
    print(repr(v))
    assert v == (
        "(\n"
        "    'abcde'\n"
        "    'fghij'\n"
        "    'klmno'\n"
        "    'pqrst'\n"
        "    'uvwxy'\n"
        "    'z\\n"
        "'\n"
        "    '01234'\n"
        "    '56789'\n"
        ")"
    )


def test_str_repr():
    pformat_ = PrettyFormat(repr_strings=True)
    v = pformat_(string.ascii_lowercase + '\n' + string.digits)
    assert v == "'abcdefghijklmnopqrstuvwxyz\\n0123456789'"


def test_bytes():
    pformat_ = PrettyFormat(width=12)
    v = pformat_(string.ascii_lowercase.encode())
    assert v == """(
    b'abcde'
    b'fghij'
    b'klmno'
    b'pqrst'
    b'uvwxy'
    b'z'
)"""


def test_short_bytes():
    assert "b'abcdefghijklmnopqrstuvwxyz'" == pformat(string.ascii_lowercase.encode())


def test_indent_numpy():
    v = pformat({'numpy test': numpy.array(range(20))})
    assert v == """{
    'numpy test': (
        array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
               17, 18, 19])
    ),
}"""


def test_indent_numpy_short():
    v = pformat({'numpy test': numpy.array(range(10))})
    assert v == """{
    'numpy test': array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
}"""


def test_ordered_dict():
    v = pformat(OrderedDict([(1, 2), (3, 4), (5, 6)]))
    print(v)
    assert v == """\
OrderedDict([
    (1, 2),
    (3, 4),
    (5, 6),
])"""


def test_frozenset():
    v = pformat(frozenset(range(3)))
    print(v)
    assert v == """\
frozenset({
    0,
    1,
    2,
})"""


def test_deep_objects():
    f = namedtuple('Foobar', ['foo', 'bar', 'spam'])
    v = pformat((
        (
            f('x', 'y', OrderedDict([(1, 2), (3, 4), (5, 6)])),
            frozenset(range(3)),
            [1, 2, {1: 2}]
        ),
        {1, 2, 3}
    ))
    print(v)
    assert v == """\
(
    (
        Foobar(
            foo='x',
            bar='y',
            spam=OrderedDict([
                (1, 2),
                (3, 4),
                (5, 6),
            ]),
        ),
        frozenset({
            0,
            1,
            2,
        }),
        [
            1,
            2,
            {1: 2},
        ],
    ),
    {1, 2, 3},
)"""


@pytest.mark.skipif(sys.version_info > (3, 5, 3), reason='like this only for old 3.5')
def test_call_args_py353():
    m = MagicMock()
    m(1, 2, 3, a=4)
    v = pformat(m.call_args)

    assert v == """\
_Call(
    (1, 2, 3),
    {'a': 4},
)"""


@pytest.mark.skipif(sys.version_info <= (3, 5, 3), reason='different for old 3.5')
def test_call_args_py354():
    m = MagicMock()
    m(1, 2, 3, a=4)
    v = pformat(m.call_args)

    assert v == """\
_Call(
    _fields=(1, 2, 3),
    {'a': 4},
)"""


def test_env_true():
    assert env_true('PATH') is False
    assert env_true('DOES_NOT_EXIST') is None


@pytest.mark.skipif(MultiDict is None, reason='MultiDict not installed')
def test_multidict():
    d = MultiDict({'a': 1, 'b': 2})
    d.add('b', 3)
    v = pformat(d)
    assert set(v.split('\n')) == {
        "<MultiDict(",
        "    'a': 1,",
        "    'b': 2,",
        "    'b': 3,",
        ")>",
    }


@pytest.mark.skipif(CIMultiDict is None, reason='CIMultiDict not installed')
def test_cimultidict():
    v = pformat(CIMultiDict({'a': 1, 'b': 2}))
    assert set(v.split('\n')) == {
        "<CIMultiDict(",
        "    'a': 1,",
        "    'b': 2,",
        ")>",
    }
