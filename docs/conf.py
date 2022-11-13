# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys, os

sys.path.insert(0, os.path.abspath("../"))

project = "htexpr"
copyright = "2019-2022, Jouni K. Seppänen"
author = "Jouni K. Seppänen"
release = "0.1.1"

extensions = ["sphinx.ext.napoleon"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "*~", ".#*"]

html_theme = "classic"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
master_doc = "index"
