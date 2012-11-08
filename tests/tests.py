#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""
Tests for DRY document rendering.
"""

import filecmp
import os
import subprocess
import sys
import unittest

_PY3 = sys.version_info >= (3, 0)

scriptdir = os.path.split(os.path.realpath(__file__))[0]
parentdir = os.path.abspath(os.path.join(scriptdir, os.path.pardir))
sys.path.insert(0, parentdir)

import drydoc
import templatefunctions

try:
    import yaml
    _YAML = True
except ImportError:
    _YAML = False

try:
    import jinja2
    _JINJA2 = True
except ImportError:
    _JINJA2 = False


correct_a = u'汉语漢'
correct_b = u'1'
correct_rendered = u'a={a}\nb={b}\n'.format(a=correct_a, b=correct_b)

correct_example = u"""
a = %s
b = %s
...

a={{ a }}
b={{ b }}
""" % (correct_a, correct_b)

correct_yaml_jinja = u"""
a: %s
b: %s
...

a={{ a }}
b={{ b }}
""" % (correct_a, correct_b)

empty_variable_definitions = """
...
document template
"""

empty_template = """a = 1
b = 2
...
"""

no_section_separator = """a=1
..
document template
"""


def example_render_func(dry_text):
    doc = drydoc.DryDoc(dry_text, engine=drydoc.engines['example'])
    return doc.render()


def yj_render_func(dry_text):
    doc = drydoc.DryDoc(dry_text, engine=drydoc.engines['yj'])
    return doc.render()


class TestDryTextRender(unittest.TestCase):

    def test_engine_setups(self):

        self.assertEqual(_JINJA2 and _YAML, 'yj' in drydoc.engines,
                         'yj engine is missing')

    def test_correct_example(self):
        rendered = example_render_func(correct_example)
        self.assertEqual(correct_rendered, rendered,
                         'example engines rendered incorrectly')

    def test_correct_yaml_jinja(self):
        if _YAML and _JINJA2:
            rendered = yj_render_func(correct_yaml_jinja)
            self.assertEqual(correct_rendered, rendered,
                             'yaml-jinja engine rendered incorrectly')

    def test_empty_variable_definitions(self):
        rendered = example_render_func(empty_variable_definitions)
        self.assertEqual('document template\n', rendered,
                         'empty variable definitions failed')

    def test_empty_template(self):
        rendered = example_render_func(empty_template)
        self.assertEqual('', rendered, 'empty template rendered incorrectly')

    def test_no_section_separator(self):
        rendered = example_render_func(no_section_separator)
        err = 'dry doc with no section separator rendered incorrectly'
        self.assertEqual(rendered, no_section_separator, err)


class TestDryFileRender(unittest.TestCase):
    """Test file reading and writing"""

    def test_render_file(self):
        filepath = scriptdir + '/correct_drydoc.txt'
        dry_text = drydoc.read_file(filepath, encoding='utf-8')
        rendered = example_render_func(dry_text)

        self.assertEqual(rendered, correct_rendered,
                         'correct_drydoc.txt was rendered incorrectly')

    def test_write_file(self):
        filepath = scriptdir + '/test_drydoc.txt'
        rendered = example_render_func(correct_example)
        drydoc.write_file(rendered, filepath, encoding='utf-8')

        correct = filecmp.cmp(filepath, scriptdir + '/correct_rendered.txt')
        self.assertEqual(correct, True, 'written file was incorrect')

        os.remove(filepath)


class TestFunctions(unittest.TestCase):
    """Test templatefunctions"""

    def drydoc(self, docpath):
        filepath = os.path.join(scriptdir, '../drydoc.py')
        func = templatefunctions.template_system
        info = {'docdir': scriptdir}
        return func('python %s %s' % (filepath, docpath), info)

    def test_filevars(self):
        rendered = self.drydoc('filevars.txt')
        compare = b'1VAR' if _PY3 else '1VAR'
        self.assertEqual(rendered, compare, 'filevars failed')

    def test_include(self):
        rendered = self.drydoc('include.txt')
        compare = b'CONTENTCONTENT' if _PY3 else 'CONTENTCONTENT'
        self.assertEqual(rendered, compare, 'include failed')

    def test_system(self):
        rendered = self.drydoc('system.txt')
        compare = b'systemtest\n' if _PY3 else 'systemtest\n'
        self.assertEqual(rendered, compare, 'system function failed')

        # System calls should be executed in directory where document is
        # located
        filepath = os.path.join(scriptdir, 'dirA/pwd.txt')
        filedir = os.path.split(filepath)[0]

        rendered = self.drydoc('dirA/pwd.txt')
        if _PY3:
            rendered = rendered.decode('utf-8')
        self.assertEqual(rendered, filedir + '\n',
                         'system function failed pwd test')

    def test_specialcharpaths(self):
        rendered = self.drydoc('specialcharpaths/specialpath.txt')
        compare = b'12' if _PY3 else '12'
        self.assertEqual(rendered, compare,
                         'including path with special chars failed')


if __name__ == '__main__':
    unittest.main()
