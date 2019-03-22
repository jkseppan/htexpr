#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `htexpr` package."""

import pytest

import parsimonious
from htexpr.htexpr import parse, simplify, to_ast, wrap_ast, convert, HtexprError



def test_grammar():
    tree = simplify(parse('<h1 id="foo" class={bar}>heading {foo}<div id="1" class="2"/></h1>'))
    assert tree == {
        'element': {
            'tag': 'h1',
            'attrs': [('id', ('literal', 'foo')),
                      ('class', ('python', 'bar'))]
        },
        'content': [('literal', 'heading '),
                    ('python', 'foo'),
                    {'element': {
                        'tag': 'div',
                        'attrs': [('id', ('literal', '1')),
                                  ('class', ('literal', '2'))]
                    },
                     'content': None,
                     'start': 38
                    }],
        'start': 0
    }


@pytest.mark.parametrize('html', [
    '<div id="asdf" />',
    '<div><div id="asdf" /></div>',
    '<div id={"asdf"} />',
    '<div id="}" />',
    '<div id={1+2+3<">"+4>5} />',
    '<ul>[1, 2, 3]</ul>',
])
def test_grammar_examples(html):
    simplify(parse(html))


@pytest.mark.parametrize('html', [
    '{}',
    'foo',
    '<div id="asdf} />',
    '<div><div id="asdf" /></span>',
    '<div id={"asdf}" />',
    '<div id={1+2+3<">"}+4>5} />',
    '<ul>[1, 2, 3]',
])
def test_grammar_nonexamples(html):
    with pytest.raises(HtexprError):
        simplify(parse(html))


def H1(**kwargs): return {**kwargs, 'tag': 'H1'}
def Div(**kwargs): return {**kwargs, 'tag': 'Div'}
def Span(**kwargs): return {**kwargs, 'tag': 'Span'}


@pytest.mark.parametrize('html,result', [
    pytest.param('<h1 id="header">{foo*bar}</h1>',
                 {'tag': 'H1', 'id': 'header', 'children': ['oneone']},
                 id='foo*bar'),
    pytest.param(
        '''
         <div class="c">
          <span id={foo} class="foo">
            10x: { "x" * 10 }
          </span>
        </div>
        ''',
        {'tag': 'Div', 'className': 'c', 'children': [
            {'tag': 'Span', 'id': 'one', 'className': 'foo', 'children': [
                "10x: ", "xxxxxxxxxx"
            ]}]},
        id='div-span')
])
def test_convert(html, result):
    foo = "one"
    bar = 2
    def map_tag(tag):
        return None, tag.title()
    assert result == eval(convert(html, map_tag=map_tag))
