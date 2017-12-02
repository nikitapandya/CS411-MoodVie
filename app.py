import os
import urllib
from flask import Flask, render_template, request, abort, redirect, url_for, send_from_directory, flash
import requests, http.client
import urllib.request, urllib.parse, urllib.error, base64, sys
import json
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from oauth import OAuthSignIn
from secret import Secret

from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'twitter': {
        'id': Secret.twitterid,
        'secret': Secret.twittersecret
    }
}

try:
    conn = http.client.HTTPSConnection("api.themoviedb.org")
except Exception as e:
    print(e.args)


db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

user_sugg = db.Table('user_sugg',
        db.Column('users_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('suggestions_id', db.Integer(), db.ForeignKey('suggestions.id')))



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    sugg = db.relationship('Suggestion', secondary=user_sugg,
                            backref=db.backref('users', lazy='dynamic'))


class SuggestionMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__= {'always_refresh': True}


class Suggestion(SuggestionMixin, db.Model):
    __tablename__ = 'suggestions'
    id =  db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(255))
    sugg1 = db.Column(db.String(255), unique=True) 
    sugg2 = db.Column(db.String(255), unique=True) 
    sugg3 = db.Column(db.String(255), unique=True) 
    sugg4 = db.Column(db.String(255), unique=True) 
    sugg5 = db.Column(db.String(255), unique=True) 

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route("/User_Action/", methods=["POST", "GET"])
def User_Action(mood):
    mooddict = {"anger": ["28", "12"], "contempt": ["27"], "disgust": ["16","99"], "fear": ["10749"], "happiness": ["35", "10402"],"neutral": ["80", "878"], "sadness": ["12"], "surprise": ["53","14","9648"]}
    text1 = mooddict[mood]
    #print("Text1: " + text1)
    randomnum = random.randint(0, len(text1)-1)
    text = text1[randomnum]
    randompage = random.randint(1,301)
    #print("Text:" + text)
    #text = request.form["Genre"]
    payload = "{}"
    try:
        conn.request("GET", "/3/genre/"+ text +"/movies?sort_by=created_at.asc&include_adult=false&language=en-US&api_key=" + Secret.moviesecret + "&page=" + str(randompage), payload)
        res = conn.getresponse()
        data = res.read()
        dataj = json.loads(data.decode()) 

        titles = ""
        randomnums = []
        suggestionLst = []

        while len(randomnums) < 5:
            randindex = random.randint(0,19)
            if randindex not in randomnums:
                randomnums.append(randindex)
        for i in range(5):
            titles += dataj['results'][randomnums[i]]['original_title'] + ", "
            suggestionLst.append(dataj['results'][randomnums[i]]['original_title'])

        suggestions = Suggestion(mood= mood, sugg1=suggestionLst[0], sugg2=suggestionLst[1], sugg3=suggestionLst[2], sugg4=suggestionLst[3], sugg5=suggestionLst[4])
        db.session.add(suggestions)
        db.session.commit()
        print(suggestionLst)
        print(suggestions)
        print(Suggestion.query.first())

        return titles[:-2]

    except Exception as e:
        print(e.args) 

@app.route("/EnterURL/", methods=["POST", "GET"])
def tested():

    text = request.form["url"]
    print(text)

    headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': Secret.microsoftsecret,
    }

    params = urllib.parse.urlencode({
    })

    body = "{ 'url': '" + text + "' }"
    print(body)

    payload = "{}"
    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, body, headers)
        res = conn.getresponse()
        data = res.read()
        # print(data)
        conn.close()
        return data
    except Exception as e:
        print(e.args)


@app.route("/testupload/")
def randtest():
    return render_template('upload.html')

@app.route("/EnterURLmovie/", methods=["POST", "GET"])
def testedmovie():

    text = request.form["url"]
    print(text)

    headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': Secret.microsoftsecret,
    }

    params = urllib.parse.urlencode({
    })

    body = "{ 'url': '" + text + "' }"
    print(body)

    payload = "{}"
    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, body, headers)
        res = conn.getresponse()
        data = res.read()
        # print(data)
        conn.close()
    except Exception as e:
        print(e.args)

    dictemotions = {"anger": 0, "contempt": 0, "disgust": 0, "fear": 0, "happiness": 0, "neutral":0,
            "sadness": 0, "surprise": 0 }

    datajson = json.loads(data.decode())
    for i in range(len(datajson)):
        emotions = (datajson[i]['scores'])

        for key, value in dictemotions.items():
            dictemotions[key] += emotions[key]

    print(dictemotions)
    mood = (max(dictemotions, key=dictemotions.get))
    print(mood)
    return User_Action(mood)




if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
