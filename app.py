import urllib
from flask import Flask, render_template, request, abort
import requests, http.client
import json
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

    processed_text = "api.themoviedb.org/3/genre/"+ text + "/movies?sort_by=created_at.asc&include_adult=false&language=en-US&api_key=6874ac2dd0d38d7150d4f758d81f6f08"


    payload = "{}"
    try:
        conn.request("GET", "/3/genre/"+ text +"/movies?sort_by=created_at.asc&include_adult=false&language=en-US&api_key=6874ac2dd0d38d7150d4f758d81f6f08", payload)


        res = conn.getresponse()
        data = res.read()

        dataj = json.loads(data.decode())   

        #print(data.decode("utf-8"))

        titles = ""
        for i in range(20):
            titles += dataj['results'][i]['original_title'] + ", "
        return titles[:-2]

    except Exception as e:
        print(e.args) 

#for 500 (internal server error) and 404 error
@app.errorhandler(500)
def internal_error(error):
    return "Genre doesn't exist"

@app.errorhandler(404)
def not_found(error):
    return "404 error",404

if __name__ == '__main__':
    app.run()
