from app import app, db
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text

# todo split this file in pieces
# todo csrf

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
  # todo check field inputs

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
  if not 'user' in session or session['user'] == '':
    return redirect('/')

  area = db.session.execute(text('select area from users where id=:a'), {
    'a': session['user']
  }).fetchone()[0]

  # todo check removed items (or just actually remove them from the db?)

  itemsFromUser = request.args.get('owner', type=int)

  if not itemsFromUser:
    items = db.session.execute(text('select items.* from items, users where items.owner = users.id and users.area=:a and items.possessor is null'), {
      'a': area
    }).fetchall()
  else:
    items = db.session.execute(text('select items.* from items, users where items.owner = users.id and users.area=:a and items.owner=:b'), {
      'a': area,
      'b': itemsFromUser
    }).fetchall()

  req = db.session.execute(text('select requests.id, items.name, requests.creator, items.owner from requests, items, users where (requests.creator=:a and items.id = requests.item) or (users.id=:a and users.id = items.owner and items.id = requests.item) group by requests.id, items.id having requests.status = \'pending\''), {
    'a': session['user']
  }).fetchall()

  reviews = db.session.execute(text('select reviews.id, reviews.given, users.nick from reviews, users where users.id = reviews.reviewed and review is null and reviews.reviewer=:a'), {
    'a': session['user']
  }).fetchall()

  given = db.session.execute(text('select * from items where owner=:a and possessor is not null'), {
    'a': session['user']
  }).fetchall()

  having = db.session.execute(text('select * from items where possessor=:a'), {
    'a': session['user']
  }).fetchall()

  return render_template('welcome.html', items=items, area=f'{area:05}', req=req, reviews=reviews, given=given, having=having)

@app.post('/item')
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
def lendItem(id):
  # todo check input
  # todo maybe check if item is available

  rid = db.session.execute(text('insert into requests (item, creator) values (:a, :b) returning id') , {
    'a': id,
    'b': session['user']
  }).fetchone()[0]

  db.session.commit()

  return redirect(f'/requests/{rid}')

@app.get('/requests/<int:id>')
def getRequest(id):
  # todo check input
  # todo maybe check if item is available
  # todo check if user is allowed to see this

  req = db.session.execute(text('select item, creator, status from requests where id=:a'), {
    'a': id
  }).fetchone()

  item = db.session.execute(text('select name, owner from items where id=:a'), {
    'a': req[0]
  }).fetchone()

  isOwner = (item[1] == session['user'])

  if isOwner:
    secondParty = req[1]
  else:
    secondParty = item[1]


  contacts = db.session.execute(text('select contacts from users where id=:a'), {
    'a': secondParty
  }).fetchone()[0]

  return render_template('request.html', req=req, item=item, isOwner=isOwner, id=id, contacts=contacts)

@app.get('/accept/<int:id>')
def acceptRequest(id):
  # todo check input
  # todo check if user is allowed to do this
  # todo do not allow accepting if item is already given to someone

  db.session.execute(text('update requests set status = \'accepted\' where id=:a'), {
    'a': id
  })

  db.session.execute(text('update items set possessor = requests.creator from requests where requests.item = items.id and requests.id=:a'), {
    'a': id
  })

  db.session.execute(text('with q as (select requests.creator, items.owner from requests, items where requests.id=:a and requests.item = items.id) insert into reviews (reviewer, reviewed) select * from q'), {
    'a': id
  })

  db.session.execute(text('with q as (select requests.creator, items.owner from requests, items where requests.id=:a and requests.item = items.id) insert into reviews (reviewed, reviewer) select * from q'), {
    'a': id
  })

  db.session.commit()

  return render_template('info.html',
    title='Olet hyväksynyt pyynnön.',
    clarification='''
      Etusivun kautta löydät vielä tarvittaessa lainaajan yhteystiedot.
      Kun esine on palautettu sinulle, merkitse se palautetuksi oman etusivusi kautta.
      <br><br>&gt;&gt; <a href="/welcome">Tästä etusivulle</a>
    '''
  )

@app.get('/decline/<int:id>')
def declineRequest(id):
  # todo check input
  # todo check if user is allowed to do this

  db.session.execute(text('update requests set status = \'declined\' where id=:a'), {
    'a': id
  })

  db.session.execute(text('with q as (select requests.creator, items.owner from requests, items where requests.id=:a and requests.item = items.id) insert into reviews (reviewer, reviewed) select * from q'), {
    'a': id
  })

  db.session.execute(text('with q as (select requests.creator, items.owner from requests, items where requests.id=:a and requests.item = items.id) insert into reviews (reviewed, reviewer) select * from q'), {
    'a': id
  })

  db.session.commit()

  return render_template('info.html',
    title='Olet hylännyt pyynnön.',
    clarification='''
      Voit antaa palautteen pyynnön tekijälle etusivun kautta.
      <br><br>&gt;&gt; <a href="/welcome">Tästä etusivulle</a>
    '''
  )

@app.get('/return/<int:id>')
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

@app.get('/review/<int:id>')
def review(id):
  # todo check input
  # todo check that task is available and user is correct

  review = db.session.execute(text('select users.nick from reviews, users where reviews.id=:a and reviews.reviewed = users.id'), {
    'a': id
  }).fetchone()

  return render_template('review.html', review=review, id=id)

@app.post('/review')
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

@app.get('/settings')
def settings():
  user = db.session.execute(text('select nick, contacts, area from users where id=:a'), {
    'a': session['user']
  }).fetchone()

  companies = db.session.execute(text('select id, name from companies where maintainer=:a'), {
    'a': session['user']
  }).fetchall()

  return render_template('settings.html', user=user, companies=companies)

@app.post('/profile')
def updateProfile():
  db.session.execute(text('update users set nick=:a, contacts=:b, area=:c where id=:d'), {
    'a': request.form['user'],
    'b': request.form['contacts'],
    'c': request.form['area'],
    'd': session['user']
  })

  db.session.commit()

  return render_template('info.html',
    title='Päivitetty',
    clarification='''
      Profiilisi päivitys onnistui.
      <br><br>&gt;&gt; <a href="/welcome">Täältä pääset takaisin etusivulle</a>
    '''
  )

@app.post('/password')
def updatePassword():
  current = db.session.execute(text('select secret from users where id=:a'), {
    'a': session['user']
  }).fetchone()[0]

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
