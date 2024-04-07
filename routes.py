from app import app, db
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text

@app.get('/')
def main():
  if 'user' in session and session['user'] != '':
    return redirect('/welcome')
  return render_template('main.html')

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
def signOut():
  session['user'] = ''

  return render_template('info.html',
    title='Olet kirjautunut ulos',
    clarification='&gt;&gt; <a href="/">Tästä pääset kirjautumaan uudelleen</a>'
  )

@app.post('/register')
def register():
  # todo check if user exists

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

@app.get('/welcome')
def welcome():
  area = db.session.execute(text('select area from users where id=:a'), {
    'a': session['user']
  }).fetchone()[0]

  items = db.session.execute(text('select items.* from items, users where items.owner = users.id and users.area=:a'), {
    'a': area
  }).fetchall()

  return render_template('welcome.html', items=items, area=f'{area:05}')

@app.post('/item')
def createItem():
  db.session.execute(text('insert into items (name, description, owner) values (:a, :b, :c)'), {
    'a': request.form['name'],
    'b': request.form['description'],
    'c': session['user']
  })

  db.session.commit()

  return render_template('info.html',
    title='Hienoa!!!',
    clarification='''
      Esineesi on nyt luotu ja alueesi asukkaat voivat nyt pyytää sitä lainaan.
      <br><br>&gt;&gt; <a href="/welcome">Tästä etusivulle</a>
    '''
  )

@app.get('/item/<int:id>')
def getItem(id):
  item = db.session.execute(text('select * from items where id=:a'), {
    'a': id
  }).fetchone()

  return render_template('item.html', item=item)
