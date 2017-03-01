class TestSuite():
    sub_suite = None
    name = ""
    details = ""


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
