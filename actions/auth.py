from app import app, db
from checks import auth, csrfGet
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from secrets import token_hex

@app.post('/in')
def signIn():
  q = db.session.execute(text('select id, secret from users where nick=:a'), {
    'a': request.form['user']
  }).fetchone()

  if q and check_password_hash(q[1], request.form['secret']):
    session['user'] = q[0]
    session['csrf'] = token_hex(24)

    return redirect('/welcome')

  return render_template('info.html', 
    clarification='Käyttäjä tai salasana väärin. Palaa edelliselle sivulle ja yritä uudestaan.'
  )

@app.get('/out')
@auth
@csrfGet
def signOut():
  session['user'] = ''
  session['csrf'] = ''

  return render_template('info.html',
    title='Olet kirjautunut ulos',
    clarification='&gt;&gt; <a href="/">Tästä pääset kirjautumaan uudelleen</a>'
  )

@app.post('/register')
def register():
  if request.form['secret'] == '':
    return render_template('info.html', 
      clarification='Tiliä ei voitu luoda. Salasana liian lyhyt.'
    )

  h = generate_password_hash(request.form['secret'])
  
  try:
    nid = db.session.execute(text('insert into users (nick, area, contacts, secret) values (:a, :b, :c, :d) returning id'), {
      'a': request.form['user'],
      'b': request.form['area'],
      'c': request.form['contacts'],
      'd': h
    }).fetchone()[0]
  except IntegrityError:
    return render_template('info.html', 
      clarification='Tiliä ei voitu luoda. Täytä kaikki kentät ja kokeile eri käyttäjänimeä.'
    )

  session['user'] = nid
  session['csrf'] = token_hex(24)

  db.session.commit()

  return render_template('info.html',
    title='Tervetuloa',
    clarification='''
      Olet onnistuneesti rekisteröitynyt korttelilainaamoon.
      Nyt alkaa unohtumaton ajanjakso elämässäsi.
      <br><br>&gt;&gt; <a href="/welcome">Tästä lainaamaan</a>
    '''
  )
