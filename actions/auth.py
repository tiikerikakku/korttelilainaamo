from app import app, db
from checks import auth
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text

@app.post('/in')
def signIn():
  q = db.session.execute(text('select id, secret from users where nick=:a'), {
    'a': request.form['user']
  }).fetchone()

  if q and check_password_hash(q[1], request.form['secret']):
    session['user'] = q[0]
    return redirect('/welcome')

  return render_template('info.html', 
    clarification='Käyttäjä tai salasana väärin. Palaa edelliselle sivulle ja yritä uudestaan.'
  )

@app.get('/out')
@auth
def signOut():
  session['user'] = ''

  return render_template('info.html',
    title='Olet kirjautunut ulos',
    clarification='&gt;&gt; <a href="/">Tästä pääset kirjautumaan uudelleen</a>'
  )

@app.post('/register')
def register():
  # todo check if user exists
  # todo check field inputs

  h = generate_password_hash(request.form['secret'])
  nid = db.session.execute(text('insert into users (nick, area, contacts, secret) values (:a, :b, :c, :d) returning id'), {
    'a': request.form['user'],
    'b': request.form['area'],
    'c': request.form['contacts'],
    'd': h
  }).fetchone()[0]

  session['user'] = nid

  db.session.commit()

  return render_template('info.html',
    title='Tervetuloa',
    clarification='''
      Olet onnistuneesti rekisteröitynyt korttelilainaamoon.
      Nyt alkaa unohtumaton ajanjakso elämässäsi.
      <br><br>&gt;&gt; <a href="/welcome">Tästä lainaamaan</a>
    '''
  )
