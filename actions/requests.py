from flask import render_template, session
from sqlalchemy.sql import text
from app import app, db
from checks import auth, csrf_get

@app.get('/requests/<int:id>')
@auth
def get_request(id):
    req = db.session.execute(text('select item, creator, status from requests where id=:a'), {
      'a': id
    }).fetchone()

    item = db.session.execute(text('select name, owner from items where id=:a'), {
      'a': req[0]
    }).fetchone()

    if (req[1] != session['user'] and item[1] != session['user']) or req[2] != 'pending':
        return render_template('info.html', clarification='EI OIKEUTTA TÄNNE!!!!')

    is_owner = (item[1] == session['user'])

    if is_owner:
        second_party = req[1]
    else:
        second_party = item[1]


    contacts = db.session.execute(text('select contacts from users where id=:a'), {
      'a': second_party
    }).fetchone()[0]

    return render_template('request.html', req=req, item=item, isOwner=is_owner, id=id, contacts=contacts)

@app.get('/accept/<int:id>')
@auth
@csrf_get
def accept_request(id):
    req = db.session.execute(text('select items.owner, requests.status, items.possessor from items, requests where items.id = requests.item and requests.id=:a'), {
      'a': id
    }).fetchone()

    if req[0] != session['user'] or req[1] != 'pending' or req[2] != None:
        return render_template('info.html',
          clarification='Tämä toimenpide ei ole sallittu.'
        )

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
@auth
@csrf_get
def decline_request(id):
    req = db.session.execute(text('select items.owner, requests.status from items, requests where items.id = requests.item and requests.id=:a'), {
      'a': id
    }).fetchone()

    if req[0] != session['user'] or req[1] != 'pending':
        return render_template('info.html',
          clarification='Tämä toimenpide ei ole sallittu.'
        )

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
