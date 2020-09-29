# -*- coding: utf-8 -*-
"""Sphinx config."""
import logging as pylogging

import axonius_api_client as pkg
import sphinx_rtd_theme
from sphinx.util import logging


class FilterForIssue123(pylogging.Filter):
    """Work around for https://github.com/agronholm/sphinx-autodoc-typehints/issues/123.

    When this https://github.com/agronholm/sphinx-autodoc-typehints/pull/153
    gets merged, we can remove this
    """

    def filter(self, record: pylogging.LogRecord) -> bool:
        """Make this check more specific by checking that dataclass name is in the message.

        so that you don't filter out other meaningful warnings
        """
        return not record.getMessage().startswith("Cannot treat a function")


logging.getLogger("sphinx_autodoc_typehints").logger.addFilter(FilterForIssue123())

# -- Project information -------------------------------------------
project = pkg.version.__project__
copyright = pkg.version.__copyright__.replace("Copyright", "").strip()
author = pkg.version.__author__
version = pkg.version.__version__
release = pkg.version.__version__
pkg_project = pkg.version.__project__
pkg_project_strip = pkg_project.replace(" ", "").replace("_", "").strip()
pkg_title = pkg.version.__title__
pkg_title_strip = pkg_title.replace(" ", "").replace("_", "").strip()

# -- General configuration -----------------------------------------
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
    "sphinx_click.ext",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "monokai"

# -- Options for HTML  ---------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "logo_only": True,
    "display_version": False,
    "prev_next_buttons_location": "both",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}
html_logo = "_static/axlogofull.png"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = True
html_show_sphinx = False
html_show_copyright = True

# -- Options for HTMLHelp ------------------------------------------
htmlhelp_basename = "{}doc".format(pkg_project_strip)

# -- Options for LaTeX ---------------------------------------------

latex_elements = {}
latex_file = "{}.tex".format(pkg_project_strip)
latex_title = "{} Documentation".format(pkg_project)
latex_documents = [(master_doc, latex_file, latex_title, author, "manual")]

# -- Options for manpages ------------------------------------------
man_title = "{} Documentation".format(pkg_project)
man_pages = [(master_doc, pkg_title_strip, man_title, [author], 1)]

# -- Options for texinfo -------------------------------------------
texinfo_title = "{} Documentation".format(pkg_project)
texinfo_desc = pkg.version.__description__
texinfo_other = "Miscellaneous"
texinfo_documents = [
    (
        master_doc,
        pkg_project_strip,
        texinfo_title,
        author,
        pkg_project_strip,
        texinfo_desc,
        texinfo_other,
    )
]

# -- Options for epub ----------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ["search.html"]

# -- Options for intersphinx ---------------------------------------
intersphinx_mapping = {
    "python": ("http://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/master/", None),
    "urllib3": ("https://urllib3.readthedocs.io/en/latest/", None),
    "dateutil": ("https://dateutil.readthedocs.io/en/latest/", None),
}

# -- Options for todo ----------------------------------------------
todo_include_todos = True

# -- Options for napoleon ------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
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

# -- Options for autosectionlabel ----------------------------------
autosectionlabel_prefix_document = True

# -- Options for sphinx_autodoc_typehints --------------------------
set_type_checking_flag = True
typehints_fully_qualified = True
always_document_param_types = True
typehints_document_rtype = True

# -- Options for sphinx.ext.autodoc --------------------------------
autodoc_default_options = {
    # "member-order": "bysource",
    # "special-members": "__init__,__call__",
    # "undoc-members": True,
    # "show-inheritance": True,
    # "exclude-members": "__weakref__,__str__,__repr__",
}
