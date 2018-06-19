import os
import sqlite3
from contextlib import closing
from os.path import join, exists

import arrow
from flask import Flask, request, send_from_directory, g, render_template, abort, redirect
from werkzeug.utils import secure_filename

from xmind2testlink.main import xmind_to_suite, xmind_to_testlink
from xmind2testlink.sharedparser import flat_suite

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = ['xmind']
DEBUG = True
DATABASE = './data.db3'
HOST = '0.0.0.0'
V2 = True

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


def init():
    if not exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    if not exists(DATABASE):
        init_db()


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
    now = str(arrow.now())
    sql = "INSERT INTO records (name,create_on,note) VALUES (?,?,?)"
    c.execute(sql, (xmind_name, now, str(note)))
    g.db.commit()


def delete_records(keep=20):
    """Clean up files on server and mark the record as deleted"""
    sql = "SELECT * from records where is_deleted<>1 ORDER BY id desc LIMIT -1 offset {}".format(keep)
    assert isinstance(g.db, sqlite3.Connection)
    c = g.db.cursor()
    c.execute(sql)
    rows = c.fetchall()
    for row in rows:
        name = row[1]
        xmind = join(app.config['UPLOAD_FOLDER'], name)
        xml = join(app.config['UPLOAD_FOLDER'], name[:-5] + 'xml')

        for f in [xmind, xml]:
            if exists(f):
                os.remove(f)

        sql = 'UPDATE records SET is_deleted=1 WHERE id = ?'
        c.execute(sql, (row[0],))
        g.db.commit()


def get_latest_record():
    found = list(get_records(1))
    if found:
        return found[0]


def get_records(limit=5):
    short_name_length = 50
    c = g.db.cursor()
    sql = "select * from records where is_deleted<>1 order by id desc limit {}".format(int(limit))
    c.execute(sql)
    rows = c.fetchall()

    for row in rows:
        name, short_name, create_on, note = row[1], row[1], row[2], row[3]

        # shorten the name for display
        if len(name) > short_name_length:
            short_name = name[:short_name_length] + '...'

        # more readable time format
        create_on = arrow.get(create_on).humanize()
        yield short_name, name, create_on, note


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_to = join(app.config['UPLOAD_FOLDER'], filename)

        if exists(upload_to):
            filename = '{}_{}.xmind'.format(filename[:-6], arrow.now().strftime('%Y%m%d_%H%M%S'))
            upload_to = join(app.config['UPLOAD_FOLDER'], filename)

        file.save(upload_to)
        insert_record(filename)
        g.is_success = True

    elif file.filename == '':
        g.is_success = False
        g.error = "Please select a file!"

    else:
        g.is_success = False
        g.invalid_files.append(file.filename)


def verify_uploaded_files(files):
    # download the xml directly if only 1 file uploaded
    if len(files) == 1 and getattr(g, 'is_success', False):
        g.download_xml = get_latest_record()[1]

    if g.invalid_files:
        g.error = "Invalid file: {}".format(','.join(g.invalid_files))


@app.route('/', methods=['GET', 'POST'])
def index(download_xml=None):
    g.invalid_files = []
    g.error = None
    g.download_xml = download_xml

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        save_file(file)
        verify_uploaded_files([file])
        delete_records()

    else:
        g.upload_form = True

    if V2:
        return render_template('v2/index.html', download_xml=g.download_xml, records=list(get_records()))
    else:
        return render_template('index.html', download_xml=g.download_xml, records=list(get_records()))


@app.route('/<filename>/to/testlink')
def download_file(filename):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)

    if not exists(full_path):
        abort(404)

    xmind_to_testlink(full_path)

    filename = filename[:-5] + 'xml'
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/preview/<filename>')
def preview_file(filename):
    full_path = join(app.config['UPLOAD_FOLDER'], filename)

    if not exists(full_path):
        abort(404)

    suite = xmind_to_suite(full_path)
    suite_count = len(suite.to_dict())
    suite = flat_suite(suite)

    return render_template('v2/preview.html', name=filename, suite=suite, suite_count=suite_count)


init()

if __name__ == '__main__':
    app.run(HOST, debug=DEBUG, port=5001)
