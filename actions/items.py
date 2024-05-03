from app import app, db
from checks import auth, csrfPost, csrfGet
from flask import render_template, request, session, redirect
from sqlalchemy.sql import text

@app.post('/item')
@auth
@csrfPost
def createItem():
  # todo check field inputs
  # todo accept link input

  db.session.execute(text('insert into items (name, description, owner, link) values (:a, :b, :c, :d)'), {
    'a': request.form['name'],
    'b': request.form['description'],
    'c': session['user'],
    'd': request.form['link']
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
@auth
def getItem(id):
  # todo check input
  # todo maybe check if item is available

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
  # todo check input
  # todo maybe check if item is available

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
  # todo check input
  # todo ensure that user is allowed to do this

  db.session.execute(text('update items set possessor = null where id=:a'), {
    'a': id
  })

  db.session.commit()

  return render_template('info.html',
    title='Esine palautettu',
    clarification='''
      Muut käyttäjät voivat nyt taas lainata esinettäsi korttelilainaamosta.
      <br><br>&gt;&gt; <a href="/welcome">Tästä pääset etusivulle</a>
    '''
  )
