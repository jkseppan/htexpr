import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from htexpr import compile
from htexpr.mappings import dbc_and_default

from toolz import curry

compile = curry(compile)(map_tag=dbc_and_default)

navbar = compile("""
<NavbarSimple brand="Demo" brand_href="#" sticky="top">
  <NavItem><NavLink href="#">Link</NavLink></NavItem>
  <DropdownMenu nav={True} in_navbar={True} label="Menu">
    <DropdownMenuItem>Entry 1</DropdownMenuItem>
    <DropdownMenuItem>Entry 2</DropdownMenuItem>
    <DropdownMenuItem divider={True} />
    <DropdownMenuItem>Entry 3</DropdownMenuItem>
  </DropdownMenu>
</NavbarSimple>
""")

body = compile("""
<Container class="mt-4">
  <Row>
    <Col>
      <Alert color="primary" dismissable={True}>alert, alert, alert, alert</Alert>
      <Button color="primary" class="my-2 mx-1" >Button!</Button>
      <Button color="secondary" class="my-2 mx-1" >Button!</Button>
      <Button color="danger" class="my-2 mx-1" >Button!</Button>
      <Card style={'width': '24rem'} class="mx-auto my-4">
        <CardImg src="https://source.unsplash.com/random/400x300" top={True} />
        <CardBody>
          <h4 class="card-title">Random photo</h4>
          <p class="card-text">This is a random photo from Unsplash,
             the treasure trove of freely useable images.</p>
        </CardBody>
      </Card>
    </Col>
    <Col>
      <h2>Digits of \u03C0</h2>
      <Graph figure={"data": [{"x": list(range(10)),
                               "y": [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]}]} />
    </Col>
  </Row>
</Container>
""")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([navbar.run(), body.run()])

if __name__ == "__main__":
    app.run_server(debug=True)
