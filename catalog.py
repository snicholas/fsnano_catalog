from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Item
import requests
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import datetime
from flask import make_response
from functools import wraps

Base = declarative_base()
GCLIENT_ID = json.loads(
    open('client_secret.json', 'r').
    read())['web']['client_id']

engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorate_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorate_function


def getUsername():
    if 'username' not in login_session:
        return ''
    return login_session.get('username')


def getUserEmail():
    if 'email' not in login_session:
        return ''
    return login_session.get('email')


# Home page
@app.route('/')
@app.route('/catalog')
def mainPage():
    categories = session.query(Category).all()
    lastItems = session.query(Item)
    lastItems = lastItems.order_by(desc(Item.date_insert))
    lastItems = lastItems.order_by(desc(Item.id)).limit(10)
    return render_template('index.html',
                           username=getUsername(),
                           useremail=getUserEmail(),
                           categories=categories,
                           lastItems=lastItems)


# Item detail page
@app.route('/catalog/<int:cat_id>/<string:cat_name>' +
           '/<int:item_id>/<string:item_name>')
def showItemDetail(cat_id, cat_name, item_id, item_name):
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('itemDetail.html',
                           username=getUsername(),
                           useremail=getUserEmail(),
                           categories=categories,
                           Item=item)


# Item detail JSON
@app.route('/catalog/<int:cat_id>/<string:cat_name>/' +
           '<int:item_id>/<string:item_name>/JSON')
def itemDetailJSON(cat_id, cat_name, item_id, item_name):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


# Item creation
@login_required
@app.route('/catalog/newItem', methods=['GET', 'POST'])
def newItem():
    categories = session.query(Category)
    categories = categories.filter_by(useremail=getUserEmail()).all()
    if len(categories) == 0:
        redirect('/catalog/newCategory?nocat=true')
    if request.method == 'POST':
        item = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category_id'],
            date_insert=datetime.datetime.now(),
            useremail=getUserEmail()
        )
        session.add(item)
        flash('Item %s Successfully Edited' % Item.name)
        session.commit()
        return redirect('/catalog')
    else:
        return render_template('newItem.html',
                               username=getUsername(),
                               useremail=getUserEmail(),
                               categories=categories,
                               Item=Item(name='',
                                         description='',
                                         category_id=-1))


# Item edit
@login_required
@app.route('/catalog/<int:cat_id>/<string:cat_name>/' +
           '<int:item_id>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editItem(cat_id, cat_name, item_id, item_name):
    categories = session.query(Category)
    categories = categories.filter_by(useremail=getUserEmail()).all()
    item = session.query(Item).filter_by(id=item_id).one()
    if login_session['email'] != item.useremail:
        return redirect('/unauthorized')
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.category_id = request.form['category_id']
        session.add(item)
        flash('Item %s Successfully Edited' % item.name)
        session.commit()
        return redirect('/catalog')
    else:
        return render_template('newItem.html',
                               username=getUsername(),
                               useremail=getUserEmail(),
                               categories=categories,
                               Item=item)


# Item delete
@login_required
@app.route('/catalog/<int:cat_id>/<string:cat_name>/' +
           '<int:item_id>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteItem(cat_id, cat_name, item_id, item_name):
    category = session.query(Category).filter_by(id=cat_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    if login_session['email'] != item.useremail:
        return redirect('/unauthorized')
    if request.method == 'POST':
        session.query(Item).filter_by(id=item_id).delete()
        flash('Item %s Successfully Deleted' % item_name)
        session.commit()
        return redirect('/catalog')
    else:
        return render_template('deleteItem.html',
                               username=getUsername(),
                               useremail=getUserEmail(),
                               category=category,
                               item=item)


# Category detail page
@app.route('/catalog/<int:cat_id>/<string:cat_name>')
def showCategory(cat_id, cat_name):
    categories = session.query(Category).all()
    items = session.query(Item)
    items = items.filter_by(category_id=cat_id)
    items = items.order_by(asc(Item.name)).all()
    return render_template('catDetail.html',
                           username=getUsername(),
                           useremail=getUserEmail(),
                           categories=categories,
                           lastItems=items)


# Item detail JSON
@app.route('/catalog/<int:cat_id>/<string:cat_name>/JSON')
def categoryJSON(cat_id, cat_name):
    category = session.query(Category).filter_by(id=cat_id).one()
    items = session.query(Item)
    items = items.filter_by(category_id=cat_id)
    items = items.order_by(asc(Item.name)).all()
    return jsonify(Category=category.serialize)


# Category creation
@login_required
@app.route('/catalog/newCategory/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCat = Category(name=request.form['name'],
                          description=request.form['description'],
                          useremail=getUserEmail())
        session.add(newCat)
        flash('New Category %s Successfully Created' % newCat.name)
        session.commit()
        return redirect('/catalog')
    else:
        return render_template('newCategory.html',
                               username=getUsername(),
                               useremail=getUserEmail(),
                               category=Category(name='', description=''))


# Category edit
@login_required
@app.route('/catalog/<int:cat_id>/<string:cat_name>/edit',
           methods=['GET', 'POST'])
def editCategory(cat_id, cat_name):
    category = session.query(Category).filter_by(id=cat_id).one()
    if login_session['email'] != category.useremail:
        return redirect('/unauthorized')
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form['description']
        session.add(category)
        flash('Category %s Successfully Edited' % category.name)
        session.commit()
        return redirect('/catalog')
    else:
        return render_template('newCategory.html',
                               username=getUsername(),
                               useremail=getUserEmail(),
                               category=category)


# Category delete
@login_required
@app.route('/catalog/<int:cat_id>/<string:cat_name>/delete',
           methods=['GET', 'POST'])
def deleteCategory(cat_id, cat_name):
    category = session.query(Category).filter_by(id=cat_id).one()
    if login_session['email'] != category.useremail:
        return redirect('/unauthorized')
    if request.method == 'POST':
        items = session.query(Item).filter_by(category_id=cat_id).delete()
        session.delete(category)
        flash('Category %s Successfully Deleted' % category.name)
        session.commit()
        return redirect('/catalog')
    else:
        return render_template('deleteCategory.html',
                               username=getUsername(),
                               category=category)


# logout: delete session data
@app.route('/logout')
def logout():
    login_session['credentials'] = None
    login_session['gplus_id'] = None
    login_session['username'] = None
    login_session['picture'] = None
    login_session['email'] = None
    return redirect('/')


# unauthorized page
@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html')


# login page
@app.route('/login')
def showLogin():
    if login_session.get('credentials') is None:
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32))
        login_session["state"] = state
        return render_template('login.html', STATE=state)
    return redirect('/')


# google connection function as implemented through the course
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != GCLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
          json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
