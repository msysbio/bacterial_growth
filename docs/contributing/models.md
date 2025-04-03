# Models guide

The application uses [SQLAlchemy](https://www.sqlalchemy.org/) for its ORM tools. Unfortunately, that's a large framework with a large amount of confusing documentation. In this guide, you can find an overview of how it's used in this project in particular.

## SQLAlchemy imports

TODO

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

To fetch records from the database, we need an SQLAlchemy `Session` object. In page handlers, one will be available to the application as `g.db_session`. In tests, it will be initialized per-test in the `self.db_session` property, as long as the test inherits `DatabaseTest`. To initialize a session directly, you can call the function `get_session` in the `db` module:

```python
from db import get_session

with get_session() as db_session:
    # ...
```

The simplest way to fetch a record by primary key is by using the `get` method:

```python
from models import Study

study = g.db_session.get(Study, 'SMGDB00000001')

print(study.name)
# "Synthetic human gut bacterial community using an automated fermentation system"
```

To fetch a study by an arbitrary query, we can use the `.scalars` method that returns a result, and then call `.one()` on it to fetch a single result or `.one_or_none()` to allow the method to return nothing:

```python
import sqlalchemy as sql
from models import Study

study = g.db_session.scalars(
    sql.select(Study)
    .where(Study.studyId == 'SMGDB00000001')
    .limit(1)
).one_or_none()

print(study.name)
# "Synthetic human gut bacterial community using an automated fermentation system"
```

We don't *have* to add `.limit(1)` to the query, but it's not a bad idea to avoid extra work by the database.

To fetch a list of records, we can use the same query, but invoke `.all()` on the result, instead of `.one()`.

```python
import sqlalchemy as sql
from models import Study

studies = g.db_session.scalars(
    sql.select(Study)
    .limit(2)
).all()

print(len(studies))
# 2
```

The `.scalars` method simply tells the session to return a single item for the results. If you want to select one field of the model, you can use that instead:

```python
import sqlalchemy as sql
from models import Study

study_ids = g.db_session.scalars(
    sql.select(Study.studyId)
    .limit(2)
).all()

print(study_ids)
# ['SMGDB00000001', 'SMGDB00000002']
```

Be careful: if you add multiple fields in the `select` clause, the `scalars` method will give you a flat list of the selected fields which doesn't seem like a particularly useful result. To query for a collection of fields and get rows as results...

TODO

## Creating or updating records

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
