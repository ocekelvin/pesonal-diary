import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Mendapatkan path direktori tempat berjalan
basepath = os.path.dirname(__file__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(basepath, 'static'), filename)


@app.route('/diary', methods=['GET'])
def show_diary():
    articles = list(db.diary.find({}, {'_id': False}))
    return jsonify({'articles': articles})


@app.route('/diary', methods=['POST'])
def save_diary():
    title_receive = request.form["title_give"]
    content_receive = request.form["content_give"]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    file = request.files["file_give"]
    file_extension = file.filename.split('.')[-1]
    filename = f'static/post-{mytime}.{file_extension}'
    file.save(os.path.join(basepath, filename))

    profile = request.files["profile_give"]
    profile_extension = profile.filename.split('.')[-1]
    profilename = f'static/profile-{mytime}.{profile_extension}'
    profile.save(os.path.join(basepath, profilename))

    time = today.strftime('%Y-%m-%d')

    doc = {
        'file': filename,
        'profile': profilename,
        'title': title_receive,
        'content': content_receive,
        'time': time,
    }
    db.diary.insert_one(doc)

    return jsonify({'msg': 'Upload complete!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
