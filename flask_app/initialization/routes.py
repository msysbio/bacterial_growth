import flask_app.pages.dashboard as dashboard_pages
import flask_app.pages.metabolites as metabolite_pages
import flask_app.pages.search as search_pages
import flask_app.pages.static as static_pages
import flask_app.pages.strains as strain_pages
import flask_app.pages.studies as study_pages
import flask_app.pages.upload as upload_pages


def init_routes(app):
    app.add_url_rule("/",      view_func=static_pages.static_home_page)
    app.add_url_rule("/help",  view_func=static_pages.static_help_page)
    app.add_url_rule("/about", view_func=static_pages.static_about_page)

    app.add_url_rule("/dashboard",       view_func=dashboard_pages.dashboard_index_page)
    app.add_url_rule("/dashboard/chart", view_func=dashboard_pages.dashboard_chart_fragment)

    app.add_url_rule("/upload", view_func=upload_pages.upload_status_page)

    app.add_url_rule("/upload/1", view_func=upload_pages.upload_step1_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/2", view_func=upload_pages.upload_step2_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/3", view_func=upload_pages.upload_step3_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/4", view_func=upload_pages.upload_step4_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/5", view_func=upload_pages.upload_step5_page, methods=["GET", "POST"])

    app.add_url_rule("/upload/study_template.xlsx", view_func=upload_pages.upload_study_template_xlsx)
    app.add_url_rule(
        "/upload/spreadsheet_preview",
        view_func=upload_pages.upload_spreadsheet_preview_fragment,
        methods=["POST"],
    )

    app.add_url_rule("/study/<string:studyId>",                view_func=study_pages.study_show_page)
    app.add_url_rule("/study/<string:studyId>/export",         view_func=study_pages.study_export_page)
    app.add_url_rule("/study/<string:studyId>/export/preview", view_func=study_pages.study_export_preview)
    app.add_url_rule("/study/<string:studyId>/export.zip",     view_func=study_pages.study_download_zip)

    app.add_url_rule("/strain/<int:id>",    view_func=strain_pages.strain_show_page)
    app.add_url_rule("/strains/completion", view_func=strain_pages.taxa_completion_json)

    app.add_url_rule("/metabolite/<string:cheb_id>", view_func=metabolite_pages.metabolite_show_page)
    app.add_url_rule("/metabolites/completion",      view_func=metabolite_pages.metabolites_completion_json)

    app.add_url_rule(
        "/search",
        view_func=search_pages.search_index_page,
        methods=["GET", "POST"],
    )

    return app
