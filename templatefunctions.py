"""
New custom templatefunctions should be added in this module.
Prefix template functions with 'template_'. It is used to detect template
functions. Funtions are callable from templates without the prefix.
"""

# Todo: This module seems kind of hacky? Maybe modifying Jinja2 instead of
#       passing template functions as environment variables would be better.
# On the other hand, this way jinja2.Template class doesn't have to be
# modified roughly.

# Warning: All imported modules will be accessible from templates!
import os
import sys
import subprocess
import drydoc


func_prefix = 'template_'


def assign_kwargs(func, **new_kwargs):
    """Create wrapper funcion for func, which modifies kwargs to be passed
    to func based on what new_kwargs contains.
    """
    def new_func(*args, **kwargs):
        for key, value in new_kwargs.items():
            if key not in kwargs:
                kwargs[key] = value
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    return new_func


def template_system(cmd, info=None):
    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT
    docdir = info['docdir']
    # Set working directory where the document is located
    output = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=PIPE,
                              shell=True, cwd=docdir)
    return output.communicate()[0]


def template_filevars(path, info=None):
    docdir = info['docdir']
    filepath = os.path.abspath(os.path.join(docdir, path))
    contents = drydoc.read_file(filepath, encoding=info['encoding'])
    doc = drydoc.DryDoc(contents)
    return doc.get_variables()


def template_include(path, render=True, info=None):
    """Returns document in path. path is relative to the document where
    include is called. By default, document is rendered as DRY doc.
    """
    docdir = info['docdir']
    filepath = os.path.abspath(os.path.join(docdir, path))

    contents = drydoc.read_file(filepath)
    if not render:
        return contents
    doc = drydoc.DryDoc(contents)

    # Copy info dictionary to prevent next templates to change
    # data in it. Each document gets their own info dictionary.
    newinfo = info.copy()

    # Update document's location to next template
    newdir = os.path.split(filepath)[0]
    newinfo['docdir'] = newdir

    # Create new template functions and pass newinfo which contains the
    # new docdir to them
    newfuncs = {}
    for name, func in info['template_funcs'].items():
        funcname = getattr(func, '__name__', None)

        # Assign newinfo to all template functions
        if funcname is not None and func.__name__.startswith(func_prefix):
            newfunc = assign_kwargs(func, info=newinfo)
            newfunc.__name__ = func.__name__
            newname = func.__name__[len(func_prefix):]
            newfuncs[newname] = newfunc
        else:
            newfuncs[name] = func

    newinfo['template_funcs'] = newfuncs
    env = newinfo['template_env']
    env.update(newfuncs)
    return doc.render(env=env)


def get_funcs(info):
    """Returns all functions that are callable from jinja templates in
    dict format. info is additional info to template functions provided from
    main program.
    """
    d = {}
    # Evilly add all global functions to be used in templates
    d.update(globals())
    d.update(globals()['__builtins__'])

    # Add all functions from this module which start with func_prefix.
    funcs = []
    for name in dir(sys.modules[__name__]):
        if name.startswith(func_prefix):
            funcs.append(globals()[name])

    for func in funcs:
        newfunc = assign_kwargs(func, info=info)
        newfunc.__name__ = func.__name__
        newname = func.__name__[len(func_prefix):]
        d[newname] = newfunc

    return d
