from app import app, db
from checks import auth, csrfPost, csrfGet
from flask import render_template, request, session, redirect
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

@app.post('/item')
@auth
@csrfPost
def createItem():
  try:
    db.session.execute(text('insert into items (name, description, owner, link) values (:a, :b, :c, :d)'), {
      'a': request.form['name'],
      'b': request.form['description'],
      'c': session['user'],
      'd': request.form['link']
    })
  except IntegrityError:
    return render_template('info.html',
      clarification='Esinettä ei luotu, koska annetut arvot eivät täytä ehtoja.'
    )

  db.session.commit()

  return render_template('info.html',
    title='Hienoa!!!',
    clarification='''
      Esineesi on nyt luotu ja alueesi asukkaat voivat nyt pyytää sitä lainaan.
      <br><br>&gt;&gt; <a href="/welcome">Tästä etusivulle</a>
    '''
  )

@app.get('/item/<int:id>')
@auth
def getItem(id):
  item = db.session.execute(text('select * from items where id=:a'), {
    'a': id
  }).fetchone()

  rating = db.session.execute(text('select coalesce(sum(review), 0) from reviews where reviewed=:a'), {
    'a': item[4]
  }).fetchone()[0]

  return render_template('item.html', item=item, rating=rating)

@app.get('/lend/<int:id>')
@auth
@csrfGet
def lendItem(id):
  rid = db.session.execute(text('insert into requests (item, creator) values (:a, :b) returning id') , {
    'a': id,
    'b': session['user']
  }).fetchone()[0]

  db.session.commit()

  return redirect(f'/requests/{rid}')

@app.get('/return/<int:id>')
@auth
@csrfGet
def returnItem(id):
  db.session.execute(text('update items set possessor = null where id=:a and owner=:b'), {
    'a': id,
    'b': session['user']
  })

  db.session.commit()

  return render_template('info.html',
    title='Esine palautettu',
    clarification='''
      Muut käyttäjät voivat nyt taas lainata esinettäsi korttelilainaamosta.
      <br><br>&gt;&gt; <a href="/welcome">Tästä pääset etusivulle</a>
    '''
  )

@app.get('/remove/<int:id>')
@auth
@csrfGet
def removeItem(id):
  db.session.execute(text('update items set removed = true where id=:a and owner=:b'), {
    'a': id,
    'b': session['user']
  })

  db.session.commit()

  return render_template('info.html',
    title='Esine poistettu',
    clarification='''
      Esine ei enää näy korttelilainaamon esinelistauksessa.
      <br><br>&gt;&gt; <a href="/welcome">Tästä pääset etusivulle</a>
    '''
  )

@app.post('/details')
@auth
@csrfPost
def updateItem():
  try:
    db.session.execute(text('update items set name=:a, description=:b, link=:c where id=:d and owner=:e'), {
      'a': request.form['name'],
      'b': request.form['description'],
      'c': request.form['link'],
      'd': request.form['id'],
      'e': session['user']
    })
  except IntegrityError:
    return render_template('info.html',
      clarification='Esinettä ei päivitetty, koska arvot eivät täytä ehtoja.'
    )

  db.session.commit()

  return render_template('info.html',
    title='Ok!',
    clarification='''
      Esineen päivitys onnistui.
      <br><br>&gt;&gt; <a href="/welcome">Täältä pääset takaisin etusivulle</a>
    '''
  )
