import logging
from json import dumps, loads
from os.path import join, dirname

import xmind2testlink.xmind_parser as parser
from xmind2testlink.sharedparser import flat_suite, cache
from xmind2testlink.xreader import set_logger_level

set_logger_level(logging.DEBUG)

xml_dir = dirname(__file__)
xmind_v1_file = join(xml_dir, 'Test cases by xmind v1.xmind')
xmind_v2_file = join(xml_dir, 'Test cases by xmind v2.xmind')
xmind_x_file = join(xml_dir, 'test-x.xmind')


def load_expected(xmind):
    file = xmind[:-5] + 'json'
    with open(file, encoding='utf8') as f:
        return loads(f.read())


def test_parse_xmind_auto():
    v1 = parser.xmind_to_suite(xmind_v1_file)
    cache.clear()
    exp = parser.xmind_to_suite_v1(xmind_v1_file)
    assert v1.to_dict() == exp.to_dict()

    v2 = parser.xmind_to_suite(xmind_v2_file)
    cache.clear()
    exp = parser.xmind_to_suite_v2(xmind_v2_file)
    assert v2.to_dict() == exp.to_dict()


def test_parse_xmind_v1():
    test_suite = parser.xmind_to_suite_v1(xmind_v1_file)
    expected = load_expected(xmind_v1_file)
    assert flat_suite(test_suite) == expected


def test_parse_xmind_v2():
    test_suite = parser.xmind_to_suite_v2(xmind_v2_file)
    expected = load_expected(xmind_v2_file)
    assert flat_suite(test_suite) == expected


def test_flat_suite():
    test_suite = parser.xmind_to_suite(xmind_v2_file)
    out = flat_suite(test_suite)
    print(dumps(out, indent=2))


def test_x_flat_suite():
    test_suite = parser.xmind_to_suite(xmind_x_file)
    out = flat_suite(test_suite)
    print(dumps(out, indent=2))
