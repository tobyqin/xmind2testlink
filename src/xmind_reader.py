from .datatype import *
from xml.etree import ElementTree as  ET
from xml.etree.ElementTree import Element
import re
import logging


def read_xmind(xmind_path):
    """Extract xmind as zip file then read the content.xml"""
    pass


def parse_xmind_content(content_xml_path):
    """Main function to read the content xml and return test suite data."""

    xml_root = read_xml_as_etree(content_xml_path)
    assert isinstance(xml_root, Element)

    try:
        xml_root_suite = xml_root.find('sheet').find('topic')
        logging.info("Parse topic: {}".format(title_of(xml_root_suite)))
    except:
        logging.error('Cannot find any topic in your xmind!')
        raise

    root_suite = TestSuite()
    root_suite.sub_suites = []
    suite_nodes = children_topics_of(xml_root_suite)

    if not suite_nodes:
        raise ValueError("Cannot find any test suite in xmind!")

    for node in suite_nodes:
        suite = parse_suite(node)
        root_suite.sub_suites.append(suite)

    return root_suite


def read_xml_as_etree(xml_path):
    with open(xml_path) as f:
        xml_content = f.read()

        # Remove the default namespace definition (xmlns="http://some/namespace")
        xml_content = re.sub(r'\sxmlns="[^"]+"', '', xml_content, count=1)
        return ET.fromstring(xml_content)


def title_of(node):
    return node.find('title').text


def children_topics_of(topic_node):
    children = topic_node.find('children')

    if children:
        return children.find('./topics[@type="attached"]')


def parse_step(step_node):
    step = TestStep()
    step.action = title_of(step_node)
    expected_node = children_topics_of(step_node)

    if expected_node:
        step.expected = title_of(children_topics_of(step_node)[0])

    return step


def parse_steps(steps_node):
    steps = []

    for step_number, step_node in enumerate(steps_node, 1):
        step = parse_step(step_node)
        step.number = step_number
        steps.append(step)

    return steps


def parse_testcase(testcase_node):
    testcase = TestCase()
    testcase.name = title_of(testcase_node)
    steps_node = children_topics_of(testcase_node
                                    )
    if steps_node:
        testcase.steps = parse_steps(steps_node)

    return testcase


def parse_suite(suite_node):
    suite = TestSuite()
    suite.name = title_of(suite_node)
    suite.details = "todo"
    suite.testcase_list = []

    for node in children_topics_of(suite_node):
        testcase = parse_testcase(node)
        suite.testcase_list.append(testcase)

    return suite
