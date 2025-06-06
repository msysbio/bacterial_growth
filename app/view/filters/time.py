import humanize


def relative_time(timestamp):
    return humanize.naturaltime(timestamp)
