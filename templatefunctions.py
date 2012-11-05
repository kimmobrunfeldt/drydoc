

import drydoc


def filevars(path, info):
    variable_engine = info['variable_engine']
    encoding = info['encoding']
    docdir = info['drydocdir']
    return drydoc.variables_from_file(path, docdir, variable_engine,
                                      encoding=encoding)


def include(path, info):
    contents = drydoc.read_file(path)
    add_vars = info['template_variables']
    rendered = drydoc.render_dry_text(contents, info['variable_engine'],
                                      info['template_engine'],
                                      add_variables=add_vars)

    return rendered


def get_all(info):
    # All functions that are callable from jinja templates
    d = {}
    d['filevars'] = lambda path: filevars(path, info)
    d['include'] = lambda path: include(path, info)
    return d
