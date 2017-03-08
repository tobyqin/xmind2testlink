import os
import sqlite3
from contextlib import closing
from datetime import datetime
from os.path import join, exists

from flask import Flask, request, send_from_directory, g, render_template
from flask import flash
from werkzeug.utils import secure_filename

from src.xmind2testlink import convert_xmind

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = ['xmind']
DEBUG = True
DATABASE = './data.sqlite3'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(32)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    download_xml = None
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_to = join(app.config['UPLOAD_FOLDER'], filename)

            if exists(upload_to):
                filename = '{}_{}.xmind'.format(filename[:-6], datetime.now().strftime('%Y%m%d_%H%M%S'))
                upload_to = join(app.config['UPLOAD_FOLDER'], filename)

            file.save(upload_to)
            convert_xmind(upload_to)
            download_xml = filename[:-5] + 'xml'
        else:
            flash("{} is not an xmind file!".format(file.filename))

    return render_template('index.html', download_xml=download_xml)


@app.route('/testlink/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':

    if not exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    if not exists(DATABASE):
        init_db()

    app.run(debug=True)
