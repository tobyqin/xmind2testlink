"""
V2 module to parse xmind file into test suite and test case objects.
"""

from .sharedparser import *


def xmind_to_suite(xmind_file):
    sheet = xmind_to_dict(xmind_file)
    root = get_default_sheet(sheet)['topic']
    assert is_v2_format(root), 'Not a V2 format of xmind!'

    suite = TestSuite()
    suite.name = root['title']
    suite.sub_suites = []

    for _ in root['topics']:
        suite.sub_suites.append(parse_suite(_))

    return suite


def parse_testcase_list(node, parent=None):
    if is_testcase_topic(node):
        yield parse_testcase(node, parent)

    else:
        if not parent:
            parent = []

        parent.append(node)
        topics = node['topics'] or []

        for child in topics:
            for _ in parse_testcase_list(child, parent):
                yield _


def parse_suite(d):
    suite = TestSuite()
    suite.name = d['title']
    suite.details = d['note']
    suite.testcase_list = []
    testcase_topics = d.get('topics', [])

    for node in testcase_topics:
        for t in parse_testcase_list(node):
            suite.testcase_list.append(t)

    return suite
