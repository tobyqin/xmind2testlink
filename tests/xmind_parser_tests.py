import logging
from json import dumps
from os.path import join, dirname

import xmind2testlink.xmind_parser as v1
import xmind2testlink.xmind_parser_v2 as v2
from xmind2testlink.xreader import set_logger_level

set_logger_level(logging.DEBUG)

xml_dir = dirname(__file__)
root_node = v1.xmind_xml_to_etree(join(xml_dir, v1.content_xml))
xmind_v1_file = join(xml_dir, 'Test cases by xmind v1.xmind')
xmind_v2_file = join(xml_dir, 'Test cases by xmind v2.xmind')

with open(join(xml_dir, v1.content_xml)) as f:
    v1.cache[v1.content_xml] = f.read()

with open(join(xml_dir, v1.comments_xml)) as f:
    v1.cache[v1.comments_xml] = f.read()


def test_parse_step():
    step_node = root_node.find('.//topic[@id="2t8lod6ibp7b5cruhn5mle90vi"]')
    step = v1.parse_step(step_node)
    assert isinstance(step, v1.TestStep)
    assert step.number == 1
    assert step.action == "step 1"
    assert step.expected == "expected 1"

    # no expected node
    step_node = root_node.find('.//topic[@id="6tjmi45cj0dcfnanvplp6ug1u3"]')
    step = v1.parse_step(step_node)
    assert isinstance(step, v1.TestStep)
    assert step.number == 1
    assert step.action == "step 1 action without expected"
    assert step.expected == ""


def test_parse_steps():
    testcase_node = root_node.find('.//topic[@id="6utjnqagpc7cg6p85gk3i2qjhb"]')
    steps_node = v1.children_topics_of(testcase_node)
    steps = v1.parse_steps(steps_node)
    v1.logging.info(steps)
    assert len(steps) == 2
    assert steps[0].number == 1
    assert steps[0].action == 'step 1'
    assert steps[1].number == 2
    assert steps[1].expected == 'expected 2'


def test_parse_testcase():
    testcase_node = root_node.find('.//topic[@id="6utjnqagpc7cg6p85gk3i2qjhb"]')
    testcase = v1.parse_testcase(testcase_node)
    assert isinstance(testcase, v1.TestCase)
    assert testcase.name == 'test case 1'
    assert testcase.summary == "summary"
    assert testcase.importance == 'priority-1'
    assert testcase.preconditions == "precondition"
    assert testcase.steps[0].action == 'step 1'
    assert testcase.steps[1].number == 2


def test_parse_suite():
    suite_node = root_node.find('.//topic[@id="5t69j48tjorm60fq4og9l82t06"]')
    suite = v1.parse_suite(suite_node)
    assert isinstance(suite, v1.TestSuite)
    assert suite.name == 'apple suite'
    assert len(suite.testcase_list) == 3
    assert suite.testcase_list[0].name == 'test case title for apple 1'
    assert suite.details == "this will be a detail or summary note"


def test_parse_xmind_content():
    test_suite = v1.parse_xmind_content()
    assert isinstance(test_suite, v1.TestSuite)
    assert test_suite.name == ""
    assert len(test_suite.sub_suites) == 5
    assert test_suite.sub_suites[0].name == "demo suite"
    assert test_suite.sub_suites[1].name == "apple suite"


def test_parse_xmind_v1():
    test_suite = v1.parse_xmind_file(xmind_v1_file)
    assert test_suite.name == ""
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
