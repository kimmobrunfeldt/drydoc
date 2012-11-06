"""
New custom templatefunctions should be added in this module.
"""

# Todo: this module seems kind of hacky?

# Warning: All imported modules will be accessible from templates!
import os
import sys
import subprocess
import drydoc


def system(cmd, info):
    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT
    docdir = info['drydocdir']
    # Set working directory where the document is located
    output = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=PIPE,
                              shell=True, cwd=docdir)
    return output.communicate()[0]


def filevars(path, info):
    docdir = info['drydocdir']
    filepath = os.path.abspath(os.path.join(docdir, path))
    contents = drydoc.read_file(filepath, encoding=info['encoding'])
    doc = drydoc.DryDoc(contents)
    return doc.get_variables()


def include(path, info, render):
    docdir = info['drydocdir']
    filepath = os.path.abspath(os.path.join(docdir, path))
    contents = drydoc.read_file(filepath)
    if not render:
        return contents
    doc = drydoc.DryDoc(contents)

    # Copy info dictionary to prevent next templates to change
    # document's location. Create new include function to be given to
    # next template
    newinfo = info.copy()
    f = lambda path, render=True: include(path, newinfo, render=render)
    newinfo['template_vars']['include'] = f

    # Update document's location to next template
    newdir = os.path.split(filepath)[0]
    newinfo['drydocdir'] = newdir

    return doc.render(add_vars=newinfo['template_vars'])


def get_funcs(info):
    """Returns all functions that are callable from jinja templates in
    dict format. info is additional info to template functions provided from
    main program.
    """
    d = {}
    # Evilly add all global functions to be used in templates
    d.update(globals())
    d.update(globals()['__builtins__'])

    d['filevars'] = lambda path: filevars(path, info)
    d['include'] = lambda path, render=True: include(path, info, render=render)
    d['system'] = lambda cmd: system(cmd, info)

    return d
