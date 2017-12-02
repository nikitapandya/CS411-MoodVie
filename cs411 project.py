import os
import urllib
from flask import Flask, render_template, request, abort, redirect, url_for, send_from_directory, flash
import requests, http.client
import urllib.request, urllib.parse, urllib.error, base64, sys
import json
import random
from werkzeug.utils import secure_filename
from flask import Flask, Response, request, render_template, redirect, url_for
import boto3
import sys
from boto.s3.key import Key
from werkzeug.utils import secure_filename
import uuid


app = Flask(__name__)
AWS_ACCESS_KEY_ID = 'AKIAIMNLH4CMCWPTQRDQ'
AWS_SECRET_ACCESS_KEY = '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'
app.config['akey'] = AWS_ACCESS_KEY_ID
app.config['sKey'] = AWS_SECRET_ACCESS_KEY
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

@app.route('/')
def index():
    return render_template('index.html')



@app.route("/AfterUpload")
def AfterUpload():
    return render_template("AfterUpload.html.")

@app.route("/upload/")
def upload():
    return render_template("upload.html")




@app.route("/EnterURL/", methods=["POST", "GET"])
def tested():

    text = request.form["url"]
    print(text)

    headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '3bc3fe2a2aac4ce995b5f3c8d2326fa7',
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

#UPLOAD

UPLOAD_FOLDER = '/Users/ruochen/desktop/UPLOAD'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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
            saveFileToS3(app.config['bucket'], app.config['UPLOAD_FOLDER'], unique_filename)
            print(unique_filename)
            file_url = "https://s3.amazonaws.com/cs411photo/" + unique_filename
            print(file_url)
            return render_template("AfterUpload.html")
    return ""




#for 500 (internal server error) and 404 error
@app.errorhandler(500)
def internal_error(error):
    return "500"

@app.errorhandler(404)
def not_found(error):
    return "404 error",404

if __name__ == '__main__':
    app.run()
