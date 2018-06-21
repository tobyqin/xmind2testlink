"""
Module to parse xmind file into test suite and test case objects.
"""

from xmind2testlink import sharedparser as __
from .datatype import *


def xmind_to_flat_dict(xmind_file):
    s = xmind_to_suite(xmind_file)
    return __.flat_suite(s)


def xmind_to_suite(xmind_file):
    """Auto detect and parser xmind to test suite object."""
    __.cache.clear()
    __.open_and_cache_xmind(xmind_file)

    if __.is_v2_format(__.cache['root']):
        return xmind_to_suite_v2(xmind_file)
    else:
        return xmind_to_suite_v1(xmind_file)


def xmind_to_suite_v1(xmind_file):
    def parse_suite(suite_dict):
        suite = TestSuite()
        suite.name = suite_dict['title']
        suite.details = suite_dict['note']
        suite.testcase_list = []
        testcase_topics = suite_dict.get('topics', [])

        for _ in testcase_topics:
            t = __.parse_testcase(_)
            suite.testcase_list.append(t)

        return suite

    __.open_and_cache_xmind(xmind_file)
    root = __.cache['root']

    suite = TestSuite()
    suite.name = root['title']
    suite.sub_suites = []

    for _ in root['topics']:
        suite.sub_suites.append(parse_suite(_))

    return suite


def xmind_to_suite_v2(xmind_file):
    def parse_testcase_list(cases_dict, parent=None):
        if __.is_testcase_topic(cases_dict):
            yield __.parse_testcase(cases_dict, parent)

        else:
            if not parent:
                parent = []

            parent.append(cases_dict)
            topics = cases_dict['topics'] or []

            for child in topics:
                for _ in parse_testcase_list(child, parent):
                    yield _

    def parse_suite(suite_dict):
        suite = TestSuite()
        suite.name = suite_dict['title']
        suite.details = suite_dict['note']
        suite.testcase_list = []
        testcase_topics = suite_dict.get('topics', [])

        for node in testcase_topics:
            for t in parse_testcase_list(node):
                suite.testcase_list.append(t)

        return suite

    __.open_and_cache_xmind(xmind_file)
    root = __.cache['root']

    suite = TestSuite()
    suite.name = root['title']
    suite.sub_suites = []

    for _ in root['topics']:
        suite.sub_suites.append(parse_suite(_))

    return suite
