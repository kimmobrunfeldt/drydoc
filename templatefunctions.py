"""
New custom templatefunctions should be added in this module.
"""

import os
import subprocess
import drydoc


def system(cmd, info):
    PIPE = subprocess.PIPE
    output = subprocess.Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True)
    return output.communicate()[0]


def filevars(path, info):
    docdir = info['drydocdir']
    filepath = os.path.abspath(os.path.join(docdir, path))
    contents = drydoc.read_file(filepath, encoding=info['encoding'])
    doc = drydoc.DryDoc(contents)
    return doc.get_variables()


def include(path, info):
    contents = drydoc.read_file(path)
    doc = drydoc.DryDoc(contents)
    return doc.render(add_vars=info['template_vars'])


def get_funcs(info):
    """Returns all functions that are callable from jinja templates in
    dict format. info is additional info to template functions provided from
    main program.
    """
    d = {}
    d['filevars'] = lambda path: filevars(path, info)
    d['include'] = lambda path: include(path, info)
    d['system'] = lambda cmd: system(cmd, info)
    return d
