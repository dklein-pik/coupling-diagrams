"""Library for code-linked coupling diagrams: one layout script -> editable PPTX slide + interactive dark HTML page.

Standard library only. See SKILL.md (one folder up) for the workflow and design rules.
"""
from .canvas import Canvas
from .links import Repo, LinkTable

__all__ = ["Canvas", "Repo", "LinkTable"]
