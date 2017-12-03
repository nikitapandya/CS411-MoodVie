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
from sqlalchemy import desc

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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)

class SuggestionMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__= {'always_refresh': True}


class Suggestion(SuggestionMixin, db.Model):
    __tablename__ = 'suggestions'
    id =  db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False)
    mood = db.Column(db.String(255))
    sugg1 = db.Column(db.String(255), unique=True)
    poster1 = db.Column(db.String(255), unique=True)
    oView1 = db.Column(db.String(1024), unique=True)
    sugg2 = db.Column(db.String(255), unique=True) 
    poster2 = db.Column(db.String(255), unique=True)
    oView2 = db.Column(db.String(1024), unique=True)
    sugg3 = db.Column(db.String(255), unique=True) 
    poster3 = db.Column(db.String(255), unique=True)
    oView3 = db.Column(db.String(1024), unique=True)
    sugg4 = db.Column(db.String(255), unique=True)
    poster4 = db.Column(db.String(255), unique=True)
    oView4 = db.Column(db.String(1024), unique=True)
    sugg5 = db.Column(db.String(255), unique=True) 
    poster5 = db.Column(db.String(255), unique=True)
    oView5 = db.Column(db.String(1024), unique=True)

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
        posterlist = []
        overviewlist = []

        while len(randomnums) < 5:
            randindex = random.randint(0,19)
            if randindex not in randomnums:
                randomnums.append(randindex)
        for i in range(5):
            titles += dataj['results'][randomnums[i]]['original_title'] + ", "
            suggestionLst.append(dataj['results'][randomnums[i]]['original_title'])
            posterlist.append("http://image.tmdb.org/t/p/w185" + dataj['results'][randomnums[i]]['poster_path'])
            overviewlist.append(dataj['results'][randomnums[i]]['overview'])

        suggestions = Suggestion(mood= mood, social_id=current_user.nickname, 
            sugg1=suggestionLst[0], poster1=posterlist[0], oView1=overviewlist[0],
            sugg2=suggestionLst[1], poster2=posterlist[1], oView2=overviewlist[1],
            sugg3=suggestionLst[2], poster3=posterlist[2], oView3=overviewlist[2],
            sugg4=suggestionLst[3], poster4=posterlist[3], oView4=overviewlist[3],
            sugg5=suggestionLst[4], poster5=posterlist[4], oView5=overviewlist[4])
        
        db.session.add(suggestions)
        db.session.commit()

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
    return User_Action(mood)

@app.route("/pastRecs/", methods=["POST","GET"])
def test():
    ordered = Suggestion.query.order_by(Suggestion.id.desc())
    filtered = ordered.filter_by(social_id = current_user.nickname).limit(5)
    #Suggestion.query.filter_by(social_id = current_user.nickname)

    message = "" 
    sugg1Lst = []
    moodLst = [] 
    posterLst = [] 
    overviewLst = [] 

    if (ordered is None):
        message = "You have no past recomendations"
    
    else:   
        for row in filtered:
            moodLst.append(row.mood)
            sugg1Lst.append(row.sugg1)
            posterLst.append(row.poster1)
            overviewLst.append(row.oView1)
            sugg1Lst.append(row.sugg2)
            posterLst.append(row.poster2)
            overviewLst.append(row.oView2)
            sugg1Lst.append(row.sugg3)
            posterLst.append(row.poster3)
            overviewLst.append(row.oView3)
            sugg1Lst.append(row.sugg4)
            posterLst.append(row.poster4)
            overviewLst.append(row.oView4)
            sugg1Lst.append(row.sugg5)
            posterLst.append(row.poster5)
            overviewLst.append(row.oView5)

        print(sugg1Lst)

        if (len(sugg1Lst) == 0 or len(posterLst) == 0 or len(overviewLst) == 0): 
            return render_template("pastRecs.html", 
                message="", messageP="", message2="", messageO="")

    return render_template("pastRecs.html", message=moodLst, 
        messageP=posterLst, 
        message2=sugg1Lst, 
        messageO=overviewLst)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
