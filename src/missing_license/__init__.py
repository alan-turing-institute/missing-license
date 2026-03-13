"""
missing-license: A GitHub Action that scans an organisation for public repositories
without a license and opens issues to notify owners.
"""

from __future__ import annotations

from importlib.metadata import version

__all__ = ("__version__",)
__version__ = version(__name__)
