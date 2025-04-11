import statistics

def init_template_filters(app):
    @app.template_filter('mean')
    def _mean(values, attribute=None):
        if attribute is not None:
            values = [getattr(v, attribute) for v in values]
            values = [v for v in values if v is not None]

        if values:
            return statistics.fmean(values)
        else:
            return 0

    @app.template_filter('std')
    def _std(values, attribute=None):
        if attribute is not None:
            values = [getattr(v, attribute) for v in values]
            values = [v for v in values if v is not None]

        if len(values) > 1:
            return statistics.stdev(values)
        else:
            return 0

    return app
