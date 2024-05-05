from flask import render_template, request, session, redirect
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from app import app, db
from checks import auth, csrf_post, csrf_get

@app.post('/item')
@auth
@csrf_post
def create_item():
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
def get_item(id):
    item = db.session.execute(text('select * from items where id=:a'), {
      'a': id
    }).fetchone()

    rating = db.session.execute(text('select coalesce(sum(review), 0) from reviews where reviewed=:a'), {
      'a': item[4]
    }).fetchone()[0]

    return render_template('item.html', item=item, rating=rating)

@app.get('/lend/<int:id>')
@auth
@csrf_get
def lend_item(id):
    rid = db.session.execute(text('insert into requests (item, creator) values (:a, :b) returning id') , {
      'a': id,
      'b': session['user']
    }).fetchone()[0]

    db.session.commit()

    return redirect(f'/requests/{rid}')

@app.get('/return/<int:id>')
@auth
@csrf_get
def return_item(id):
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
@csrf_get
def remove_item(id):
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
@csrf_post
def update_item():
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
