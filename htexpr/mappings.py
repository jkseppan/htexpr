# -*- coding: utf-8 -*-
"""Functions or mappings for use with :func:`htexpr.compile`.

:data:`default` is a suitable value for the ``map_tag`` argument
of :func:`compile`; it assumes that

* :mod:`dash_html_components` is imported as ``html``
* :mod:`dash_core_components` is imported as ``dcc``
* :mod:`dash_table` is imported as ``dash_table``

and allows you to type ``html`` tags in any case but requires title
case for the others.

:data:`dbc_and_default` is similar, but adds in the front
:mod:`dash_bootstrap_components` as ``dbc``. To type ``html`` tags
shadowed by ``dbc`` tags, use non-title case.

If you import the modules under other names, you can instantiate the mapping
functions with those, e.g.::

    other_names = [html('dash_html_components'), dcc('dash_core_components')]

:data:`default_attributes` is the default value for the
``map_attribute`` argument of :func:`compile`

"""

from .exceptions import HtexprError
from toolz import curry


@curry
def html(module, tag):
    """Mapping for html tags.

    Maps tags to title case, so you can type html tags as ``<audio>``
    or ``<AuDiO>`` or whichever way.

    """
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
        return module, title


@curry
def dcc(module, tag):
    """Mapping for dash core components."""

    if tag in {
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
        return module, tag


@curry
def datatable(module, tag):
    """Mapping for DataTable."""
    if tag == "DataTable":
        return module, tag


@curry
def dbc(module, tag):
    """Mapping for dash bootstrap components.

    The default assumes that :mod:`dash_bootstrap_components` is
    imported as ``dbc``, which can be changed by setting `module`.

    """

    if tag in {
        "Alert",
        "Badge",
        "Button",
        "ButtonGroup",
        "Card",
        "CardBody",
        "CardColumns",
        "CardDeck",
        "CardFooter",
        "CardGroup",
        "CardHeader",
        "CardImg",
        "CardImgOverlay",
        "CardLink",
        "CardSubtitle",
        "CardText",
        "CardTitle",
        "Checkbox",
        "Checklist",
        "Col",
        "Collapse",
        "Container",
        "DatePickerRange",
        "DatePickerSingle",
        "DropdownMenu",
        "DropdownMenuItem",
        "Fade",
        "Form",
        "FormFeedback",
        "FormGroup",
        "FormText",
        "Input",
        "InputGroup",
        "InputGroupAddon",
        "InputGroupText",
        "Jumbotron",
        "Label",
        "ListGroup",
        "ListGroupItem",
        "ListGroupItemHeading",
        "ListGroupItemText",
        "Modal",
        "ModalBody",
        "ModalFooter",
        "ModalHeader",
        "Nav",
        "NavItem",
        "NavLink",
        "Navbar",
        "NavbarBrand",
        "NavbarSimple",
        "NavbarToggler",
        "Popover",
        "PopoverBody",
        "PopoverHeader",
        "Progress",
        "RadioButton",
        "RadioItems",
        "Row",
        "Select",
        "Spinner",
        "Tab",
        "Table",
        "Tabs",
        "Textarea",
        "Toast",
        "Tooltip",
    }:
        return module, tag


default = (html("html"), dcc("dcc"), datatable("dash_table"))
dbc_and_default = (dbc("dbc"), html("html"), dcc("dcc"), datatable("dash_table"))


default_attributes = {
    "class": "className",
    "accesskey": "accessKey",
    "hreflang": "hrefLang",
    "contenteditable": "contentEditable",
    "tabindex": "tabIndex",
    "colspan": "colSpan",
    "rowspan": "rowSpan",
    "spellcheck": "spellCheck",
    "for": "htmlFor",
}


def _lookup(tag, mappings):
    if not isinstance(mappings, tuple):
        mappings = (mappings,)
    for m in mappings:
        if callable(m):
            value = m(tag)
        else:
            value = m.get(tag)
        if value is not None:
            return value
    raise HtexprError(f"don't know a mapping for {tag}")
