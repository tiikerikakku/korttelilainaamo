from app import app, db
from checks import auth, csrfPost
from flask import render_template, request, session, redirect
from sqlalchemy.sql import text

@app.get('/review/<int:id>')
@auth
def review(id):
  review = db.session.execute(text('select users.nick, reviews.reviewer, reviews.review from reviews, users where reviews.id=:a and reviews.reviewed = users.id'), {
    'a': id
  }).fetchone()

  if review[1] != session['user'] or review[2] != None:
    return render_template('info.html',
      clarification='Et voi antaa arvioita muiden puolesta... Et voi myöskään antaa arviota samasta tapahtumasta useasti.'
    )

  return render_template('review.html', review=review, id=id)

@app.post('/review')
@auth
@csrfPost
def sendReview():
  rating = 0

  if request.form['review'] == 'good':
    rating = 1

  if request.form['review'] == 'bad':
    rating = -1

  db.session.execute(text('update reviews set review=:a, given = now() where id=:b and reviewer=:c and review is null'), {
    'a': rating,
    'b': request.form['id'],
    'c': session['user']
  })

  db.session.commit()

  return render_template('info.html',
    title='Arvio annettu ;)',
    clarification='''
      Nyt voit jatkaa lainaamista! Tai vaikkapa antaa lisää arvioita...
      <br><br>&gt;&gt; <a href="/welcome">Siirry etusivulle</a>
    '''
  )
