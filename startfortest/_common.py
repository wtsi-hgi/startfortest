_TAB = "    "


def reduce_whitespace(string: str) -> str:
    """
    Reduces the whitespace in the given command.
    :param string: the command to reduce whitespace from
    :return: command with reduced whitespace
    """
    leading_tabs = int(min({(len(line) - len(line.lstrip(_TAB))) / len(_TAB) for line in string.split("\n") if len(line.strip()) > 0}))
    stripped = []
    for line in string.split("\n"):
        stripped.append(line.replace(_TAB, "", leading_tabs))
    return "\n".join(stripped)

