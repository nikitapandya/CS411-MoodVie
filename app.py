import os
import urllib
from flask import Flask, render_template, request, abort, redirect, url_for, send_from_directory
import requests, http.client
import urllib.request, urllib.parse, urllib.error, base64, sys
import json
import random
from werkzeug.utils import secure_filename
app = Flask(__name__)

try:
    conn = http.client.HTTPSConnection("api.themoviedb.org")
except Exception as e:
    print(e.args)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/User_Action/", methods=["POST", "GET"])
def User_Action():

    text = request.form["Genre"]
    payload = "{}"
    try:
        randomPage = random.randint(0,1000) 
        conn.request("GET", "/3/genre/"+ text +"/movies?sort_by=created_at.asc&include_adult=false&language=en-US&api_key=6874ac2dd0d38d7150d4f758d81f6f08&page=" + str(randomPage), payload)

        res = conn.getresponse()
        data = res.read()
        dataj = json.loads(data.decode()) 

        titles = ""
        for i in range(20):
            titles += dataj['results'][i]['original_title'] + ", "
        return titles[:-2]

    except Exception as e:
        print(e.args) 

@app.route("/EnterURL/", methods=["POST", "GET"])
def tested():

    text = request.form["url"]
    print(text)

    headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '82c354542ca9458b9374839f1171647b',
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



#for 500 (internal server error) and 404 error
@app.errorhandler(500)
def internal_error(error):
    return "500"

@app.errorhandler(404)
def not_found(error):
    return "404 error",404

if __name__ == '__main__':
    app.run()
