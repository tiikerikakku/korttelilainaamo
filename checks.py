from functools import wraps
from flask import render_template, request, session, redirect

def auth(f):
  @wraps(f)
  def isSignedIn(*a, **b):
    if not 'user' in session or session['user'] == '':
      return redirect('/')
    return f(*a, **b)
  return isSignedIn
