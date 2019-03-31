# -*- coding: utf-8 -*-

"Parse HTML with embedded Python expressions into Python code objects"

from parsimonious.grammar import Grammar, NodeVisitor
from parsimonious import exceptions as pe
import ast
from toolz import pipe, partial, first
from functools import reduce
import itertools as it
import random
import builtins


class HtexprError(Exception):
    pass


def compile(html, *, map_tag=None, map_attribute=None):
    return pipe(
        html,
        parse,
        simplify,
        partial(to_ast, map_tag=map_tag, map_attribute=map_attribute),
        wrap_ast,
        ast.fix_missing_locations,
        partial(builtins.compile, filename="<unknown>", mode="eval"),
    )


_grammar = Grammar(
    r"""
    document            = _ element _
    _                   = ~'[ \t\n]*'
    element             = elt_empty / elt_nonempty
    elt_nonempty        = tag_open content tag_close
    tag_open            = langle tag_name attributes rangle _
    tag_close           = _ lclose tag_name rangle
    elt_empty           = langle tag_name attributes rclose
    langle              = ~r"\s*<\s*"
    rangle              = ~r"\s*>\s*"
    lclose              = ~r"\s*</\s*"
    rclose              = ~r"\s*/>\s*"
    attributes          = attr*
    attr                = _ attr_name _ '=' _ attr_value
    tag_name            = ~"[a-z][a-z0-9._-]*"i
    attr_name           = ~"[a-z][a-z0-9._-]*"i
    attr_value          = attr_value_literal / attr_value_pydict / attr_value_python / attr_value_pylist
    attr_value_literal  = ~'"[^"]*"|\'[^\']*\''
    attr_value_pydict   = lbrace python_expr_nocolon ':' python_expr rbrace
    attr_value_python   = lbrace python_expr rbrace
    attr_value_pylist   = lbracket python_expr rbracket
    content             = content1*
    content1            = content_python / content_pylist / element / text
    content_python      = lbrace python_expr rbrace
    content_pylist      = lbracket python_expr rbracket
    lbrace              = ~r"{\s*"
    rbrace              = ~r"\s*}"
    lbracket            = ~r"[\[]\s*"
    rbracket            = ~r"\s*]"
    text                = ~r'[^<{\[]+'
    python_expr         = (double3_str / single3_str / double_str / single_str / nested / parens / braces / brackets / other)*
    python_expr_nocolon = (double3_str / single3_str / double_str / single_str / nested / parens / braces / brackets / nocolon)*
    double3_str         = '"\""' ~r'([^"]|"[^"]|""[^"])*' '"\""'
    single3_str         = "'''"  ~r"([^']|'[^']|''[^'])*" "'''"
    double_str          = '"' ~r'([^"\\]|\\.)*' '"'
    single_str          = "'" ~r"([^'\\]|\\.)*" "'"
    nested              = ~r"\(\s*" element ")"
    parens              = "(" python_expr ")"
    braces              = "{" python_expr "}"
    brackets            = "[" python_expr "]"
    other               = ~'[^][(){}"\']+'
    nocolon             = ~'[^][(){}"\':]+'
    """
)


def parse(html):
    try:
        return _grammar.parse(html)
    except pe.ParseError as e:
        raise HtexprError(e)


