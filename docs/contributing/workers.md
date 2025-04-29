# Workers

Processing that happens outside of the website's request-response loop is handled with background jobs run by workers. This is done using [Celery](https://docs.celeryq.dev/en/stable/index.html).

To run the workers, you can use the instructions in the Celery project's documentation, or just trigger the provided script:

```
bin/worker
```

This starts a celery process that connects to redis on 6380, a port specified in the `docker-compose.yml` file. Triggering jobs feeds information about them into redis and the worker's threads consume the job information and run the relevant code.

An example of starting a job in code:

```python
# Fetch or create a particular database record
calculation_technique = ...

# Enqueue a job function using the `.delay` method:
result = update_calculation_technique.delay(calculation_technique.id, params)

# The return result object represents the task that was started and we can hold
# on to the id for monitoring purposes.
calculation_technique.jobUuid = result.task_id
```

In this example, the job will update the state of the database record and in the web UI, we can check that state to do something when the record is in a "ready" state.
