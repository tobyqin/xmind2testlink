"""
V2 module to parse xmind file into test suite and test case objects.
"""
import logging
import re
from xml.etree import ElementTree as  ET
from xml.etree.ElementTree import Element
from zipfile import ZipFile

from .datatype import *

config = {'sep': ' ', 'valid_sep': '/>-+', 'precondition_sep': '\n', 'summary_sep': '\n'}

content_xml = "content.xml"
comments_xml = "comments.xml"


def is_v2_format(root_node):
    if maker_of(root_node, maker_prefix='star'):
        last_char = title_of(root_node)[-1:]
        if last_char in config['valid_sep']:
            config['sep'] = last_char

        return True


def is_testcase_node(node):
    priority = maker_of(node, 'priority')

    if priority:
        return True

    child_node = children_topics_of(node)

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


def parse_xmind_file(file_path):
    """Extract xmind as zip file then read the content.xml"""
    with ZipFile(file_path) as xmind:
        for f in xmind.namelist():
            for key in [content_xml, comments_xml]:
                if f == key:
                    cache[key] = xmind.open(f).read().decode('utf-8')

    return parse_xmind_content()


def parse_xmind_content():
    """Main function to read the content xml and return test suite data."""
    xml_root = xmind_content_to_etree(cache[content_xml])
    assert isinstance(xml_root, Element)

    try:
        xml_root_suite = xml_root.find('sheet').find('topic')
        assert is_v2_format(xml_root_suite), 'Not a V2 xmind file!'
        logging.info("Parse topic: {}".format(title_of(xml_root_suite)))
    except:
        logging.error('Cannot find any topic in your xmind!')
        raise

    root_suite = TestSuite()
    root_suite.name = title_of(xml_root_suite)
    root_suite.sub_suites = []
    suite_nodes = children_topics_of(xml_root_suite, is_root_node=True)

    if suite_nodes is None:
        raise ValueError("Cannot find any test suite in xmind!")

    for node in suite_nodes:
        suite = parse_suite(node)
        root_suite.sub_suites.append(suite)

    return root_suite


def xmind_content_to_etree(content):
    # Remove the default namespace definition (xmlns="http://some/namespace")
    xml_content = re.sub(r'\sxmlns="[^"]+"', '', content, count=1)
    return ET.fromstring(xml_content.encode('utf-8'))


def xmind_xml_to_etree(xml_path):
    with open(xml_path) as f:
        content = f.read()
        return xmind_content_to_etree(content)


def comments_of(node):
    if cache.get(comments_xml, None):
        node_id = node.attrib.get('id', None)

        if node_id:
            xml_root = xmind_content_to_etree(cache[comments_xml])
            comment = xml_root.find('./comment[@object-id="{}"]'.format(node_id))

            if comment is not None:
                return comment.find('content').text


def title_of(node):
    title = node.find('title')

    if title is not None:
        return title.text


def id_of(node):
    title = node.find('id')

    if title is not None:
        return title.text


def note_of(topic_node):
    note_node = topic_node.find('notes')

    if note_node is not None:
        note = note_node.find('plain').text
        return note.strip()


def debug_node(node):
    return ET.tostring(node)

def maker_of(topic_node, maker_prefix):
    maker_node = topic_node.find('marker-refs')
    if maker_node is not None:
        for maker in maker_node:
            maker_id = maker.attrib['marker-id']
            if maker_id.startswith(maker_prefix):
                return maker_id


def children_topics_of(topic_node, is_root_node=False):
    children = topic_node.find('children')

    if children is not None:
        # root node title is always empty
        # if not is_root_node:

        # # when topic title is empty or starts with "!" will be ignored
        # title = title_of(children)
        # if not title or title.startswith('!'):
        #     return None

        return children.find('./topics[@type="attached"]')


def parse_step(step_node):
    step = TestStep()
    step.action = title_of(step_node)
    expected_node = children_topics_of(step_node)

    if expected_node is not None:
        step.expected = title_of(expected_node[0])

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

    if parent:
        parent.append(testcase_node)
    else:
        parent = [testcase_node]

    testcase.name = build_testcase_title(parent)
    testcase.summary = build_testcase_summary(parent)
    testcase.importance = maker_of(testcase_node, 'priority')
    testcase.preconditions = build_testcase_precondition(parent)
    steps_node = children_topics_of(testcase_node)

    if steps_node is not None:
        testcase.steps = parse_steps(steps_node)

    return testcase


def parse_testcase_list(node, parent=None):
    if is_testcase_node(node):
        yield parse_testcase(node, parent)

    else:
        if not parent:
            parent = []

        parent.append(node)
        return parse_testcase_list(children_topics_of(node), parent)


def parse_suite(suite_node):
    suite = TestSuite()
    suite.name = title_of(suite_node)
    suite.details = note_of(suite_node)
    suite.testcase_list = []
    testcase_nodes = children_topics_of(suite_node)

    if testcase_nodes is not None:
        for node in testcase_nodes:
            for t in parse_testcase_list(node):
                suite.testcase_list.append(t)

    return suite
