def xmind_to_dict(file_path):
    """Open and convert xmind to dict type."""
    from .xreader import open_xmind, get_sheets, sheet_to_dict

    open_xmind(file_path)
    data = []

    for s in get_sheets():
        data.append(sheet_to_dict(s))

    return data


def get_default_sheet(d):
    assert len(d) >= 0, 'Invalid xmind: should have at least 1 sheet!'
    return d[0]


def get_logger():
    from .xreader import logger
    return logger


def flat_suite(suite):
    tests = []

    for suite in suite.sub_suites:
        for test in suite.testcase_list:
            d = test.to_dict()
            d['suite'] = suite.name
            tests.append(d)

    return tests


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


def _filter_empty_value(values):
    return [v for v in values if v]


def is_testcase_topic(d):
    priority = get_priority(d)

    if priority:
        return True

    child_node = d.get('topics', [])

    if child_node:
        return False

    # consider image node?
    return True


def build_testcase_title(nodes):
    values = [n['title'] for n in nodes]
    values = _filter_empty_value(values)
    return _config['sep'].join(values)


def build_testcase_precondition(nodes):
    values = [n['comment'] for n in nodes]
    values = _filter_empty_value(values)
    comment_list = [comment_list for comment_list in values]

    comments = []
    for lst in comment_list:
        for comment in lst:
            comments.append(comment['content'])

    return _config['precondition_sep'].join(comments)


def build_testcase_summary(nodes):
    values = [n['note'] for n in nodes]
    values = _filter_empty_value(values)
    return _config['summary_sep'].join(values)


def parse_step(step_dict):
    step = TestStep()
    step.action = step_dict['title']
    expected_node = step_dict.get('topics', None)

    if expected_node is not None:
        step.expected = expected_node[0]['title']

    return step


def parse_steps(steps_dict):
    steps = []

    for step_number, step_node in enumerate(steps_dict, 1):
        step = parse_step(step_node)
        step.number = step_number
        steps.append(step)

    return steps


def parse_testcase(testcase_dict, parent=None):
    testcase = TestCase()
    nodes = parent + [testcase_dict] if parent else [testcase_dict]

    testcase.name = build_testcase_title(nodes)
    testcase.summary = build_testcase_summary(nodes)
    testcase.preconditions = build_testcase_precondition(nodes)
    testcase.importance = get_priority(testcase_dict)

    steps_node = testcase_dict.get('topics', None)

    if steps_node is not None:
        testcase.steps = parse_steps(steps_node)

    return testcase