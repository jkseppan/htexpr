Details
=======

Configuration
-------------

The preceding discussion assumes you import Dash
packages under the usual names::

    from dash import html, dcc
    from dash import table as dash_table

If this does not match your preferences, you can customize the
mappings used by htexpr::

    from dash import html as H
    from dash import dcc as C

    import htexpr
    from htexpr import mappings

    tags = [mappings.html('H'), mappings.dcc('C')]

    def compile(code):
        return htexpr.compile(code, map_tag=tags)

There is a prebuilt configuration for `Dash Bootstrap components`_::

    from dash import html, dcc
    import dash_bootstrap_components as dbc
    import htexpr
    from htexpr import mappings

    def compile(code):
        return htexpr.compile(code, map_tag=mappings.dbc_and_default)

    layout = compile("""
        <Container class="p-5"><Alert>Hello Bootstrap!</Alert></Container>
    """).run()

The Bootstrap components shadow some HTML components, but there is a
trick to work around this: if you need to use an HTML component, just
use upper/lowercase letters differently from the Bootstrap components. ::

    compile("""
      <div>
        <Label>this is a Bootstrap label</Label>
        <label>this is an HTML label</label>
      </div>
    """)


.. _`Dash Bootstrap components`: https://dash-bootstrap-components.opensource.faculty.ai



Htexpr objects
--------------

The ``compile`` function returns an ``Htexpr`` object, which
encapsulates the Python code resulting from the compilation. This
object needs to be evaluated to result in actual Dash objects. Because
the Python code refers to various objects (such as imported modules,
functions, and variables) these need to be passed in::

    from dash import html
    htexpr.compile(
        "<div>[(<span>{i}</span>) for i in range(10) if i not in removed]</div>"
    ).eval({**globals(), "removed": {1, 2, 3}})

The compiled code is able to refer to ``html.Div`` because ``html``
occurs in ``globals()``, and to the ``removed`` variable because it is
included in the bindings manually. Similarly, local variables can be
included with ``**locals()``.

Including ``**globals()`` and ``**locals()`` every time gets tedious,
so there is a small magic trick to do it automatically::

    from dash import html
    htexpr.compile(
        "<div>[(<span>{i}</span>) for i in range(10) if i not in removed]</div>"
    ).run(removed={1, 2, 3})

The ``run`` method peeks into the caller's frame and automatically
includes all the global and local bindings. Any keyword arguments are
added on top of these.

Peeking into frames is discouraged by some Python developers and
involves calling a private function, so the ``eval`` method is
recommended for anyone who is worried.
