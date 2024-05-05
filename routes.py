from flask import render_template, request, session, redirect
from sqlalchemy.sql import text
from app import app, db
from checks import auth

@app.get('/')
def main():
    if 'user' in session and session['user'] != '':
        return redirect('/welcome')
    return render_template('main.html')

@app.get('/welcome')
@auth
def welcome():
    area = db.session.execute(text('select area from users where id=:a'), {
      'a': session['user']
    }).fetchone()[0]

    business = None

    if str(area)[-1] == '9':
        business = 'Tuntematon yrityskortteli'
        bid = int(str(area)[:-1])

        business_info = db.session.execute(text('select name from companies where id=:a'), {
          'a': bid
        }).fetchone()

        if business_info:
            business = business_info[0]

    items_from_user = request.args.get('owner', type=int)

    if not items_from_user:
        items = db.session.execute(text('select items.* from items, users where items.owner = users.id and users.area=:a and items.possessor is null and items.owner!=:b and items.removed is false'), {
          'a': area,
          'b': session['user']
        }).fetchall()
    else:
        items = db.session.execute(text('select items.* from items, users where items.owner = users.id and users.area=:a and items.owner=:b and items.removed is false'), {
          'a': area,
          'b': items_from_user
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

    return render_template('welcome.html', items=items, area=f'{area:05}', business=business, req=req, reviews=reviews, given=given, having=having)

# pylint: disable=unused-import

import actions.auth
import actions.items
import actions.requests
import actions.reviews
import actions.settings
import actions.business
