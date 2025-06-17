from markupsafe import Markup
from flask import url_for


def ncbi_url(ncbi_id):
    return f"https://www.ncbi.nlm.nih.gov/datasets/taxonomy/{ncbi_id}/"


def chebi_url(chebi_id):
    return f"https://www.ebi.ac.uk/chebi/searchId.do?chebiId={chebi_id}"


def external_link(url, text=None):
    text = text or url

    return Markup(f"""<a class="external" target="_blank" rel="noreferrer" href="{url}">{text}</a>""")


def help_link(page_name, text=None, section=None, css_class=''):
    text = text or page_name.replace('-', ' ').title()
    url = url_for('help_show_page', name=page_name)

    if section:
        url += '#'
        url += section

    return Markup(f"""<a class="{css_class}" target="_blank" href="{url}">{text}</a>""")
