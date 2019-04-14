htexpr
======

htexpr compiles an html-like syntax into Python expressions. It is
inspired by [JSX]() and intended to complement the excellent [dash]()
package, which allows you to write single-page React apps in
Python. Here is an example, a simple ASCII table:

```python
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
```

Compare this to a similar implementation using function calls:

```python
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
```

The latter has a small mistake that is in my opinion easy to make by
accident, but is completely avoided in the htexpr syntax.

A somewhat more complicated [Unicode table]() example
demonstrates the syntax further.

[JSX]: https://reactjs.org/docs/introducing-jsx.html
[dash]: https://dash.plot.ly
[Unicode table]: https://github.com/jkseppan/htexpr/blob/master/examples/unicode_table.py


API
---

Use the following imports:

```python
import dash_core_components as dcc
import dash_html_components as html
import dash_table
```

Then call `htexpr.compile` with an expression, and elements such as

    <div class="c"><Input id="i" type="number" /></div>

will be transformed into Python function calls:

    html.Div(className="c", children=[
	    dcc.Input(id="i", type="number", children=[])
	])

`html` tags can be written in any case, `dcc` tags must be in the
exact same case as the function name. The `class` attribute becomes
`className` and some other lower-case attributes such as `rowspan` are
transformed into camel-case (`rowSpan`). The `map_tag` and
`map_attribute` keyword arguments override these defaults.

The expression must be evaluated with its `eval` method to be
effective, with suitable bindings for all variables referenced
(including imports of `dash_html_components as html`, etc.)  A
convenience method that captures the globals and locals in the calling
environment is `run`.


Syntax
------

All tags must be closed: `<div>...</div>` or `<div />`. Literal
attribute values must appear in quotes and Python values in brackets
`[]` or braces `{}`. Text inside elements can also include Python
expressions in brackets or braces.

Braces may contain any Python expression, but the braces are not
included in the expression; however, if there is a colon at the top
level of an expression appearing as an attribute value, the braces are
included. This allows specifying dictionary-valued attributes with a
single level of braces at the cost of misparsing type annotations.
Brackets are included in the expression, so they always specify a list
value. A bracketed expression is spliced into the list of children of
the parent element, so

    <ul>
	  <li> Item Zero </li>
	  [(<li> Item {i} </li>) for i in range(1,10)]
	  <li> Item Ten </li>
    </ul>

results in a single flat list of eleven elements as the children of
the `ul` element. This splicing is triggered solely by the bracket
syntax, so a list-valued expression inside braces does not get the
splicing treatment.

The htexpr syntax can appear nested inside Python expressions, but the
subexpression must be surrounded in parentheses: `(<li>...</li>)`.


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

Since the library creates code objects using the `ast` module, it is
likely quite dependent on the CPython implementation. I haven't looked
how much work it would be to work with the other Python
implementations.

