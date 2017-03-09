import os
import sqlite3
from contextlib import closing
from datetime import datetime
from os.path import join, exists

from flask import Flask, request, send_from_directory, g, render_template
from flask import flash
from werkzeug.utils import secure_filename
from xmind2testlink.main import xmind_to_testlink

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = ['xmind']
DEBUG = True
DATABASE = './data.db3'

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


def insert_record(xmind_name, note=''):
    c = g.db.cursor()
    now = str(datetime.now())
    sql = "insert into records (name,create_on,note) VALUES (?,?,?)"
    c.execute(sql, (xmind_name, now, str(note)))
    g.db.commit()


def get_records(limit=10):
    c = g.db.cursor()
    sql = "select * from records order by id desc limit {}}".format(int(limit))
    c.execute(sql)
    return c.fetchall()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index(download_xml=None):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_to = join(app.config['UPLOAD_FOLDER'], filename)

            if exists(upload_to):
                filename = '{}_{}.xmind'.format(filename[:-6], datetime.now().strftime('%Y%m%d_%H%M%S'))
                upload_to = join(app.config['UPLOAD_FOLDER'], filename)

            file.save(upload_to)
            xmind_to_testlink(upload_to)
            insert_record(filename)
            download_xml = filename[:-5] + 'xml'
            flash('Success!')
        else:
            flash("<b>{}</b> is not an xmind file!".format(file.filename))

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
