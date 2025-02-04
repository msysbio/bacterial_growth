
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('./extensions'))

# -- Project information -----------------------------------------------------

# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "μGrowthDB"
organization = "Lab of Microbial Systems Biology"
author = f"{organization} & Contributors"
copyright = f"2025, {author}"
version = "0.0.1"
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-release
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_inline_tabs",
    "sphinx_design",
    "sphinx_issues",

    # For using CONTRIBUTING.md.
    "myst_parser",

    # Local packages.
    "youtube",
    "trello",
    "variables",
    "tags",
    "links",
    "hacks",

    "notfound.extension",

    # These extensions require RTDs to work so they will not work locally.
    #
    # TODO figure out a way to make them work
    #
    # "hoverxref.extension",
    # "sphinx_search.extension",
    # "autoapi.extension"

]

myst_enable_extensions = ["colon_fence"]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    ".env",
    "extensions",
    "**/includes",
    "README.md",
    "design-tabs.js", # We are using inline-tabs and this throws errors/warnings
]

# https://github.com/readthedocs/readthedocs.org/issues/4603
# `tags` come from the `extensions` folder, where the tags.py is located, including the `Tags` class.
if os.environ.get('PLATFORM') == "READTHEDOCS":
    tags.add('readthedocs')
    tags.add("birp")
    tags.add("hdrp")
    tags.add("urp")
else:
    notfound_no_urls_prefix = True

# -- Features ----------------------------------------------------------------

# Auto numbering of figures
numfig = True

# GitHub repo
issues_github_path = "msysbio/bacterial_growth"

# https://sphinx-hoverxref.readthedocs.io/en/latest/usage.html#tooltip-on-all-ref-roles
hoverxref_auto_ref = True
hoverxref_role_types = {
    "ref": "tooltip",  # for hoverxref_auto_ref config
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# https://github.com/pradyunsg/furo
# https://pradyunsg.me/furo/
html_theme = 'furo'
html_title = "μGrowthDB"
html_short_title = "μGrowthDB"
# html_logo = '../logo/crest-oceanrender-logo.svg'
html_logo = '_static/logo-somon.svg'
html_favicon = '../logo/logo-somon.svg'

html_theme_options = {
    "light_logo": 'logo-somon.svg',  # "crest-oceanrender-logo.svg",
    "dark_logo": 'logo-dark.svg',  # "crest-oceanrender-logo-dark.svg",
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
html_static_path = ["_static",
                    "../figs",
]

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

# Customise PDF here. maketitle overrides the cover page.
latex_elements = {
    # "maketitle": "\\input{your_cover.tex}"
    # "maketitle": "\\sphinxmaketitle",
}

# latex_logo = "../logo/crest-oceanrender-logomark512.png"
latex_logo = "../figs/logo-free-white.png"

# -- Templating --------------------------------------------------------------

# The default role will be used for `` so we do not need to do :get:``.
default_role = "get"

# "replace" substitutions are static/global:
#   |name1| replace:: value
#   |name1|
# Cannot do this:
#   |name2| replace:: |name1|
# Inline content has no nested parsing.

# "set" only supports inline content. It will pass its contents to the parser so roles will be processed. Brace
# substitution is supported and is text only (it will lose any nodes). Use it when you need substitutions in role
# content.
#   .. set:: LongName Example
#   .. set:: ShortName :abbr:`{LongName}`
#   An example of using `ShortName`.

# For links where you want to use substitutions, use the link role:
#   .. set Something Example Page
#   .. set BaseURL https://example.com
#   :link:`Link Text for {Something} <{BaseURL}/example>`
# Pass the URL within the angle brackets. Brace substitution will work and will be text only for URLs and support nodes
# for the link text.
#
# For URLs, it is best to use braces even in "set" as they don't require being enclosed in escaped whitespace:
#   .. set:: Link `LinkBase`\ /something/\ `LinkPart`\ /example.html
# Versus:
#   .. set:: Link {LinkBase}/something/{LinkPart}/example.html

# -- Debugging ---------------------------------------------------------------

# For debugging if you want to always have a tag on or off
# tags.add("tag")
# tags.remove("tag")


# -- Options for autoapi -------------------------------------------------------
autoapi_type = "python"
autoapi_dirs = ["../flask_app"]
autoapi_keep_files = True
autoapi_root = "api"
autoapi_member_order = "groupwise"

# No need to manually register .md, as myst_parser handles it
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',  # This is registered automatically by myst_parser
}

# md = markdown.Markdown(extensions=['pymdownx.snippets'])
