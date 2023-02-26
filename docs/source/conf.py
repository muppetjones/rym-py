# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import logging
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def _add_namespaces_to_sys_path():
    parts = Path(__file__).parts
    index = parts.index("rym-py") + 1
    root = Path(*parts[:index]).resolve()
    paths = [str(Path(root, x)) for x in ("rym-lpath",)]
    sys.path.extend(paths)


_add_namespaces_to_sys_path()


project = "rym"
copyright = "2023, Stephen Bush"
author = "Stephen Bush"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["**/tests"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "muppetjones",  # Username
    "github_repo": "rym-py",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/source/",  # Path in the checkout to the docs root
}
