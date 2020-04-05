# Changelog

## [0.0.5] - 2020-04-05

The code is now tested against Dash 1.10.

## [0.0.4] - 2019-11-09

`dash_bootstrap_components` can now be used (see `examples/bootstrap.py`).

The examples are now run as part of automated tests using the Selenium
Chrome driver.

The code is now tested against Python 3.8 and Dash 1.6.

## [0.0.3] - 2019-06-21

The `for` attribute, as in `<label for="field">Label</label>`,
is now mapped to the React attribute `htmlFor`.

The example dependencies are updated to allow Dash 1.0.0.

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
[0.0.3]: https://github.com/jkseppan/htexpr/compare/0.0.2...0.0.3
[0.0.4]: https://github.com/jkseppan/htexpr/compare/0.0.3...0.0.4
[0.0.5]: https://github.com/jkseppan/htexpr/compare/0.0.4...0.0.5
