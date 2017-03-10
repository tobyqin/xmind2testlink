from xmind2testlink.testlink_parser import *
from .xmind_parser_tests import *

test_suite = parse_xmind_file(xmind_file)
test_link_xml = 'testlink.xml'


def test_to_testlink_xml():
    if exists(test_link_xml):
        os.remove(test_link_xml)

    to_testlink_xml_file(test_suite, test_link_xml)
    # manually import and verify the result

    assert exists(test_link_xml)
    os.remove(test_link_xml)