class SimplifyVisitor(NodeVisitor):
    __slots__ = ("nested",)
    visit_element = visit_content1 = NodeVisitor.lift_child
    unwrapped_exceptions = (HtexprError,)

    def __init__(self):
        self.nested = []

    def generic_visit(self, node, children):
        return node

    def visit_document(self, node, children):
        _, elt, _ = children
        return elt

    def visit__(self, node, children):
        return None

    def visit_elt_empty(self, node, children):
        _, tag, attrs, _ = children
        return {"element": {"tag": tag, "attrs": attrs}, "content": None, "start": node.start}

    def visit_elt_nonempty(self, node, children):
        (tag_open, attrs), content, tag_close = children
        if tag_open != tag_close:
            raise HtexprError(f"<{tag_open}> closed by </{tag_close}>")
        if content and isinstance(content[-1], tuple) and content[-1][0] == "literal":
            stripped = content[-1][1].rstrip()
            if stripped:
                content[-1] = ("literal", stripped)
            else:
                del content[-1]
        return {
            "element": {"tag": tag_open, "attrs": attrs},
            "content": content,
            "start": node.start,
        }

    def visit_tag_open(self, node, children):
        _, tag_name, attrs, _, _, = children
        return tag_name, attrs

    def visit_tag_close(self, node, children):
        _, _, tag_name, _ = children
        return tag_name

    def visit_tag_name(self, node, children):
        return node.text

    visit_attr_name = visit_tag_name

    def visit_attributes(self, node, children):
        return children

    def visit_attr(self, node, children):
        _, name, _, _, _, value = children
        return name, value

    def visit_attr_value(self, node, children):
        return children[0]

    def visit_attr_value_literal(self, node, children):
        return "literal", node.text[1:-1]

    def visit_attr_value_pydict(self, node, children):
        _, python1, _, python2, _ = children
        return "python", [(f"{{{python1.text}:{python2.text}}}", None)]

    def visit_attr_value_python(self, node, children):
        _, python, _ = children
        return "python", [(python.text, None)]

    def visit_attr_value_pylist(self, node, children):
        _, python, _ = children
        return "pylist", [(python.text, None)]

    def visit_content(self, node, children):
        return children

    def get_nested(self, node):
        minimum = node.start
        for (start, end, element) in sorted(self.nested):
            if start < minimum:
                continue
            if start >= node.end:
                break
            yield start, end, element
            minimum = end

    def get_interposed(self, node):
        point = node.start
        for (start, end, element) in self.get_nested(node):
            if start > point:
                yield node.full_text[point:start], None
            yield node.full_text[start:end], element
            point = end
        if point < node.end:
            yield node.full_text[point : node.end], None

    def visit_content_python(self, node, children):
        _, python, _ = children
        return "python", list(self.get_interposed(python))

    def visit_content_pylist(self, node, children):
        _, python, _ = children
        return "pylist", list(self.get_interposed(python))

    def visit_text(self, node, children):
        return "literal", node.text

    def visit_nested(self, node, children):
        _, element, _ = children
        self.nested.append((node.start, node.end, element))

    visit_double3_str = visit_single3_str = visit_double_str = visit_single_str = visit__
    visit_parens = visit_braces = visit_brackets = visit_other = visit__


def simplify(tree):
    return SimplifyVisitor().visit(tree)


def _map_tag_dash(tag):
    title = tag.title()
    if title in {
        "A",
        "Abbr",
        "Acronym",
        "Address",
        "Area",
        "Article",
        "Aside",
        "Audio",
        "B",
        "Base",
        "Basefont",
        "Bdi",
        "Bdo",
        "Big",
        "Blink",
        "Blockquote",
        "Br",
        "Button",
        "Canvas",
        "Caption",
        "Center",
        "Cite",
        "Code",
        "Col",
        "Colgroup",
        "Command",
        "Content",
        "Data",
        "Datalist",
        "Dd",
        "Del",
        "Details",
        "Dfn",
        "Dialog",
        "Div",
        "Dl",
        "Dt",
        "Element",
        "Em",
        "Embed",
        "Fieldset",
        "Figcaption",
        "Figure",
        "Font",
        "Footer",
        "Form",
        "Frame",
        "Frameset",
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "Header",
        "Hgroup",
        "Hr",
        "I",
        "Iframe",
        "Img",
        "Ins",
        "Isindex",
        "Kbd",
        "Keygen",
        "Label",
        "Legend",
        "Li",
        "Link",
        "Listing",
        "Main",
        "Map",
        "Mark",
        "Marquee",
        "Meta",
        "Meter",
        "Multicol",
        "Nav",
        "Nextid",
        "Nobr",
        "Noscript",
        "Object",
        "Ol",
        "Optgroup",
        "Option",
        "Output",
        "P",
        "Param",
        "Picture",
        "Plaintext",
        "Pre",
        "Progress",
        "Q",
        "Rb",
        "Rp",
        "Rt",
        "Rtc",
        "Ruby",
        "S",
        "Samp",
        "Script",
        "Section",
        "Select",
        "Shadow",
        "Slot",
        "Small",
        "Source",
        "Spacer",
        "Span",
        "Strike",
        "Strong",
        "Sub",
        "Summary",
        "Sup",
        "Table",
        "Tbody",
        "Td",
        "Template",
        "Textarea",
        "Tfoot",
        "Th",
        "Thead",
        "Time",
        "Title",
        "Tr",
        "Track",
        "U",
        "Ul",
        "Var",
        "Video",
        "Wbr",
        "Xmp",
    }:
        if title in {"Map", "Object"}:
            title = f"{title}El"
        return "html", title
    elif tag in {
        "Checklist",
        "ConfirmDialog",
        "ConfirmDialogProvider",
        "DatePickerRange",
        "DatePickerSingle",
        "Dropdown",
        "Graph",
        "Input",
        "Interval",
        "Link",
        "Loading",
        "Location",
        "LogoutButton",
        "Markdown",
        "RadioItems",
        "RangeSlider",
        "Slider",
        "Store",
        "SyntaxHighlighter",
        "Tab",
        "Tabs",
        "Textarea",
        "Upload",
    }:
        return "dcc", tag
    elif tag == "DataTable":
        return "dash_table", tag
    else:
        raise HtexprError(f"don't know a Dash module for {tag}")


