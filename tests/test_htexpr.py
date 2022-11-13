#!/usr/bin/env python

"""Tests for `htexpr` package."""

import itertools
import pytest
import types

import parsimonious
from htexpr.htexpr import (
    parse,
    simplify,
    to_ast,
    wrap_ast,
    compile,
    HtexprError,
    SimplifyVisitor,
    _flatten,
    _grammar,
)
from htexpr import mappings


def test_grammar():
    tree = simplify(parse('<h1 id="foo" class={bar}>heading {foo}<div id="1" class="2"/></h1>'))
    assert tree == {
        "element": {
            "tag": "h1",
            "attrs": [("id", ("literal", "foo")), ("class", ("python", [("bar", None)]))],
        },
        "content": [
            ("literal", "heading "),
            ("python", [("foo", None)]),
            {
                "element": {
                    "tag": "div",
                    "attrs": [("id", ("literal", "1")), ("class", ("literal", "2"))],
                },
                "content": None,
                "start": 38,
            },
        ],
        "start": 0,
    }


@pytest.mark.parametrize(
    "html",
    [
        '<div id="asdf" />',
        "<span class='qwerty'></span>",
        '<div><div id="asdf" /></div>',
        '<div id={"asdf"} />',
        '<div id="}" />',
        '<div id={1+2+3<">"+4>5} />',
        "<ul>[1, 2, 3]</ul>",
    ],
)
def test_grammar_examples(html):
    simplify(parse(html))


@pytest.mark.parametrize(
    "html",
    [
        "{}",
        "foo",
        '<div id="asdf} />',
        '<div><div id="asdf" /></span>',
        '<div id={"asdf}" />',
        '<div id={1+2+3<">"}+4>5} />',
        "<ul>[1, 2, 3]",
    ],
)
def test_grammar_nonexamples(html):
    with pytest.raises(HtexprError):
        simplify(parse(html))


def _walk(tree, path):
    for idx, name in path:
        tree = tree.children[idx]
        assert tree.expr_name == name
    return tree


@pytest.mark.parametrize(
    "code,result",
    [
        ("1 if 2 < 3 else 4 > 5", [("1 if 2 < 3 else 4 > 5", None)]),
        (
            "(<span />) if 2 < 3 else (<naps />)",
            [("(<span />)", "span"), (" if 2 < 3 else ", None), ("(<naps />)", "naps")],
        ),
        (
            "1 + 2 + (<div />) + (<span />)",
            [("1 + 2 + ", None), ("(<div />)", "div"), (" + ", None), ("(<span />)", "span")],
        ),
        ("(<div>{(<span/>)}</div>)", [("(<div>{(<span/>)}</div>)", "div")]),
    ],
)
def test_nesting(code, result):
    tree = parse(f"<div>{{{code}}}</div>")
    expr = _walk(
        tree,
        [
            (1, "element"),
            (0, "elt_nonempty"),
            (1, "content"),
            (0, "content1"),
            (0, "content_python"),
            (1, "python_expr"),
        ],
    )

    visitor = SimplifyVisitor()
    visitor.visit(tree)
    interposed = visitor.get_interposed(expr)
    for (text0, subtree), (text1, elem_name) in itertools.zip_longest(interposed, result):
        assert text0 == text1
        if subtree is None:
            assert elem_name is None
        else:
            assert subtree["element"]["tag"] == elem_name


def H1(**kwargs):
    return {**kwargs, "tag": "H1"}


def Div(**kwargs):
    return {**kwargs, "tag": "Div"}


def Span(**kwargs):
    return {**kwargs, "tag": "Span"}


