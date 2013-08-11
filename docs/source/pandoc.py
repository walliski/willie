"""Pandoc extension for Sphinx

This allows you to write your docstrings in whatever markup you want, as long
as pandoc supports it. Markdown is used by default; use the pandoc_use_parser
config value to change it to something else.
"""

import pypandoc

def setup(app):
    app.add_config_value('pandoc_use_parser', 'markdown', True)
    app.connect('autodoc-process-docstring', pandoc_process)

def pandoc_process(app, what, name, obj, options, lines):
    input_format = app.config.pandoc_use_parser
    for i in xrange(len(lines)):
        print lines[i]
        line = lines[i].encode('utf-8')
        lines[i] = unicode(pypandoc.convert(line, 'rst', format=input_format),
                           encoding='utf-8')
