test:
	pytest --cov=htexpr --cov-report=html --cov-report=term tests
.PHONY: test

dash_test:
	pytest --headless examples/test_dash.py
.PHONY: dash_test
