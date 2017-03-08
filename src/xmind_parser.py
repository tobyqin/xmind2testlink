"""
Module to parse xmind file into test suite and test case objects.
"""
import logging
import re
from xml.etree import ElementTree as  ET
from xml.etree.ElementTree import Element
from zipfile import ZipFile

from .datatype import *

content_xml = "content.xml"
comments_xml = "comments.xml"


def parse_xmind_file(file_path):
    """Extract xmind as zip file then read the content.xml"""
    with ZipFile(file_path) as xmind:
        for f in xmind.namelist():
            if f == content_xml:
                cache[content_xml] = xmind.open(f).read().decode()

            if f == comments_xml:
                cache[comments_xml] = xmind.open(f).read().decode()

    return parse_xmind_content()


def parse_xmind_content():
    """Main function to read the content xml and return test suite data."""
    xml_root = xmind_content_to_etree(cache[content_xml])
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


def xmind_content_to_etree(content):
    # Remove the default namespace definition (xmlns="http://some/namespace")
    xml_content = re.sub(r'\sxmlns="[^"]+"', '', content, count=1)
    return ET.fromstring(xml_content)


def xmind_xml_to_etree(xml_path):
    with open(xml_path) as f:
        content = f.read()
        return xmind_content_to_etree(content)


def comments_of(node):
    if cache.get(comments_xml, None):
        xml_root = xmind_content_to_etree(cache[comments_xml])
        node_id = node.attrib['id']
        comment = xml_root.find('./comment[@object-id="{}"]'.format(node_id))

        if comment:
            return comment.find('content').text


def title_of(node):
    return node.find('title').text


def note_of(topic_node):
    note_node = topic_node.find('notes')

    if note_node:
        note = note_node.find('plain').text
        return note.strip()


def maker_of(topic_node, maker_prefix):
    maker_node = topic_node.find('marker-refs')
    if maker_node:
        for maker in maker_node:
            maker_id = maker.attrib['marker-id']
            if maker_id.startswith(maker_prefix):
                return maker_id


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
    testcase.summary = note_of(testcase_node)
    testcase.importance = maker_of(testcase_node, 'priority')
    testcase.preconditions = comments_of(testcase_node)
    steps_node = children_topics_of(testcase_node)

    if steps_node:
        testcase.steps = parse_steps(steps_node)

    return testcase


def parse_suite(suite_node):
    suite = TestSuite()
    suite.name = title_of(suite_node)
    suite.details = note_of(suite_node)
    suite.testcase_list = []
    testcase_nodes = children_topics_of(suite_node)

    if testcase_nodes:
        for node in testcase_nodes:
            testcase = parse_testcase(node)
            suite.testcase_list.append(testcase)

    return suite
