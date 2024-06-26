from flask import render_template, request, session
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from app import app, db
from checks import auth, csrf_post, csrf_get

@app.post('/business')
@auth
@csrf_post
def create_business():
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

@app.get('/blowupbusiness/<int:id>')
@auth
@csrf_get
def remove_business(id):
    db.session.execute(text('delete from companies where id=:a and maintainer=:b'), {
      'a': id,
      'b': session['user']
    })

    db.session.commit()

    return render_template('info.html',
      title='Yritys veks.',
      clarification='''
      Yrityskortteli on nyt poistettu. Korttelin jäsenet voivat vaihtaa postinumeroaan
      omista asetuksistaan.
      <br><br>&gt;&gt; <a href="/welcome">Täältä pääset takaisin etusivulle</a>
    '''
    )
