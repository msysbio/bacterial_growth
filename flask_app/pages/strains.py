from flask import render_template


def strain_show_page(cheb_id):
    return render_template("pages/metabolites/show.html", cheb_id=cheb_id)
