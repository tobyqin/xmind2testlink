"""
A tool to parse xmind file into testlink xml file, which will help
you generate an xml file once command run, then you can import it
into testlink manually.

Usage:
 python xmind2testlink.py [path_to_xmind_file]

Example:
 python xmind2testlink.py C:\\tests\\testcase.xmind

"""

import sys

from datatype import cache
from testlink_parser import to_testlink_xml_file, to_testlink_xml_content
from xmind_parser import parse_xmind_file


def xmind_to_testlink(xmind):
    xml_out = xmind[:-5] + 'xml'
    suite = parse_xmind_file(xmind)
    to_testlink_xml_file(suite, xml_out)
    return xml_out


def get_testcase_count(xmind):
    suite = parse_xmind_file(xmind)
    to_testlink_xml_content(suite)
    return cache.get('testcase_count', 0)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].endswith('.xmind'):
        xmind = sys.argv[1]
        xml_out = xmind_to_testlink(xmind)
        print("Generated: {}".format(xml_out))
    else:
        print(__doc__)
