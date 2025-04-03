# Models guide

The application uses [SQLAlchemy](https://www.sqlalchemy.org/) for its ORM tools. Unfortunately, that's a large framework with a large amount of confusing documentation. In this guide, you can find an overview of how it's used in this project in particular.

## Basic models

Each table in the database is represented in the code by a model in the `models` directory. The table name is plural, while the model name is singular, and both are CapitalCamelCased. For example:

- The file `models/bioreplicate.py` contains the model code
- There is only one class in it, called `Bioreplicate`, that inherits from `OrmBase`
- The table name is `Bioreplicates` (TODO: right now, it's `BioReplicatesPerExperiment`)

The file `models/__init__.py` contains a full list of imports of *all* models, alphabetically sorted. Whenever any non-model file needs to import models, it should go through that file to ensure that all model code has been loaded *before* it gets evaluated. This avoids problems with uninitialized relationships. For instance, if you need to make a query that joins metabolites and their join table to studies, you might do something like this:

```python
from models import(
    Metabolite,
    StudyMetabolite,
)

# See the section "Fetching records" for an explanation on the following query:

metabolites = db_session.scalars(
    sql.select(Metabolite)
    .join(StudyMetabolite)
    .where(StudyMetabolite.studyId == study.studyId)
).all()
```

If you need to reference other models in particular *model* file, it's highly recommended to perform this import inside the relevant method, rather than at the top of the file. That way, you avoid circular import errors. For instance, the above code was originally taken from inside a method in the `Measurement` model.

## Defining fields

TODO

## Defining relationships

TODO

## Fetching records

TODO

## Specific recipes

In this section, we'll list some special use cases that you might find in one or two places in the codebase and might not be particularly obvious.

### JSON fields

If a model has a JSON field, then modifying it will not flag the model as needing to be changed. You need to call `flag_modified`:

```python
from sqlalchemy.orm.attributes import flag_modified

submission = g.db_session.get(Submission, 42)

submission.studyDesign['project']['name'] = 'Updated'
flag_modified(submission)

g.db_session.add(submission)
g.db_session.commit()
```

If you forget to invoke that function, SQLAlchemy will happily "forget" to invoke an SQL query. This is unfortunate, but it seems unavoidable.

### Hybrid properties

TODO
