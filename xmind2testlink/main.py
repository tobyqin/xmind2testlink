"""
A tool to parse xmind file into testlink xml file, which will help
you generate a testlink recognized xml file, then you can import it
into testlink as test suites.

Usage:
 xmind2testlink [path_to_xmind_file] [-json]

Example:
 xmind2testlink C:\\tests\\testcase.xmind       => output xml
 xmind2testlink C:\\tests\\testcase.xmind -json => output json

"""

import json
import sys

from xmind2testlink.testlink_parser import to_testlink_xml_file
from xmind2testlink.xmind_parser import xmind_to_suite, xmind_to_flat_dict


def xmind_to_testlink(xmind):
    xml_out = xmind[:-5] + 'xml'
    suite = xmind_to_suite(xmind)
    to_testlink_xml_file(suite, xml_out)
    return xml_out


def xmind_to_json(xmind):
    json_out = xmind[:-5] + 'json'
    with open(json_out, 'w', encoding='utf8') as f:
        f.write(json.dumps(xmind_to_flat_dict(xmind), indent=2))

    return json_out


def main():
    if len(sys.argv) > 1 and sys.argv[1].endswith('.xmind'):
        xmind = sys.argv[1]

        if len(sys.argv) == 3 and sys.argv[2] == '-json':
            file_out = xmind_to_json(xmind)
        else:
            file_out = xmind_to_testlink(xmind)

        print('Generated: "{}"'.format(file_out))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
