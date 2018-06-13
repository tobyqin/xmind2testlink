import logging
from json import dumps
from os.path import join, dirname

import xmind2testlink.xmind_parser as parser
from xmind2testlink.sharedparser import flat_suite
from xmind2testlink.xreader import set_logger_level

set_logger_level(logging.DEBUG)

xml_dir = dirname(__file__)
xmind_v1_file = join(xml_dir, 'Test cases by xmind v1.xmind')
xmind_v2_file = join(xml_dir, 'Test cases by xmind v2.xmind')


def test_parse_xmind_auto():
    v1 = parser.xmind_to_suite(xmind_v1_file)
    exp = parser.xmind_to_suite_v1(xmind_v1_file)
    assert v1.to_dict() == exp.to_dict()

    v2 = parser.xmind_to_suite(xmind_v2_file)
    exp = parser.xmind_to_suite_v1(xmind_v1_file)
    assert v2.to_dict() == exp.to_dict()


def test_parse_xmind_v1():
    test_suite = parser.xmind_to_suite_v1(xmind_v1_file)
    assert test_suite.name == "test case by xmind"
    assert len(test_suite.sub_suites) == 5
    assert test_suite.sub_suites[0].name == "demo suite"
    assert test_suite.sub_suites[1].name == "apple suite"


def test_parse_xmind_v2():
    test_suite = parser.xmind_to_suite_v2(xmind_v2_file)
    assert test_suite.name == "Test cases by xmind v2"
    assert len(test_suite.sub_suites) == 3
    assert test_suite.sub_suites[0].name == "ui check"
    assert test_suite.sub_suites[1].name == "db check"


def test_flat_suite():
    test_suite = parser.xmind_to_suite(xmind_v2_file)
    out = flat_suite(test_suite)
    print(dumps(out, indent=2))
