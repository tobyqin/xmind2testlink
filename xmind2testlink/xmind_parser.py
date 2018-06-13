"""
Module to parse xmind file into test suite and test case objects.
"""

from .sharedparser import *

cache = {}


def _open_xmind(xmind_file):
    if not cache:
        cache['sheet'] = xmind_to_dict(xmind_file)
        cache['root'] = get_default_sheet(cache['sheet'])['topic']


def xmind_to_suite(xmind_file):
    cache.clear()
    _open_xmind(xmind_file)

    if is_v2_format(cache['root']):
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
            t = parse_testcase(_)
            suite.testcase_list.append(t)

        return suite

    _open_xmind(xmind_file)
    root = cache['root']

    suite = TestSuite()
    suite.name = root['title']
    suite.sub_suites = []

    for _ in root['topics']:
        suite.sub_suites.append(parse_suite(_))

    return suite


def xmind_to_suite_v2(xmind_file):
    def parse_testcase_list(cases_dict, parent=None):
        if is_testcase_topic(cases_dict):
            yield parse_testcase(cases_dict, parent)

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

    _open_xmind(xmind_file)
    root = cache['root']

    suite = TestSuite()
    suite.name = root['title']
    suite.sub_suites = []

    for _ in root['topics']:
        suite.sub_suites.append(parse_suite(_))

    return suite
