"""
V2 module to parse xmind file into test suite and test case objects.
"""

from .datatype import *
from .shared_parser import *

_config = {'sep': ' ', 'valid_sep': '/>-+', 'precondition_sep': '\n', 'summary_sep': '\n'}


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


def is_v2_format(d):
    """v2 xmind root dict will have a star maker, and sep is this last char of title."""
    if isinstance(d['makers'], list):
        for m in d['makers']:
            if m.startswith('star'):

                last_char = d['title'][-1:]
                if last_char in _config['valid_sep']:
                    _config['sep'] = last_char

                return True


def get_priority(d):
    if isinstance(d['makers'], list):
        for m in d['makers']:
            if m.startswith('priority'):
                return m


def is_testcase_topic(d):
    priority = get_priority(d)

    if priority:
        return True

    child_node = d.get('topics', [])

    if child_node:
        return False

    # consider image node?
    return True


def _filter_empty_value(values):
    return [v for v in values if v]


def build_testcase_title(nodes):
    values = [title_of(n) for n in nodes]
    values = _filter_empty_value(values)
    return config['sep'].join(values)


def build_testcase_precondition(nodes):
    values = [comments_of(n) for n in nodes]
    values = _filter_empty_value(values)
    return config['precondition_sep'].join(values)


def build_testcase_summary(nodes):
    values = [note_of(n) for n in nodes]
    values = _filter_empty_value(values)
    return config['summary_sep'].join(values)


def parse_step(step_node):
    step = TestStep()
    step.action = step_node['title']
    expected_node = step_node.get('topics', None)

    if expected_node is not None:
        step.expected = expected_node[0]['title']

    return step


def parse_steps(steps_node):
    steps = []

    for step_number, step_node in enumerate(steps_node, 1):
        step = parse_step(step_node)
        step.number = step_number
        steps.append(step)

    return steps


def parse_testcase(testcase_node, parent=None):
    testcase = TestCase()

    testcase.name = testcase_node['title']
    testcase.summary = testcase_node['note']
    testcase.importance = get_priority(testcase_node)
    testcase.preconditions = testcase_node['comment']
    steps_node = testcase_node.get('topics', None)

    if steps_node is not None:
        testcase.steps = parse_steps(steps_node)

    return testcase


def parse_testcase_list(node, parent=None):
    if is_testcase_topic(node):
        yield parse_testcase(node, parent)

    else:
        if not parent:
            parent = []

        parent.append(node)
        topics = node['topics'] or []
        for child in topics:
            yield from parse_testcase_list(child, parent)


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
