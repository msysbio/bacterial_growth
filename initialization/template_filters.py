from app.view.filters import (
    lists,
    numbers,
    time,
)


def init_template_filters(app):
    app.template_filter('join_tag')(lists.join_tag)
    app.template_filter('relative_time')(time.relative_time)
    app.template_filter('map_scientific')(numbers.map_scientific)

    return app
