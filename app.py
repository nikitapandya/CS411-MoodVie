import urllib
from flask import Flask, render_template, request
import requests, http.client
import json
app = Flask(__name__)
conn = http.client.HTTPSConnection("api.themoviedb.org")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/User_Action/", methods=["POST", "GET"])
def User_Action():

    text = request.form["Genre"]

    processed_text = "api.themoviedb.org/3/genre/"+ text + "/movies?sort_by=created_at.asc&include_adult=false&language=en-US&api_key=6874ac2dd0d38d7150d4f758d81f6f08"


    payload = "{}"
    conn.request("GET", "/3/genre/"+ text +"/movies?sort_by=created_at.asc&include_adult=false&language=en-US&api_key=6874ac2dd0d38d7150d4f758d81f6f08", payload)


    res = conn.getresponse()
    data = res.read()

    dataj = json.loads(data.decode())

    #print(data.decode("utf-8"))

    titles = ""
    for i in range(20):
        titles += dataj['results'][i]['original_title'] + ", "
    return titles[:-2]

if __name__ == '__main__':
    app.run()
