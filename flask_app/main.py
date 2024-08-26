from jinja2.environment import Template

from flask import Flask
import flask_assets

import flask_app.pages.dashboard as dashboard_pages
import flask_app.pages.metabolites as metabolite_pages
import flask_app.pages.search as search_pages
import flask_app.pages.static as static_pages
import flask_app.pages.strains as strain_pages
import flask_app.pages.studies as study_pages
import flask_app.pages.upload as upload_pages


def create_app():
    app = Flask(__name__)
    app.config.update(
        DEBUG=True,
        ASSETS_DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
        EXPLAIN_TEMPLATE_LOADING=True,
        SECRET_KEY='development_key',
    )

    assets = flask_assets.Environment(app)

    javascripts = flask_assets.Bundle(
        'js/vendor/jquery-3.7.1.js',
        'js/util.js',
        'js/main.js',
        'js/search.js',
        filters='jsmin',
        output='build/bundle.js'
    )
    assets.register('js_bundle', javascripts)

    stylesheets = flask_assets.Bundle(
        'css/reset.css',
        'css/utils.css',
        'css/main.css',
        'css/sidebar.css',
        'css/search.css',
        filters='cssmin',
        output='build/bundle.css'
    )
    assets.register('css_bundle', stylesheets)

    app.add_url_rule("/",      view_func=static_pages.static_home_page)
    app.add_url_rule("/help",  view_func=static_pages.static_help_page)
    app.add_url_rule("/about", view_func=static_pages.static_about_page)

    app.add_url_rule("/dashboard", view_func=dashboard_pages.dashboard_index_page)
    app.add_url_rule("/upload",    view_func=upload_pages.upload_index_page)

    app.add_url_rule("/study/<string:studyId>",     view_func=study_pages.study_show_page)
    app.add_url_rule("/study/<string:studyId>.zip", view_func=study_pages.study_download_page)

    app.add_url_rule("/strain/<int:id>",             view_func=strain_pages.strain_show_page)
    app.add_url_rule("/metabolite/<string:cheb_id>", view_func=metabolite_pages.metabolite_show_page)

    app.add_url_rule(
        "/search",
        view_func=search_pages.search_index_page,
        methods=["GET", "POST"],
    )

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host="0.0.0.0", port=8080)