@pytest.mark.parametrize(
    "html,result",
    [
        pytest.param(
            '<h1 id="header">{foo*bar}</h1>',
            {"tag": "H1", "id": "header", "children": ["oneone"]},
            id="foo*bar",
        ),
        pytest.param(
            """
             <div class="c">
              <span id={foo} class="foo">
                10x: { "x" * 10 }
              </span>
            </div>
        """,
            {
                "tag": "Div",
                "className": "c",
                "children": [
                    {
                        "tag": "Span",
                        "id": "one",
                        "className": "foo",
                        "children": ["10x: ", "xxxxxxxxxx"],
                    }
                ],
            },
            id="div-span",
        ),
        pytest.param(
            "<div>[ Span(x=i) for i in range(3) ]</div>",
            {
                "tag": "Div",
                "children": [
                    {"tag": "Span", "x": 0},
                    {"tag": "Span", "x": 1},
                    {"tag": "Span", "x": 2},
                ],
            },
            id="python-list",
        ),
        pytest.param(
            "<div>{(<span id={'spam'}/>)}</div>",
            {"tag": "Div", "children": [{"tag": "Span", "id": "spam", "children": []}]},
            id="nested-python",
        ),
        pytest.param(
            """<div>[ (<span x={i} />) if i%2==0 else (<h1 x={i} />)
                      for i in range(3) ]</div>""",
            {
                "tag": "Div",
                "children": [
                    {"children": [], "tag": "Span", "x": 0},
                    {"children": [], "tag": "H1", "x": 1},
                    {"children": [], "tag": "Span", "x": 2},
                ],
            },
            id="nested-two",
        ),
        pytest.param(
            "<div>{(<span>one {(<h1>two</h1>) or 1/0} three</span>)}</div>",
            {
                "tag": "Div",
                "children": [
                    {
                        "tag": "Span",
                        "children": ["one ", {"tag": "H1", "children": ["two"]}, " three"],
                    }
                ],
            },
            id="nested-deep",
        ),
        pytest.param(
            "<div a1={[i**2 for i in range(3)]} a2=[i**2 for i in range(3)] />",
            {"tag": "Div", "a1": [0, 1, 4], "a2": [0, 1, 4], "children": []},
            id="attribute-lists",
        ),
        pytest.param(
            "<div a1={{'a': 1, 'b': 2}} a2={'a': 1, 'b': 2} />",
            {"tag": "Div", "a1": {"a": 1, "b": 2}, "a2": {"a": 1, "b": 2}, "children": []},
            id="attribute-dicts",
        ),
        pytest.param(
            """
                <div>{
                  (<span />)
                }</div>
            """,
            {"tag": "Div", "children": [{"tag": "Span", "children": []}]},
            id="issue-2",
        ),
    ],
)
def test_compile(html, result):
    foo = "one"
    bar = 2

    def map_tag(tag):
        return None, tag.title()

    assert result == compile(html, map_tag=map_tag).eval(
        {**globals(), "foo": "one", "bar": 2, "map_tag": map_tag}
    )


def test_bindings():
    def Div(children):
        return {"div": children}

    def Span(children):
        return {"span": children}

    html = types.SimpleNamespace()
    html.Div = Div
    html.Span = Span

    expr = compile("<div>[(<span>{i}</span>) for i in range(10) if i not in removed]</div>")

    with pytest.raises(NameError):
        expr.run()

    assert expr.run(removed={0, 1, 2, 3, 5, 6, 7, 9}) == {"div": [{"span": [4]}, {"span": [8]}]}


def test_map_tag():
    def map_tag(tag):
        if tag == "a":
            return None, "tag_anchor"
        elif tag == "b":
            return "Html", "tag_bold"

    def tag_anchor(**kwargs):
        return "Anchor", kwargs

    class Html:
        @staticmethod
        def tag_bold(**kwargs):
            return "Bold", kwargs

    assert compile('<a foo="bar"><b>x</b></a>', map_tag=map_tag).run() == (
        "Anchor",
        {"foo": "bar", "children": [("Bold", {"children": ["x"]})]},
    )


