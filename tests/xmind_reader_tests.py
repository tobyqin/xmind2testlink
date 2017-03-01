from src.xmind_reader import *
from os import path


def test_read_xmind_xml():
    content_xml = path.join(path.dirname(__file__), 'xmind_content.xml')
    with open(content_xml) as f:
        content = f.readlines()
        test_suite = read_xmind_xml(content)

        assert isinstance(test_suite, TestSuite)
        assert test_suite.name == ""
