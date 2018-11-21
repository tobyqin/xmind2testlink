"""
to debug real xmind files.
"""

import xmind2testlink.xmind_parser as parser

xmind = r"my.xmind"


def test_parse_xmind_file():
    out = parser.xmind_to_suite(xmind)
    print(out)
