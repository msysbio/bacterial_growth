from pathlib import Path

from flask import render_template
from markdown_it import MarkdownIt
from markupsafe import Markup
from jinja2.exceptions import TemplateNotFound


MARKDOWN = MarkdownIt().enable('table')


def help_index_page():
    return render_template("pages/help/index.html")


def help_show_page(name):
    title = name.replace('-', ' ').title()

    try:
        markdown_content = render_template(f"pages/help/pages/{name}.md")
        html_content = Markup(MARKDOWN.render(markdown_content))
    except TemplateNotFound:
        html_content = Markup(render_template(f"pages/help/pages/{name}.html"))

    return render_template(f"pages/help/page.html", title=title, content=html_content)
