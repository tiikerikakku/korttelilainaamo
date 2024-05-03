from functools import wraps
from flask import render_template, request, session, redirect

def auth(f):
  @wraps(f)
  def isSignedIn(*a, **b):
    if not 'user' in session or session['user'] == '':
      return redirect('/')
    return f(*a, **b)
  return isSignedIn

def csrfPost(f):
  @wraps(f)
  def hasValidCsrf(*a, **b):
    if not 'csrf' in request.form or request.form['csrf'] != session['csrf']:
      return render_template('info.html',
        clarification='Kirjaudu ulos ja sisään uudelleen. Yritä sitten uudestaan.'
      )
    return f(*a, **b)
  return hasValidCsrf

def csrfGet(f):
  @wraps(f)
  def hasValidCsrf(*a, **b):
    token = request.args.get('csrf')

    if not token or token != session['csrf']:
      return render_template('info.html',
        clarification='Kirjaudu ulos ja sisään uudelleen. Yritä sitten uudestaan.'
      )
    return f(*a, **b)
  return hasValidCsrf
