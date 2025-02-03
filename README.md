# Flask app

## Setup

Given a working python environment, dependencies can be installed using:

```
pip install -r requirements.txt
```

In the database config directory, the file [`db/config.toml.example`](db/config.toml.example) contains a template for the database configuration. Copy this file to `db/config.toml` and update it with the correct credentials to access a running mysql database. On linux, you may have to add a `unix_socket = ` field as well.

The database structure can be created by running migrations:

```
bin/migrations-run
```

You can also manually interact with the configured database using:

```
bin/dbconsole
```

To launch the application in development mode on <http://localhost:8081>, run:

```
bin/server
```

## Code structure

### Startup: `initialization`

The application starts from `main.py`, which imports and runs code from the "initialization" folder. This includes configuration, routing, static asset compilation, and other utilities that need to be run before the server can start serving requests.

### MVC: `models`, `templates` and `static`, `pages`

The application loosely follows the model-view-controller (MVC) architecture with these three folders holding the three layers. Inside `models`, we keep domain logic dedicated to a specific unit of data. This could be a wrapper for a database table, like "experiment" or "user", or a logical concept like "submission" that is loaded from data in the session. The functions and classes inside the relevant model are all meant to encapsulate potentially complex logic that reads and writes this data.

The `templates` folder contains [Jinja2](https://jinja.palletsprojects.com/en/stable/) templates for every page or HTML fragment. The javascript, CSS, and images that are rendered in the main layout are located in the `static` directory. This follows the default structure of flask apps. An outlier is the Excel metadata template, stored under [`templates/excel`](templates/excel/).

The `pages` folder has all the handler functions that instantiate model objects, call utility functions, and inject the output into a template. These are hooked up to URL routes in [`initialization/routes.py`](initialization/routes.py).

### Other code: `lib`, `forms`, `legacy`

The `lib` folder contains general-purpose utility code. This is code that is not tied to the specific domain of the application. For instance, if we wanted to backport `itertools.batched` from the python 3.12 standard library, we'd put it there.

Form objects are contained in `forms`. Their purpose is to encapsulate some view-level logic that transforms data into a user-facing form. For instance, preparing a dropdown with labels that get translated to database values, or a static CSV file into a collection of fields. Some of these use [Flask-WTF](https://flask-wtf.readthedocs.io/en/0.15.x/), but some are plain objects. They are not in `models`, because they are used to generate HTML, so they sit between the model and view layers.

Code from the original streamlit app that is in active use is in the `legacy` folder. Ideally, it should be restructured and organized in its right place.

### Database: `db`

This folder contains the database configuration in [`db/config.toml.example`](db/config.toml.example) and an `__init__.py` file with the main functions to access a database connection.

Every database change is encapsulated in a migration file under [`db/migrations`](db/migrations), which has an `up` function and a `down` function. The first one applies the migration, the other rolls it back. Ideally, all migrations should be runnable in order. The [`bin/migrations-new`](bin/migrations-new) script bootstraps a new migration in that folder, while [`bin/migrations-run`](bin/migrations-run) runs all of them that haven't already run.

A snapshot of the database schema can be accessed in [`db/schema.sql`](db/schema.sql). This is regenerated on every migration and should be committed into git. It can be used to learn the current state of the database, or to bootstrap the structure for testing purposes.

### Testing: `tests`

In the long term, all logic should be tested by unit tests in this folder. Right now, it only contains a proof-of-concept for database tests.

## External references

- CSS reset: <https://piccalil.li/blog/a-more-modern-css-reset/>
- SVG Spinners: <https://github.com/n3r4zzurr0/svg-spinners>
- Web icons: <https://github.com/tabler/tabler-icons>
