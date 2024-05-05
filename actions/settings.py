from app import app, db
from checks import auth, csrfPost
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

@app.get('/settings')
@auth
def settings():
    user = db.session.execute(text('select nick, contacts, area from users where id=:a'), {
      'a': session['user']
    }).fetchone()

    companies = db.session.execute(text('select id, name from companies where maintainer=:a'), {
      'a': session['user']
    }).fetchall()

    return render_template('settings.html', user=user, companies=companies)

@app.post('/profile')
@auth
@csrfPost
def updateProfile():
    try:
        db.session.execute(text('update users set nick=:a, contacts=:b, area=:c where id=:d'), {
          'a': request.form['user'],
          'b': request.form['contacts'],
          'c': request.form['area'],
          'd': session['user']
        })
    except IntegrityError:
        return render_template('info.html',
          clarification='Käyttäjän tietoja ei tallennettu, koska arvot eivät täytä niille asetettuja ehtoja.'
        )

    db.session.commit()

    return render_template('info.html',
      title='Päivitetty',
      clarification='''
      Profiilisi päivitys onnistui.
      <br><br>&gt;&gt; <a href="/welcome">Täältä pääset takaisin etusivulle</a>
    '''
    )

@app.post('/password')
@auth
@csrfPost
def updatePassword():
    current = db.session.execute(text('select secret from users where id=:a'), {
      'a': session['user']
    }).fetchone()[0]

    if request.form['theNewSecret'] == '':
        return render_template('info.html', clarification='Uusi salasana ei voi olla tyhjä. Palaa takaisin.')

    if not check_password_hash(current, request.form['secret']):
        return render_template('info.html', clarification='Nyt ei onnistunut. Palaa takaisin ja yritä uudestaan.')

    new = generate_password_hash(request.form['theNewSecret'])

    db.session.execute(text('update users set secret=:a where id=:b'), {
      'a': new,
      'b': session['user']
    })

    db.session.commit()

    return render_template('info.html',
      title='Hyvin meni',
      clarification='''
      Salasanasi on muutettu. Pistä uusi sana muistiin.
      <br><br>&gt;&gt; <a href="/welcome">Täältä pääset takaisin etusivulle</a>
    '''
    )
