from app import app, db
from checks import auth
from flask import render_template, request, session, redirect
from sqlalchemy.sql import text

@app.get('/review/<int:id>')
@auth
def review(id):
  # todo check input
  # todo check that task is available and user is correct

  review = db.session.execute(text('select users.nick from reviews, users where reviews.id=:a and reviews.reviewed = users.id'), {
    'a': id
  }).fetchone()

  return render_template('review.html', review=review, id=id)

@app.post('/review')
@auth
def sendReview():
  # todo check that user is allowed to do this

  rating = 0

  if request.form['review'] == 'good':
    rating = 1

  if request.form['review'] == 'bad':
    rating = -1

  db.session.execute(text('update reviews set review=:a, given = now() where id=:b'), {
    'a': rating,
    'b': request.form['id']
  })

  db.session.commit()

  return render_template('info.html',
    title='Arvio annettu ;)',
    clarification='''
      Nyt voit jatkaa lainaamista! Tai vaikkapa antaa lisää arvioita...
      <br><br>&gt;&gt; <a href="/welcome">Siirry etusivulle</a>
    '''
  )
