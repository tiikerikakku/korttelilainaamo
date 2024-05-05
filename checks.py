from functools import wraps
from flask import render_template, request, session, redirect

# pylint: disable=invalid-name

def auth(f):
    @wraps(f)
    def is_signed_in(*a, **b):
        if not 'user' in session or session['user'] == '':
            return redirect('/')
        return f(*a, **b)
    return is_signed_in

def csrf_post(f):
    @wraps(f)
    def has_valid_csrf(*a, **b):
        if not 'csrf' in request.form or request.form['csrf'] != session['csrf']:
            return render_template('info.html',
              clarification='Kirjaudu ulos ja sisään uudelleen. Yritä sitten uudestaan.'
            )
        return f(*a, **b)
    return has_valid_csrf

def csrf_get(f):
    @wraps(f)
    def has_valid_csrf(*a, **b):
        token = request.args.get('csrf')

        if not token or token != session['csrf']:
            return render_template('info.html',
              clarification='Kirjaudu ulos ja sisään uudelleen. Yritä sitten uudestaan.'
            )
        return f(*a, **b)
    return has_valid_csrf
