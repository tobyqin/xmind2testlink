from .datatype import *
from xml.etree import ElementTree as  ET
import re
import logging


def read_xmind(xmind_path):
    """Extract xmind as zip file then read the content.xml"""
    pass


def read_xmind_xml(content_xml_path):
    """Main function to read the content xml and return test suite data."""

    with open(content_xml_path) as f:
        xml_content = f.read()

    def get_title(node):
        return node.find('title').text

    # Remove the default namespace definition (xmlns="http://some/namespace")
    xml_content = re.sub(r'\sxmlns="[^"]+"', '', xml_content, count=1)

    xml_root = ET.fromstring(xml_content)
    try:
        xml_root_suite = xml_root[0][0]
        logging.info("Found test case topic: {}".format(get_title(xml_root_suite)))
    except:
        logging.error('Cannot find test case topic!')
        raise

    root_suite = TestSuite()

    def process_step(xml_step):
        pass

    def process_testcase(xml_testcase):
        pass

    def process_suite(xml_suite):
        for xml_testcase in xml_suite:
            if not get_title(xml_testcase).startswith('!'):
                process_testcase(xml_testcase)

    for xml_suite in xml_root_suite[1]:
        if xml_suite.attrib['type'] == 'attached':
            process_suite(xml_suite)

    return root_suite
