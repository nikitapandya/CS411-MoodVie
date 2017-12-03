import os
import urllib
from flask import Flask, render_template, request, abort, redirect, url_for, send_from_directory, flash
import requests, http.client
import urllib.request, urllib.parse, urllib.error, base64, sys
import json
import random
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from oauth import OAuthSignIn
from secret import Secret

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
    email = db.Column(db.String(64), nullable=True)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    return render_template('index.html', error = "")


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
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route("/User_Action/", methods=["POST", "GET"])

def User_Action(mood):
    mooddict = {"anger": ["28", "12"], "contempt": ["27"], "disgust": ["16","99"], "fear": ["10749"], "happiness": ["35", "10402"],"neutral": ["80", "878"], "sadness": ["12"], "surprise": ["53","14","9648"]}
    text1 = mooddict[mood]
    randomnum = random.randint(0, len(text1)-1)
    text = text1[randomnum]
    randompage = random.randint(1,20)
    genredict = {"28": "Action", "12": "Adventure", "16": "Animation", "35": "Comedy", "80": "Crime", "99": "Documentary",
            "18": "Drama", "10751": "Family", "14": "Fantasy", "36": "History", "27": "Horror", "10402": "Music",
             "9648": "Mystery", "10749": "Romance", "878": "Science Fiction", "10770": "TV Movie", "53": "Thriller",
             "10752": "War", "37": "Western"}
    #text = request.form["Genre"]
    genre = genredict[str(text)]
    payload = "{}"
    try:
        conn.request("GET", "/3/genre/"+ text +"/movies?sort_by=created_at.asc&include_adult=false&language=en-US&sort_by=popularity.desc&api_key=" + Secret.moviesecret + "&page=" + str(randompage), payload)
        res = conn.getresponse()
        data = res.read()
        dataj = json.loads(data.decode())
        titles = ""
        randomnums = []
        suggestionLst = []
        posterlist = []
        overviewlist = []

        for i in range(10):
            randomnums.append(random.randint(0,20))

        count = 0
        i = 0
        while count < 5:
            try:
                thissuggestion = dataj['results'][randomnums[i]]['original_title']
                thisposter = dataj['results'][randomnums[i]]['poster_path']
                thisoverview = dataj['results'][randomnums[i]]['overview']
                suggestionLst.append(thissuggestion)
                posterlist.append("http://image.tmdb.org/t/p/w185" + thisposter)
                overviewlist.append(thisoverview)
                i += 1
                count += 1

            except Exception as e:
                i += 1
                print("EXCEPTION")
                continue


        # return titles[:-2]
        return getResults(suggestionLst, posterlist, overviewlist, mood, genre)
    except Exception as e:
        print(e.args)

def getResults(suggestionlist, posterlist, overviewlist, mood, genre):
    return render_template('results.html', suggestionlist = suggestionlist, posterlist = posterlist,
                           overviewlist = overviewlist, mood = mood, genre = genre)


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
    try:
        for i in range(len(datajson)):
            emotions = (datajson[i]['scores'])

        for key, value in dictemotions.items():
            dictemotions[key] += emotions[key]

        print(dictemotions)
        mood = (max(dictemotions, key=dictemotions.get))
        print(mood)
        return User_Action(mood)

    except Exception as e:
        return render_template('index.html', error = "Invalid URL. Please try again.")



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)