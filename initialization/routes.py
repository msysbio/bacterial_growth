import json

import pages.metabolites as metabolite_pages
import pages.search as search_pages
import pages.static as static_pages
import pages.strains as strain_pages
import pages.studies as study_pages
import pages.upload as upload_pages
import pages.submissions as submission_pages
import pages.users as user_pages
import pages.projects as project_pages
import pages.comparison as comparison_pages
import pages.excel_files as excel_file_pages


def init_routes(app):
    app.add_url_rule("/",       view_func=static_pages.static_home_page)
    app.add_url_rule("/help/",  view_func=static_pages.static_help_page)
    app.add_url_rule("/about/", view_func=static_pages.static_about_page)

    app.add_url_rule("/upload/", view_func=upload_pages.upload_status_page)

    app.add_url_rule("/upload/1", view_func=upload_pages.upload_step1_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/2", view_func=upload_pages.upload_step2_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/3", view_func=upload_pages.upload_step3_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/4", view_func=upload_pages.upload_step4_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/5", view_func=upload_pages.upload_step5_page, methods=["GET", "POST"])

    app.add_url_rule(
        "/upload/new_submission/",
        view_func=submission_pages.new_submission_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/upload/edit_submission/<id>",
        view_func=submission_pages.edit_submission_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/upload/delete_submission/<id>",
        view_func=submission_pages.delete_submission_action,
        methods=["POST"],
    )

    app.add_url_rule("/upload/study_template.xlsx", view_func=upload_pages.download_study_template_xlsx, methods=["POST"])
    app.add_url_rule("/upload/data_template.xlsx", view_func=upload_pages.download_data_template_xlsx, methods=["POST"])
    app.add_url_rule(
        "/upload/spreadsheet_preview/",
        view_func=upload_pages.upload_spreadsheet_preview_fragment,
        methods=["POST"],
    )

    app.add_url_rule("/study/<string:studyId>/",                view_func=study_pages.study_show_page)
    app.add_url_rule("/study/<string:studyId>.zip",             view_func=study_pages.study_download_zip)
    app.add_url_rule("/study/<string:studyId>/export",          view_func=study_pages.study_export_page)
    app.add_url_rule("/study/<string:studyId>/export/preview",  view_func=study_pages.study_export_preview_fragment)
    app.add_url_rule("/study/<string:studyId>/manage",          view_func=study_pages.study_manage_page)
    app.add_url_rule("/study/<string:studyId>/visualize",       view_func=study_pages.study_visualize_page)
    app.add_url_rule("/study/<string:studyId>/visualize/chart", view_func=study_pages.study_chart_fragment)


    app.add_url_rule("/project/<string:projectId>", view_func=project_pages.project_show_page)

    app.add_url_rule("/strain/<int:id>",     view_func=strain_pages.strain_show_page)
    app.add_url_rule("/strains/completion/", view_func=strain_pages.taxa_completion_json)

    app.add_url_rule("/metabolite/<string:chebi_id>", view_func=metabolite_pages.metabolite_show_page)
    app.add_url_rule("/metabolites/completion/",      view_func=metabolite_pages.metabolites_completion_json)

    app.add_url_rule("/comparison/",      view_func=comparison_pages.comparison_show_page)
    app.add_url_rule("/comparison/chart", view_func=comparison_pages.comparison_chart_fragment)
    app.add_url_rule("/comparison/clear", view_func=comparison_pages.comparison_clear_action,   methods=["POST"])
    app.add_url_rule(
        "/comparison/update/<action>.json",
        view_func=comparison_pages.comparison_update_json,
        methods=["POST"],
    )

    app.add_url_rule(
        "/search/",
        view_func=search_pages.search_index_page,
        methods=["GET", "POST"],
    )

    app.add_url_rule("/profile/", view_func=user_pages.user_show_page)
    app.add_url_rule("/login/",   view_func=user_pages.user_login_action, methods=["POST"])

    app.add_url_rule("/claim-project/", view_func=user_pages.user_claim_project_action, methods=["POST"])
    app.add_url_rule("/claim-study/",   view_func=user_pages.user_claim_study_action,   methods=["POST"])

    app.add_url_rule("/excel_files/<id>.xlsx", view_func=excel_file_pages.download_excel_file)

    return app


def dump_routes(rules, filename):
    mapping = {}

    for rule in rules:
        # Taken from werkzeug:
        # https://github.com/pallets/werkzeug/blob/7868bef5d978093a8baa0784464ebe5d775ae92a/src/werkzeug/routing/rules.py#L920-L926
        #
        parts = []
        for is_dynamic, data in rule._trace:
            if is_dynamic:
                parts.append(f"<{data}>")
            else:
                parts.append(data)
        parts_str = "".join(parts).lstrip("|")

        mapping[parts_str] = rule.endpoint

    with open(filename, 'w') as f:
        json.dump(mapping, f, indent=4)
