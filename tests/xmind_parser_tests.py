import logging
from json import dumps
from os.path import join, dirname

import xmind2testlink.xmind_parser as v1
import xmind2testlink.xmind_parser_v2 as v2
from xmind2testlink.xreader import set_logger_level

set_logger_level(logging.DEBUG)

xml_dir = dirname(__file__)
xmind_v1_file = join(xml_dir, 'Test cases by xmind v1.xmind')
xmind_v2_file = join(xml_dir, 'Test cases by xmind v2.xmind')


def test_parse_xmind_v1():
    test_suite = v1.xmind_to_suite(xmind_v1_file)
    assert test_suite.name == "test case by xmind"
    assert len(test_suite.sub_suites) == 5
    assert test_suite.sub_suites[0].name == "demo suite"
    assert test_suite.sub_suites[1].name == "apple suite"


def test_parse_xmind_v2():
    test_suite = v2.xmind_to_suite(xmind_v2_file)
    print(dumps(test_suite.to_dict(), indent=2))


def test_flat_suite():
    test_suite = v2.xmind_to_suite(xmind_v2_file)
    out = v2.flat_suite(test_suite)
    print(dumps(out, indent=2))


def test_xmind_to_dict():
    d = v2.xmind_to_dict(xmind_v2_file)
    print(dumps(d, indent=2))
