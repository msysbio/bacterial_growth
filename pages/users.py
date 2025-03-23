from flask import (
    g,
    render_template,
    redirect,
    request,
    session,
)

def user_show_page():
    return render_template('pages/users/show.html')


def user_login_action():
    session['user_uuid'] = request.form['user_uuid']

    return redirect(request.referrer)