_map_attribute = {
    "class": "className",
    "accesskey": "accessKey",
    "hreflang": "hrefLang",
    "contenteditable": "contentEditable",
    "tabindex": "tabIndex",
    "colspan": "colSpan",
    "rowspan": "rowSpan",
    "spellcheck": "spellCheck",
}


def to_ast(tree, map_tag=None, map_attribute=None):
    if map_tag is None:
        map_tag = _map_tag_dash
    if map_attribute is None:
        map_attribute = _map_attribute
    recur = partial(to_ast, map_tag=map_tag, map_attribute=map_attribute)
    if isinstance(tree, tuple):
        kind, body = tree
        if kind == "literal":
            return "scalar", ast.Str(s=body, col_offset=0, lineno=1)
        elif kind in ("python", "pylist"):
            splice = {
                f"__htexpr_{i}": recur(subtree)[1]
                for i, (text, subtree) in enumerate(body)
                if subtree is not None
            }
            code = "".join(
                text if subtree is None else f"__htexpr_{i}"
                for i, (text, subtree) in enumerate(body)
            )
            parsed = ast.parse(f"[{code}]" if kind == "pylist" else code, mode="eval").body
            modified = SpliceSubtrees(splice).visit(parsed)
            return ("list" if kind == "pylist" else "scalar", modified)
        else:
            raise HtexprError(f"unknown kind of value tuple: {kind}")
    elif isinstance(tree, dict) and "element" in tree:
        tag = tree["element"]["tag"]
        module, function = map_tag(tag)
        return (
            "scalar",
            _function_call(
                module,
                function,
                [
                    (map_attribute.get(key, key), recur(value)[1])
                    for (key, value) in tree["element"]["attrs"]
                ],
                [recur(node) for node in tree["content"] or []],
            ),
        )
    else:
        raise HtexprError(f"tree not in expected format: {type(tree)}")


def _function_call(module, function, attributes, children):
    if module is None:
        f = ast.Name(id=function, ctx=ast.Load(), col_offset=0, lineno=1)
    else:
        f = ast.Attribute(
            value=ast.Name(id=module, ctx=ast.Load(), col_offset=0, lineno=1),
            ctx=ast.Load(),
            attr=function,
        )

    return ast.Call(
        col_offset=0,
        lineno=1,
        func=f,
        args=[],
        keywords=[ast.keyword(arg="children", value=_flatten(children), col_offset=0, lineno=1)]
        + [
            ast.keyword(arg=arg, value=value, col_offset=0, lineno=1) for (arg, value) in attributes
        ],
    )


# Use cases:
#
# <ul>[ Li() ... ]</ul>
# => Ul(children=[Li(), ...])
#
# <table><tr><th>header</th></tr>
#   [ Tr(...) ]
# <tr><td>footer</td></tr></table>
# => Table(children=[Tr(Th('header'))]+[Tr(...),...]+[Tr(Td('footer'))])
#
# <div>{ code() } constant { code() } constant ...</div>
# => Div(children=[code(), constant, code(), constant, ...])


def _flatten(items):
    if not items:
        return _into_list([])
    groups = [(kind, [item for (_, item) in group]) for kind, group in it.groupby(items, first)]
    groups = [
        _into_list(values) if kind == "scalar" else _into_flat(values) for (kind, values) in groups
    ]
    while len(groups) > 1:
        value0, value1, *_ = groups
        groups[:2] = [_join_lists(value0, value1)]
    return groups[0]


def _into_list(elts):
    return ast.List(elts=elts, col_offset=0, lineno=1, ctx=ast.Load())


def _into_flat(lists):
    return reduce(_join_lists, lists)


def _join_lists(left, right):
    return ast.BinOp(op=ast.Add(), left=left, right=right, lineno=1)


def wrap_ast(body):
    return ast.Expression(body=body[1], lineno=1)


class SpliceSubtrees(ast.NodeTransformer):
    __slots__ = ("subtrees",)

    def __init__(self, subtrees):
        self.subtrees = subtrees

    def visit_Name(self, node):
        replacement = self.subtrees.get(node.id)
        if replacement is None:
            return node
        return ast.copy_location(replacement, node)
