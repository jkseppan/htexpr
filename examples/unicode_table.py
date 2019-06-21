import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from htexpr import compile
import unicodedata

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/jkseppan/pen/qwBNGp.css'])
app.layout = compile("""
<div>
  <h1>Unicode table</h1>
  <div id="inputs">
     <label for="from">From</label>
     <Input id="from" value="128500" type="number" />
     <label for="to">to</label>
     <Input id="to" value="129000" type="number" />
     <label for="step">by steps of</label>
     <Input id="step" value="3" type="number" />
  </div>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Char</th>
        <th            >Number</th>
        <th rowspan="2">Name</th>
        <th rowspan="2">Category</th>
        <th rowspan="2">Bidirectional</th>
      </tr>
      <tr>
        <th class="rt">(Hexadecimal)</th>
      </tr>
    </thead>
    <tbody id="body">
    </tbody>
  </table>
</div>
""").run()

row1 = compile("""
<tr>
  <td rowspan="2">{ chr(i) }</td>
  <td>{ i }</td>
  <td rowspan="2">{ unicodedata.name(chr(i), '???') }</td>
  <td rowspan="2">{ unicodedata.category(chr(i)) }</td>
  <td rowspan="2">{ unicodedata.bidirectional(chr(i)) }</td>
</tr>
""")

row2 = compile("""
<tr>
  <td class="rt fw">U+{ f'{i:04x}' }</td>
</tr>
""")

def parseint(x):
    try:
        return max(0, int(x))
    except ValueError:
        return 0

@app.callback(
    Output("body", "children"),
    [Input("from", "value"), Input("to", "value"), Input("step", "value")]
)
def update_table(from_, to, step):
    from_ = parseint(from_)
    to = parseint(to)
    step = max(1, parseint(step))
    return [row
            for pair in [(row1.run(), row2.run()) for i in range(from_, to+1, step)]
            for row in pair]

@app.callback(
    Output("to", "value"),
    [Input("from", "value")],
    [State("to", "value")]
)
def update_to(from_, to):
    return max(parseint(from_), int(to))


# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
