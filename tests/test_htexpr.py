#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `htexpr` package."""

import itertools
import pytest

import parsimonious
from htexpr.htexpr import (
    parse,
    simplify,
    to_ast,
    wrap_ast,
    convert,
    HtexprError,
    SimplifyVisitor,
    _map_tag_dash,
    _flatten,
    _grammar,
)


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
    ],
)
def test_convert(html, result):
    foo = "one"
    bar = 2

    def map_tag(tag):
        return None, tag.title()

    assert result == eval(convert(html, map_tag=map_tag))


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

    assert eval(convert('<a foo="bar"><b>x</b></a>', map_tag=map_tag)) == (
        "Anchor",
        {"foo": "bar", "children": [("Bold", {"children": ["x"]})]},
    )


def test_map_tag_dash():
    assert _map_tag_dash("a") == ("html", "A")
    assert _map_tag_dash("CENTER") == ("html", "Center")
    assert _map_tag_dash("object") == ("html", "ObjectEl")
    assert _map_tag_dash("DatePickerSingle") == ("dcc", "DatePickerSingle")
    assert _map_tag_dash("DataTable") == ("dash_table", "DataTable")
    with pytest.raises(HtexprError):
        _map_tag_dash("no-such-element")


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
        useless = {"col_offset", "lineno", "ctx"}
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
