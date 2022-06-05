htexpr: Templating for Dash
===========================

[![PyPI](https://img.shields.io/pypi/v/htexpr)](https://pypi.org/project/htexpr/)
[![MIT License](https://img.shields.io/pypi/l/htexpr?color=brightgreen)](https://github.com/jkseppan/htexpr/blob/master/LICENSE)
[![CircleCI](https://img.shields.io/circleci/build/github/jkseppan/htexpr)](https://circleci.com/gh/jkseppan/htexpr/tree/master)
[![Github CI](https://github.com/jkseppan/htexpr/workflows/CI/badge.svg)](https://github.com/jkseppan/htexpr/actions?query=workflow%3ACI)
[![Documentation Status](https://readthedocs.org/projects/htexpr/badge/?version=latest)](https://htexpr.readthedocs.io/en/latest/?badge=latest)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/)

`htexpr` compiles an html-like template syntax into Python
expressions, allowing embedded Python expressions in attributes and
content. It is inspired by [JSX]() and intended to complement the
excellent [Dash]() package, which allows you to write single-page
React apps in Python. For motivation and further instructions, see the
[documentation](https://htexpr.readthedocs.io/en/latest/).

[JSX]: https://reactjs.org/docs/introducing-jsx.html
[Dash]: https://dash.plot.ly

Example
-------

A Unicode table::

    import dash
    from dash import dcc, html, Input, Output, State
    
    from htexpr import compile
    import unicodedata

    app = dash.Dash()
    app.layout = compile("""
    <div>
      <table style={"margin": "0 auto"}>
        <tr><th>char</th><th>name</th><th>category</th></tr>
           [
             (<tr style={'background-color': '#eee' if line % 2 else '#ccc'}>
                <td>{ char }</td>
                <td>{ unicodedata.name(char, '???') }</td>
                <td>{ unicodedata.category(char) }</td>
              </tr>)
             for line, char in enumerate(chr(i) for i in range(32, 128))
           ]
      </table>
    </div>
    """).run()

    app.run_server(debug=True)

Further demonstrations:

* a larger [Unicode table](examples/unicode_table.py)
* a [Bootstrap example](examples/bootstrap.py)


Development status
------------------

I wrote this to help me with a particular project where I kept making
[bracketing mistakes](https://htexpr.readthedocs.io/en/latest/motivation.html).
The code works for that project, but there are likely to be corner
cases I haven't considered.

The Python grammar used here is quite simplistic: it recognizes
strings and variously parenthesized expressions. By understanding more
Python it would probably be possible to disambiguate between
comparison operators and tags, and thus drop the requirement to
enclose nested expressions in parentheses.

The error messages are not always helpful, and in particular the code
objects don't yet have reliable line-number data.
