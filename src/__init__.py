"""Top-level package for the project.

Exposes common ASCII helpers for convenient imports in tests and scripts.
"""

from .draw_ascii import DEFAULT_WIDTH, get_ascii_char, image_to_ascii  # noqa: F401

__all__ = [
    "DEFAULT_WIDTH",
    "get_ascii_char",
    "image_to_ascii",
]
