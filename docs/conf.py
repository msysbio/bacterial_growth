# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'μGrowthDB'
copyright = '2025, Lab of Microbial Systems Biology'
organization = "Lab of Microbial Systems Biology"
author = f"{organization} & Contributors"
release = 'v1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath('./extensions'))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "autoapi.extension",
    "nbsphinx",

    "myst_parser",
    "sphinx_search.extension",

    # Local packages.
    "youtube",
    "trello",
    "variables",
    "tags",
    "links",
    "hacks"
]


# -- Options for autoapi -------------------------------------------------------

# NOTE: This pair works good in the RTD
autoapi_dirs = ['../app', '../initialization']
autoapi_ignore = []


# Enable typehints
autodoc_typehints = "signature"

# Napoleon settings
napoleon_numpy_docstring = True

# The master toctree document.
master_doc = "index"

pygments_style = "sphinx"

# -- Options for HTML output --------------------------------------------------

mathjax_path = (
    "https://cdn.mathjax.org/mathjax/latest/"
    "MathJax.js?config=TeX-AMS-MML_HTMLorMML"
)

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Features ----------------------------------------------------------------

# Auto numbering of figures
numfig = True

# GitHub repo
issues_github_path = "msysbio/bacterial_growth"

# -- Options for HTML output -------------------------------------------------
# Check also: https://github.com/pradyunsg/furo
html_theme = 'furo'
html_title = "μGrowthDB"
html_short_title = "μGrowthDB"
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'
html_theme_options = {
    "light_logo": 'logo.png',  # "crest-oceanrender-logo.svg",
    "dark_logo": 'logo.png',  # "crest-oceanrender-logo-dark.svg",
    "sidebar_hide_name": True,
    # "announcement": "<em>Important</em> announcement!",
}

html_context = {
    "organization": organization,
}

html_show_sphinx = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# These paths are either relative to html_static_path or fully qualified paths (eg. https://...).
# Increment query parameter to invalidate the cache.
html_css_files = [
    'custom.css',
]

html_js_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/medium-zoom/1.0.6/medium-zoom.min.js',
    'https://p.trellocdn.com/embed.min.js',
    'custom.js',
]

html_output_encoding = "utf-8"

# -- Options for PDF output --------------------------------------------------
latex_logo = "_static/logo-free-white.png"

# -- Templating --------------------------------------------------------------

# The default role will be used for `` so we do not need to do :get:``.
default_role = "get"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
}

# No need to manually register .md, as myst_parser handles it
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',  # This is registered automatically by myst_parser
}
