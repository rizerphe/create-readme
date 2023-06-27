"""A basic helper function for multiline input."""

import sys


def multiline_input(prompt: str) -> str:
    """Return a string of user input from a prompt.

    The user can input multiple lines of text, and the function will return
    the string of text when the user enters a blank line.

    Args:
        prompt: The prompt to display to the user.

    Returns:
        The string of text entered by the user.
    """
    print(prompt, "(Press Ctrl+D to finish.)")
    return sys.stdin.read().strip()
