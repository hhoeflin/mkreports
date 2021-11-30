def ensure_newline(x: str, nl_before: int, nl_after: int) -> str:
    """Ensure that the number of newlines is as requested."""
    # first strip trailing newline, then add requested number
    x_no_nl = x.rstrip("\n").lstrip("\n")
    return "\n" * nl_before + x_no_nl + "\n" * nl_after
