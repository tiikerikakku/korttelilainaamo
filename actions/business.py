from app import app, db
from checks import auth, csrfPost
from flask import render_template, request, session, redirect
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

@app.post('/business')
@auth
@csrfPost
def createBusiness():
  try:
    db.session.execute(text('insert into companies (name, maintainer) values (:a, :b)'), {
      'a': request.form['name'],
      'b': session['user']
    })
  except IntegrityError:
    return render_template('info.html',
      clarification='Yrityskorrtelin luonti epäonnistui. Palaa takaisin ja kokeile eri nimellä.'
    )

  db.session.commit()

  return render_template('info.html',
    title='Kuin yritysjohtaja.',
    clarification='''
      Sinä siis. Yrityskorttelisi on luotu!
      <br><br>&gt;&gt; <a href="/welcome">Täältä pääset takaisin etusivulle</a>
    '''
  )
