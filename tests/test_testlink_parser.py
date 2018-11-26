from tests.test_xmind_parser import xmind_v1_file
from xmind2testlink.testlink_parser import *
from xmind2testlink.xmind_parser import xmind_to_suite

test_suite = xmind_to_suite(xmind_v1_file)
test_link_xml = 'testlink.xml'


def test_to_testlink_xml():
    if exists(test_link_xml):
        os.remove(test_link_xml)

    to_testlink_xml_file(test_suite, test_link_xml)
    with open(test_link_xml) as f:
        content = f.read()

    assert "apple suite" in content
    assert "my test case 2" in content
    assert "expected something" in content
    assert "only with precondition" in content
    assert "summary of test case" in content
    assert "ignore me" not in content
    assert "<importance>3</importance>" in content
    os.remove(test_link_xml)
