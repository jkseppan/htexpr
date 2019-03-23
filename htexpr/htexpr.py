# -*- coding: utf-8 -*-

"Parse HTML with embedded Python expressions into Python code objects"

from parsimonious.grammar import Grammar, NodeVisitor
from parsimonious import exceptions as pe
import ast
from toolz import pipe, partial


class HtexprError(Exception):
    pass


def convert(html, *, map_tag=None, map_attribute=None):
    return pipe(
        html,
        parse,
        simplify,
        partial(to_ast, map_tag=map_tag, map_attribute=map_attribute),
        wrap_ast,
        ast.fix_missing_locations,
        partial(compile, filename="<unknown>", mode="eval"),
    )


_grammar = Grammar(
    r"""
    document      = _ element _
    _             = ~'[ \t\n]*'
    element       = elt_empty / elt_nonempty
    elt_nonempty  = tag_open content tag_close
    tag_open      = langle tag_name attributes rangle _
    tag_close     = _ lclose tag_name rangle
    elt_empty     = langle tag_name attributes rclose
    langle        = ~r"\s*<\s*"
    rangle        = ~r"\s*>\s*"
    lclose        = ~r"\s*</\s*"
    rclose        = ~r"\s*/>\s*"
    attributes    = attr*
    attr          = _ attr_name _ '=' _ attr_value
    tag_name      = ~"[a-z][a-z0-9._-]*"i
    attr_name     = ~"[a-z][a-z0-9._-]*"i
    attr_value    = attr_value_literal / attr_value_python
    attr_value_literal = ~'"[^"]*"'
    attr_value_python = '{' python_expr '}'
    content       = content1*
    content1      = content_python / element / text
    content_python = lbrace python_expr rbrace
    lbrace        = ~r"{\s*"
    rbrace        = ~r"\s*}"
    text          = ~r'[^<{]+'
    python_expr   = (double3_str / single3_str / double_str / single_str / parens / braces / brackets / other)*
    double3_str   = '"\""' ~r'([^"]|"[^"]|""[^"])*' '"\""'
    single3_str   = "'''"  ~r"([^']|'[^']|''[^'])*" "'''"
    double_str    = '"' ~r'([^"\\]|\\.)*' '"'
    single_str    = "'" ~r"([^'\\]|\\.)*" "'"
    parens        = "(" python_expr ")"
    braces        = "{" python_expr "}"
    brackets      = "[" python_expr "]"
    other         = ~'[^(){}"\']+'
    """
)


def parse(html):
    try:
        return _grammar.parse(html)
    except pe.ParseError as e:
        raise HtexprError(e)


class SimplifyVisitor(NodeVisitor):
    visit_element = visit_content1 = NodeVisitor.lift_child
    unwrapped_exceptions = (HtexprError,)

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

    def visit_attr_value_python(self, node, children):
        _, python, _ = children
        return "python", python.text

    def visit_attr_dict(self, node, children):
        _, _, python, _ = children
        return "dict", python.text

    def visit_content(self, node, children):
        return children

    def visit_content_python(self, node, children):
        _, python, _ = children
        return "python", python.text

    def visit_text(self, node, children):
        return "literal", node.text

    visit_double3_str = (
        visit_single3_str
    ) = (
        visit_double_str
    ) = visit_single_str = visit_parens = visit_braces = visit_brackets = visit_other = visit__


simplify = SimplifyVisitor().visit


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
}


def to_ast(tree, map_tag=None, map_attribute=None):
    if map_tag is None:
        map_tag = _map_tag_dash
    if map_attribute is None:
        map_attribute = _map_attribute
    recur = partial(to_ast, map_tag=map_tag, map_attribute=map_attribute)
    if isinstance(tree, tuple):
        kind, value = tree
        if kind == "literal":
            return ast.Str(s=value, col_offset=0, lineno=1)
        elif kind == "python":
            return ast.parse(value, mode="eval").body
        else:
            raise HtexprError(f"unknown kind of value tuple: {kind}")
    elif "element" in tree:
        children = ast.List(
            elts=[recur(node) for node in tree["content"] or []],
            col_offset=0,
            lineno=1,
            ctx=ast.Load(),
        )
        tag = tree["element"]["tag"]
        module, tag = map_tag(tag)
        if module is None:
            func = ast.Name(id=tag, ctx=ast.Load(), col_offset=0, lineno=1)
        else:
            func = ast.Attribute(
                value=ast.Name(id=module, ctx=ast.Load(), col_offset=0, lineno=1),
                ctx=ast.Load(),
                attr=tag,
            )
        return ast.Call(
            col_offset=0,
            lineno=1,
            func=func,
            args=[],
            keywords=[ast.keyword(arg="children", value=children, col_offset=0, lineno=1)]
            + [
                ast.keyword(
                    arg=map_attribute.get(key, key), value=recur(value), col_offset=0, lineno=1
                )
                for (key, value) in tree["element"]["attrs"]
            ],
        )
    else:
        raise HtexprError(
            f'tree not in expected format: {type(tree)}, {tree[0] if isinstance(tree, tuple) else ""}'
        )


def wrap_ast(body):
    return ast.Expression(body=body, lineno=1)
