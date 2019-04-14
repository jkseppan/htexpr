# Changelog

## [0.0.2] - 2019-04-14

The `compile` function now returns an `Htexpr` object instead of a
Python code object. The methods `eval` and `run` replace the Python
built-in `eval` function, with different conventions for passing
variable bindings.

The parser is now more tolerant to whitespace in the beginning of
embedded Python code.

The `compile` function results are now memoized to speed up repeated
calls.


[0.0.2]: https://github.com/jkseppan/htexpr/compare/0.0.1...0.0.2
