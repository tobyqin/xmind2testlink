"""
Module to parse xmind file into test suite and test case objects.
"""

from .sharedparser import *


def xmind_to_suite(xmind_file):
    sheet = xmind_to_dict(xmind_file)
    root = get_default_sheet(sheet)['topic']

    suite = TestSuite()
    suite.name = root['title']
    suite.sub_suites = []

    for _ in root['topics']:
        suite.sub_suites.append(parse_suite(_))

    return suite


def parse_suite(d):
    suite = TestSuite()
    suite.name = d['title']
    suite.details = d['note']
    suite.testcase_list = []
    testcase_topics = d.get('topics', [])

    for _ in testcase_topics:
        t = parse_testcase(_)
        suite.testcase_list.append(t)

    return suite