def test_mappings_lookup():
    lookup = mappings._lookup
    # default mapping
    dft = mappings.default
    assert lookup("a", dft) == ("html", "A")
    assert lookup("Nav", dft) == ("html", "Nav")
    assert lookup("CENTER", dft) == ("html", "Center")
    assert lookup("object", dft) == ("html", "ObjectEl")
    assert lookup("DatePickerSingle", dft) == ("dcc", "DatePickerSingle")
    assert lookup("DataTable", dft) == ("dash_table", "DataTable")
    with pytest.raises(HtexprError):
        lookup("no-such-element", dft)

    # mapping with bootstrap components
    dbc = mappings.dbc_and_default
    assert lookup("a", dbc) == ("html", "A")
    assert lookup("Nav", dbc) == ("dbc", "Nav")
    assert lookup("nav", dbc) == ("html", "Nav")

    # single callable as mapping
    def foo(tag):
        return "foo", tag

    assert lookup("xyzzy", foo) == ("foo", "xyzzy")

    # callables and dicts together
    def bar(tag):
        if "bar" in tag:
            return "bar", tag

    d = {"foo": ("foo", "xyzzy")}
    assert lookup("foo", (bar, d)) == ("foo", "xyzzy")
    assert lookup("baric", (bar, d)) == ("bar", "baric")
    with pytest.raises(HtexprError):
        lookup("none", (bar, d))
    assert lookup("foo", (d, bar)) == ("foo", "xyzzy")
    assert lookup("baric", (d, bar)) == ("bar", "baric")

    # vary the module names
    map = (mappings.html("H"), mappings.dcc("C"))
    assert lookup("a", map) == ("H", "A")
    assert lookup("object", map) == ("H", "ObjectEl")
    assert lookup("DatePickerSingle", map) == ("C", "DatePickerSingle")


def test_to_ast_errors():
    with pytest.raises(HtexprError):
        to_ast(("foobar", 123))
    with pytest.raises(HtexprError):
        to_ast(object())


def _dfs_ast(node, name=None, depth=0):
    if depth > 30:
        return "..."
    print(f"DFS {node}")
    prefix = "" if name is None else f"{name}="
    if isinstance(node, list):
        return f'{prefix}[{",".join(_dfs_ast(kid, None, depth+1) for kid in node)}]'
    elif isinstance(node, (int, str)):
        return f"{prefix}{node}"
    else:
        useless = {"col_offset", "lineno", "end_col_offset", "end_lineno", "ctx"}
        args = ",".join(
            _dfs_ast(getattr(node, kid), kid, depth + 1)
            for kid in sorted(dir(node))
            if not (kid.startswith("_") or kid in useless)
        )
        return f"{prefix}{type(node).__name__}({args})"


@pytest.mark.parametrize(
    "input,output",
    [
        ([], "List(elts=[])"),
        ([("scalar", 1)], "List(elts=[1])"),
        ([("scalar", 1), ("scalar", 2)], "List(elts=[1,2])"),
        ([("list", "expr")], "expr"),
        ([("list", "expr1"), ("list", "expr2")], "BinOp(left=expr1,op=Add(),right=expr2)"),
        (
            [("list", "expr1"), ("list", "expr2"), ("list", "expr3")],
            "BinOp(left=BinOp(left=expr1,op=Add(),right=expr2),op=Add(),right=expr3)",
        ),
        ([("scalar", "v"), ("list", "expr")], "BinOp(left=List(elts=[v]),op=Add(),right=expr)"),
        ([("list", "expr"), ("scalar", "v")], "BinOp(left=expr,op=Add(),right=List(elts=[v]))"),
        (
            [("scalar", "v"), ("list", "expr1"), ("list", "expr2")],
            "BinOp(left=List(elts=[v]),op=Add(),right=BinOp(left=expr1,op=Add(),right=expr2))",
        ),
        (
            [("list", "expr1"), ("scalar", "v"), ("list", "expr2")],
            "BinOp(left=BinOp(left=expr1,op=Add(),right=List(elts=[v])),op=Add(),right=expr2)",
        ),
        (
            [("list", "expr1"), ("list", "expr2"), ("scalar", "v")],
            "BinOp(left=BinOp(left=expr1,op=Add(),right=expr2),op=Add(),right=List(elts=[v]))",
        ),
        ([("list", "abc"), ("list", "de")], "BinOp(left=abc,op=Add(),right=de)"),
    ],
)
def test_flatten(input, output):
    result = _flatten(input)
    print(result)
    print(_dfs_ast(result))
    assert _dfs_ast(result) == output
