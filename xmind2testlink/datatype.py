class TestSuite():
    sub_suites = None
    name = ""
    details = ""
    testcase_list = None


class TestCase():
    name = ""
    summary = ""
    preconditions = ""
    importance = 2
    execution_type = ""
    steps = None


class TestStep():
    number = 1
    action = ""
    expected = ""
    execution_type = ""


cache = {}
