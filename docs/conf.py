# -*- coding: utf-8 -*-
"""Sphinx config."""
from __future__ import absolute_import, division, print_function, unicode_literals

import axonius_api_client as pkg  # noqa

import sphinx_rtd_theme


def strip(t):  # noqa
    return t.replace(" ", "").replace("_", "").strip()


# -- Project information -----------------------------------------------------

project = pkg.version.__project__
copyright = pkg.version.__copyright__.replace("Copyright", "").strip()
author = pkg.version.__author__
version = pkg.version.__version__
release = pkg.version.__version__
pkg_project = pkg.version.__project__
pkg_title = pkg.version.__title__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "monokai"

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "logo_only": True,
    "display_version": False,
    "prev_next_buttons_location": "both",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 5,
    "includehidden": True,
    "titles_only": False,
}
html_logo = "_static/axlogofull.png"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = True
html_show_sphinx = False
html_show_copyright = True

# -- Options for HTMLHelp output ---------------------------------------------
htmlhelp_basename = "{}doc".format(strip(pkg_project))

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}
latex_documents = [
    (
        master_doc,
        "{}.tex".format(strip(pkg_project)),
        "{} Documentation".format(pkg_project),
        author,
        "manual",
    )
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc, strip(pkg_title), "{} Documentation".format(pkg_project), [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (
        master_doc,
        strip(pkg_project),
        "{} Documentation".format(pkg_project),
        author,
        strip(pkg_project),
        pkg.version.__description__,
        "Miscellaneous",
    )
]

# -- Options for Epub output -------------------------------------------------

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ["search.html"]

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("http://docs.python.org/3", None),
    "requests": ("https://2.python-requests.org//en/master/", None),
    "urllib3": ("https://urllib3.readthedocs.io/en/latest/", None),
}

# -- Options for todo extension ----------------------------------------------

todo_include_todos = True

# -- Options for Napoleon -------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_keyword = True
napoleon_use_rtype = True

autosectionlabel_prefix_document = True
