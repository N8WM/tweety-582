"""Helper functions for the project"""

import re


def simplify(phrase: str) -> str:
    """Format a phrase to make it easier to compare"""
    return re.sub(r"\.|!|\?|'|,", r"", phrase.lower()).strip()
