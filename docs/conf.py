# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'BustAPI'
copyright = '2025, GrandpaEJ'
author = 'GrandpaEJ'
release = '0.2.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

# -- Autodoc settings -------------------------------------------------------
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Add the python directory to the path
import sys
import os
sys.path.insert(0, os.path.abspath('../python'))