from flask import render_template


def metabolite_show_page(id):
    return render_template("pages/strains/show.html", id=id)
