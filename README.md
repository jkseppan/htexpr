htexpr
======

[![PyPI](https://img.shields.io/pypi/v/htexpr)](https://pypi.org/project/htexpr/)
[![MIT License](https://img.shields.io/pypi/l/htexpr?color=brightgreen)](https://github.com/jkseppan/htexpr/blob/master/LICENSE)
[![CircleCI](https://img.shields.io/circleci/build/github/jkseppan/htexpr)](https://circleci.com/gh/jkseppan/htexpr/tree/master)
[![Github CI](https://github.com/jkseppan/htexpr/workflows/CI/badge.svg)](https://github.com/jkseppan/htexpr/actions?query=workflow%3ACI)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/)

htexpr compiles an html-like syntax into Python expressions. It is
inspired by [JSX]() and intended to complement the excellent [dash]()
package, which allows you to write single-page React apps in
Python. For motivation and further instructions, see the
[documentation](https://htexpr.readthedocs.io/en/latest/).

[JSX]: https://reactjs.org/docs/introducing-jsx.html
[dash]: https://dash.plot.ly

Example
-------

A Unicode table::

    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dependencies import Input, Output, State

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
the kind of bracketing mistakes exhibited above. The code works for
that purpose, but there are likely to be corner cases I haven't
considered.

The Python grammar used here is quite simplistic: it recognizes
strings and variously parenthesized expressions. By understanding more
Python it would probably be possible to disambiguate between
comparison operators and tags, and thus drop the requirement to
enclose nested expressions in parentheses.

The error messages are not always helpful, and in particular the code
objects don't yet have reliable line-number data.
