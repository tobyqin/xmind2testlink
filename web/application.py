import os
import sqlite3
from contextlib import closing
from datetime import datetime
from os.path import join, exists

from flask import Flask, request, redirect, url_for, send_from_directory, g
from werkzeug.utils import secure_filename

from src.xmind2testlink import convert_xmind

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = ['xmind']
DEBUG = True
DATABASE = './data.sqlite3'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    app.logger.info('request start...')
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    app.logger.info('request end...')
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = '{}_{}.xmind'.format(filename[:-6], datetime.now().strftime('%Y%m%d_%H%M%S'))
            upload_to = join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_to)
            convert_xmind(upload_to)
            return redirect(url_for('xmind_file', filename=filename))
        else:
            return "Please upload xmind file!"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/xmind/to/testlink/<filename>')
def xmind_file(filename):
    xml_name = filename[:-5] + 'xml'
    return send_from_directory(app.config['UPLOAD_FOLDER'], xml_name)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':

    if not exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    if not exists(DATABASE):
        init_db()

    app.run(debug=True)
