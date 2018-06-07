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


def open_xmind(file_path):
    """open xmind as zip file and cache the content."""
    with ZipFile(file_path) as xmind:
        for f in xmind.namelist():
            for key in [content_xml, comments_xml]:
                if f == key:
                    cache[key] = xmind.open(f).read().decode('utf-8')


def check_xmind():
    """check xmind contains valid topics and return root topic node."""
    tree = xmind_content_to_etree(cache[content_xml])
    assert isinstance(tree, Element)

    try:
        root_topic_node = tree.find('sheet').find('topic')
        logging.info("Parse topic: {}".format(title_of(root_topic_node)))
    except:
        logging.error('Cannot find any topic in your xmind!')
        raise

    return root_topic_node


def xmind_to_dict(file_path):
    """Open and convert xmind to dict type."""
    open_xmind(file_path)
    root = check_xmind()
    return _node_to_dict(root)


def _node_to_dict(node):
    """parse Element to dict data type."""
    title = title_of(node)
    comment = comments_of(node)
    note = note_of(node)
    makers = maker_of(node)
    child = children_topics_of(node)
    d = {'title': title, 'comment': comment, 'note': note, 'makers': makers}
    if child:
        d['topics'] = []
        for c in child:
            d['topics'].append(_node_to_dict(c))

    return d


def is_v2_format(d):
    """v2 xmind root dict will have a star maker, and sep is this last char of title."""
    if isinstance(d['makers'], list):
        for m in d['makers']:
            if m.startswith('star'):

                last_char = title_of(d['title'])[-1:]
                if last_char in config['valid_sep']:
                    config['sep'] = last_char

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


def parse_xmind_file(file_path):
    """Extract xmind as zip file then read the content.xml"""
    d = xmind_to_dict(file_path)
    return parse_xmind_content(d)


def parse_xmind_content(d):
    """Main function to read the content xml and return test suite data."""

    root_suite = TestSuite()
    root_suite.name = d['title']
    root_suite.sub_suites = []
    suite_nodes = d['topics']

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


def note_of(topic_node):
    note_node = topic_node.find('notes')

    if note_node is not None:
        note = note_node.find('plain').text
        return note.strip()


def debug_node(node):
    return ET.tostring(node)


def maker_of(topic_node, maker_prefix=None):
    maker_node = topic_node.find('marker-refs')
    if maker_node is not None:
        makers = []
        for maker in maker_node:
            makers.append(maker.attrib['marker-id'])

        if maker_prefix:
            for m in makers:
                if m.startswith(maker_prefix):
                    return m
        else:
            return makers


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

    # if parent:
    #     parent.append(testcase_node)
    # else:
    #     parent = [testcase_node]

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
