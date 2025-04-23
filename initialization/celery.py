from celery import Celery, Task


def init_celery(app):
    """
    The redis config hardcodes port 6380, which is the same one used in the
    docker image.
    """
    class AppTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=AppTask)
    celery_app.config_from_object({
        'broker_url':         "redis://localhost:6380/0",
        'result_backend':     "redis://localhost:6380/0",
        'task_ignore_result': True,
    })
    celery_app.set_default()
    app.extensions["celery"] = celery_app

    return app
