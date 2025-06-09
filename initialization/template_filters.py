from app.view.filters import (
    lists,
    numbers,
    time,
    urls,
)


def init_template_filters(app):
    app.template_filter('join_tag')(lists.join_tag)
    app.template_filter('relative_time')(time.relative_time)
    app.template_filter('map_scientific')(numbers.map_scientific)
    app.template_filter('ncbi_url')(urls.ncbi_url)
    app.template_filter('chebi_url')(urls.chebi_url)

    return app
