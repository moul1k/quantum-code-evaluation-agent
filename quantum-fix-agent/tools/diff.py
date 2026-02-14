from difflib import unified_diff


def make_unified_diff(before: str, after: str, fromfile: str = "before.py", tofile: str = "after.py") -> str:
    return "".join(
        unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
        )
    )
