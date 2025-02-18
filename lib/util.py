def trim_lines(string):
    return "\n".join(
        line.strip()
        for line in string.splitlines()
        if line != ''
    )
