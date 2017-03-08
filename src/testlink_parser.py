"""
Module to parse test suite objects into testlink xml.
"""
import os
from io import BytesIO
from os.path import exists
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from .datatype import *


class Tags():
    xml = 'xml'
    testsuite = "testsuite"
    details = 'details'
    testcase = 'testcase'
    summary = 'summary'
    precoditions = 'preconditions'
    steps = 'steps'
    step = 'step'
    step_number = 'step_number'
    actions = 'actions'
    expected = 'expectedresults'
    execution_type = 'execution_type'
    importance = 'importance'


class Attributes():
    name = 'name'


def to_testlink_xml_file(testsuite, path_to_xml):
    """Save test suite object to testlink xml file."""
    content = to_testlink_xml_content(testsuite)
    if exists(path_to_xml):
        os.remove(path_to_xml)

    with open(path_to_xml, 'w') as f:
        f.write(prettify_xml(content))


def _convert_importance(importance_value):
    mapping = {'priority-1': '3', 'priority-2': '2', 'priority-3': '1'}
    if importance_value in mapping.keys():
        return mapping[importance_value]
    else:
        return '2'


def to_testlink_xml_content(testsuite):
    assert isinstance(testsuite, TestSuite)
    root_suite = Element(Tags.testsuite)
    root_suite.set(Attributes.name, testsuite.name)
    cache['testcase_count'] = 0

    for suite in testsuite.sub_suites:
        assert isinstance(suite, TestSuite)

        if suite.name.startswith('!'):
            continue

        suite_element = SubElement(root_suite, Tags.testsuite)
        suite_element.set(Attributes.name, suite.name)

        if suite.details and not suite.details.startswith('!'):
            e = SubElement(suite_element, Tags.details)
            e.text = suite.details

        for testcase in suite.testcase_list:
            assert isinstance(testcase, TestCase)

            if testcase.name.startswith('!'):
                continue

            cache['testcase_count'] += 1
            testcase_element = SubElement(suite_element, Tags.testcase)
            testcase_element.set(Attributes.name, testcase.name)

            if testcase.summary and not testcase.summary.startswith('!'):
                e = SubElement(testcase_element, Tags.summary)
                e.text = testcase.summary

            if testcase.preconditions and not testcase.preconditions.startswith('!'):
                e = SubElement(testcase_element, Tags.precoditions)
                e.text = testcase.preconditions

            if testcase.execution_type:
                e = SubElement(testcase_element, Tags.execution_type)
                e.text = testcase.execution_type

            e = SubElement(testcase_element, Tags.importance)
            e.text = _convert_importance(testcase.importance)

            if testcase.steps:
                steps_element = SubElement(testcase_element, Tags.steps)

                for step in testcase.steps:
                    assert isinstance(step, TestStep)

                    if step.action.startswith('!'):
                        continue
                    else:
                        step_element = SubElement(steps_element, Tags.step)

                    if step.action and not step.action.startswith('!'):
                        e = SubElement(step_element, Tags.actions)
                        e.text = step.action

                    if step.expected and not step.expected.startswith('!'):
                        e = SubElement(step_element, Tags.expected)
                        e.text = step.expected

                    if step.execution_type:
                        e = SubElement(step_element, Tags.execution_type)
                        e.text = step.execution_type

                    e = SubElement(step_element, Tags.step_number)
                    e.text = str(step.number)

    tree = ElementTree.ElementTree(root_suite)
    f = BytesIO()
    tree.write(f, encoding='utf-8', xml_declaration=True)
    return f.getvalue()


def prettify_xml(xml_string):
    """Return a pretty-printed XML string for the Element.
    """
    reparsed = minidom.parseString(xml_string)
    return reparsed.toprettyxml(indent="\t")
