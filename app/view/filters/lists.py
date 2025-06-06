from markupsafe import Markup


def join_tag(collection, tag_name):
    text = f"<{tag_name}>"
    text += f"</{tag_name}>, <{tag_name}>".join(collection)
    text += f"</{tag_name}>"

    return Markup(text)
