# Controller layer: `pages`, `initialization.routes`

When the flask app is started, it needs to have a mapping between the browser URL and some python code that determines how it's handled. This is the job of the controller layer.

The helper module `initialization.routes` defines the `init_routes` function that creates the mapping. Each route is associated with a function taken from the `pages` module. For example, `pages.studies` includes functions like `study_show_page`, `study_manage_page`, and so on.

## Basic request lifecycle

A simple function handler does several things, in order:

- It receives information about the request. On a static page like the homepage, there might be no additional information needed to create an appropriate response.
- It fetches the data it needs from the database through the model layer.
- It *might* modify the data and store it to the database
- It returns a string that is sent back to the browser. This could be an HTML template located under `templates`, rendered via `render_template`. It could be a JSON string, or even just a static string. It could be a redirect to another page.

Before each request, it's possible for callbacks to be invoked that load data that all pages might need. These are located in the `initialization.global_handlers` module.

## Request-level variables

Flask documentation: [The Application Context](https://flask.palletsprojects.com/en/stable/appcontext/)

Flask provides "magic" objects that act like global variables. They are not global, however -- they're specific to the request. Even if multiple requests are being handled at the same time, these values are local to the current context.

They need to be imported from the `flask` namespace:

```python
from flask import (
    request,
    session,
    g,
)
```

In templates, they are all available without importing.

**Note**: Since these act like global variables, it's important to only use them within the context of a request. If we have a method in a model that accesses `g.db_session`, it will work fine during requests, but it would raise an error in tests or in background jobs that are executed outside of any request-response cycle.

### `request`

This contains all information about the current request, including submitted form data in `request.form`, the URL that was requested, accessible via `request.full_path` or `request.path`, and many others. A full list of its attributes can be found in the Flask API documentation: [`flask.Request`](https://tedboy.github.io/flask/generated/generated/flask.Request.html).

### `session`

The session is stored in an encrypted cookie and contains persistent information across requests, stored in the visitor's browser. That's where the user id is located, which identifies a particular browser as a particular known person.

The value in `session['user_uuid']` is used to fetch a user record from the database and store it in `g.current_user`, if it represents a known user.

The session cookie is set to expire in 31 days of inactivity by default. This means that once a user has logged in, they won't be logged out if they regularly visit.

### `g`

An important context that can contain arbitrary state for the duration of the request. Currently, it contains:

- `g.db_session`: A database session. This is the main method to fetch records from the database, both in the page functions, and, if necessary, in the view templates. Ideally, this connection should be passed along to generic logic in the model layer.
- `g.current_user`: The current user record. While it could be fetched explicitly when needed, it's very commonly needed to dispatch user-specific logic in pages and templates, so it's useful to fetch it on every request.

## Response

The response of a handler function is usually `return render_template`, or it could return some other string. There are a few other things a function might do.

### `flash` and `redirect`

Flask documentation: [Message Flashing](https://flask.palletsprojects.com/en/stable/patterns/flashing/)

The `flash` function sets a single message in the session that can be used to communicate successes or errors after form submission. For instance, when a user logs in, we might want to show them a message:

```python
flash(f"You've successfully logged in as {username}", "success")
return redirect(url_for('home_page'))
```

However, if their password didn't match, we could show them an "error" message instead:

```python
message = "Password login failed, please try again or use the \"Forgotten password\" functionality"
flash(message, "error")
return redirect(url_for('login_page'))
```

If we wanted to show this message in the current template, we could just pass it along to `render_template`. However, the point of `flash` is to keep the message in the session for the *next* request after a redirect.

### `send_file`

If we want to create a download link for a file, the request handler needs to send the binary data using the `send_file` function. For instance, we can generate a template Excel spreadsheet and stream it to the browser as a download:

```python
spreadsheet = create_excel(...)

return send_file(
    io.BytesIO(spreadsheet),
    as_attachment=True,
    download_name="template.xlsx",
)
```
