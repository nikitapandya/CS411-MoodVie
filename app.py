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

import boto3
from boto.s3.key import Key
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['akey'] = Secret.AWS_ACCESS_KEY_ID
app.config['sKey'] = Secret.AWS_SECRET_ACCESS_KEY
app.config['bucket'] = 'cs411photo'

def enviroment(filename):
    # Create an S3 client
    s3 = boto3.client('s3')

    # Create the configuration for the website
    website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
    }

    # Set the new policy on the selected bucket
    s3.put_bucket_website(
        Bucket='my-bucket',
        WebsiteConfiguration=website_configuration
    )

def saveFileToS3(bucket, path, filename):
    s3 = boto3.resource('s3')
    data = open(path + "/" + filename, 'rb')
    s3.Bucket(bucket).put_object(Key=filename, Body=data, ACL='public-read')


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
    poster1 = db.Column(db.String(255), unique=True, nullable=True)
    oView1 = db.Column(db.VARCHAR, unique=True, nullable=True)
    sugg2 = db.Column(db.String(255), unique=True) 
    poster2 = db.Column(db.String(255), unique=True, nullable=True)
    oView2 = db.Column(db.VARCHAR, unique=True, nullable=True)
    sugg3 = db.Column(db.String(255), unique=True) 
    poster3 = db.Column(db.String(255), unique=True, nullable=True)
    oView3 = db.Column(db.VARCHAR, unique=True, nullable=True)
    sugg4 = db.Column(db.String(255), unique=True)
    poster4 = db.Column(db.String(255), unique=True, nullable=True)
    oView4 = db.Column(db.VARCHAR, unique=True, nullable=True)
    sugg5 = db.Column(db.String(255), unique=True)
    poster5 = db.Column(db.String(255), unique=True, nullable=True)
    oView5 = db.Column(db.VARCHAR, unique=True, nullable=True)

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


@app.route('/index/')
def back():
    return render_template('index.html')


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
    randomnum = random.randint(0, len(text1)-1)
    text = text1[randomnum]
    randompage = random.randint(1,20)
    genredict = {"28": "Action", "12": "Adventure", "16": "Animation", "35": "Comedy", "80": "Crime", "99": "Documentary",
            "18": "Drama", "10751": "Family", "14": "Fantasy", "36": "History", "27": "Horror", "10402": "Music",
             "9648": "Mystery", "10749": "Romance", "878": "Science Fiction", "10770": "TV Movie", "53": "Thriller",
             "10752": "War", "37": "Western"}
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

        while len(randomnums) < 10:
            randindex = random.randint(0, 19)
            if randindex not in randomnums:
                randomnums.append(randindex)

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
                
        suggestions = Suggestion(mood= mood, social_id=current_user.nickname, 
            sugg1=suggestionLst[0], poster1=posterlist[0], oView1=overviewlist[0],
            sugg2=suggestionLst[1], poster2=posterlist[1], oView2=overviewlist[1],
            sugg3=suggestionLst[2], poster3=posterlist[2], oView3=overviewlist[2],
            sugg4=suggestionLst[3], poster4=posterlist[3], oView4=overviewlist[3],
            sugg5=suggestionLst[4], poster5=posterlist[4], oView5=overviewlist[4])
        
        db.session.add(suggestions)
        db.session.commit()
        
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

#upload
UPLOAD_FOLDER = '/Users/ruochen/desktop/UPLOAD'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload/")
def upload():
    return render_template("upload.html")

def testedmovie_image(url):

    text = url
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
        message = "You have no past recommendations"
    
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
  
@app.route("/uploadImage/", methods=['POST', 'GET'])
def uploadFile():
    if request.method == 'POST':
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(index.html)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + "." + filename.rsplit('.', 1)[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            saveFileToS3('cs411photo', app.config['UPLOAD_FOLDER'], unique_filename)
            print(unique_filename)
            file_url = "https://s3.amazonaws.com/cs411photo/" + unique_filename
            print(file_url)
            return testedmovie_image(file_url)
    flash("Please select a valid photo! allowed:'pdf', 'png', 'jpg', 'jpeg', 'gif'")
    return render_template('index.html', error = "")
  
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)