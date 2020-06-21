Motivation
==========

`Dash`_ is an excellent way to build React-powered single-page apps in
Python. When building some dashboards, I found myself making a lot of
mistakes [#]_ like this::

    app.layout = html.Div([
        html.Table(style={"margin": "0 auto"}, children=[
               html.Tr(html.Th("char"), html.Th("name"), html.Th("category"))
           ] + [
               html.Tr(
                   [html.Td(char),
                    html.Td(unicodedata.name(char, '???')),
                    html.Td(unicodedata.category(char))],
                  style={'background-color': '#eee' if line % 2 else '#ccc'}
               )
              for line, char in enumerate(chr(i) for i in range(32, 128))
           ])
    ])

An obvious idea would be to use a templating language such as Jinja::

   <div>
      <table style="margin: 0 auto;">
        <tr><th>char</th><th>name</th><th>category</th></tr>
            {% for i in range(32, 128) %}
            <tr style="background-color: {{ loop.cycle('#eee', '#ccc') }}">
                <td>{ i | chr }</td>
                <td>{ i | getname }</td>
                <td>{ i | getcategory }</td>
            </tr>
            {% endfor %}
      </table>
   </div>

assuming suitable filters for the Unicode lookups. But this doesn't
work with Dash, because Jinja produces HTML while Dash builds a React
app from the component tree.

The htexpr package allows a similar syntax, with embedded Python for
templating but a Dash component tree as the output::

    app.layout = htexpr.compile("""
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


.. _`Dash`: https://dash.plot.ly

.. [#] The ``Th`` calls within ``Tr`` should have been enclosed in a list,
       but without that list one of the ``Th`` objects was interpreted
       as the element ID, leading to ::

           File ".../dash/development/base_component.py", line 244, in _traverse_with_paths
               "(id={:s})".format(i.id)
           TypeError: unsupported format string passed to Th.__format__
