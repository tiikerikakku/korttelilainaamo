from app import app, db
from flask import render_template, request, session, redirect
from sqlalchemy.sql import text

@app.post('/business')
def createBusiness():
  db.session.execute(text('insert into companies (name, maintainer) values (:a, :b)'), {
    'a': request.form['name'],
    'b': session['user']
  })

  db.session.commit()

  return render_template('info.html',
    title='Kuin yritysjohtaja.',
    clarification='''
      Sinä siis. Yrityskorttelisi on luotu!
      <br><br>&gt;&gt; <a href="/welcome">Täältä pääset takaisin etusivulle</a>
    '''
  )
