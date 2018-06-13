"""
A tool to parse xmind file into testlink xml file, which will help
you generate a testlink recognized xml file, then you can import it
into testlink as test suites.

Usage:
 xmind2testlink [path_to_xmind_file]

Example:
 xmind2testlink C:\\tests\\testcase.xmind

"""

import sys

from xmind2testlink.datatype import cache
from xmind2testlink.testlink_parser import to_testlink_xml_file, to_testlink_xml_content
from xmind2testlink.xmind_parser import xmind_to_suite


def xmind_to_testlink(xmind):
    xml_out = xmind[:-5] + 'xml'
    suite = xmind_to_suite(xmind)
    to_testlink_xml_file(suite, xml_out)
    return xml_out


def get_testcase_count(xmind):
    suite = xmind_to_suite(xmind)
    to_testlink_xml_content(suite)
    return cache.get('testcase_count', 0)


def main():
    if len(sys.argv) > 1 and sys.argv[1].endswith('.xmind'):
        xmind = sys.argv[1]
        xml_out = xmind_to_testlink(xmind)
        print("Generated: {}".format(xml_out))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
