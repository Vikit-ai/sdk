# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "vikit.ai SDK"
copyright = "2024, vikit.ai team"
author = "vikit.ai team"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
]

autoapi_dirs = ["../vikit"]
autoapi_type = "python"
autoapi_template_dir = "_templates/autoapi"

autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autodoc_typehints = "signature"

rst_prolog = """
.. role:: summarylabel
"""
html_css_files = [
    "css/custom.css",
]


def contains(seq, item):
    return item in seq


def prepare_jinja_env(jinja_env) -> None:
    jinja_env.tests["contains"] = contains


autoapi_prepare_jinja_env = prepare_jinja_env

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
