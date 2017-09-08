from flask import Flask, request, render_template, flash, Markup, g
import sqlite3
from sklearn.metrics import accuracy_score, f1_score, log_loss, roc_auc_score
import os
app = Flask(__name__)

app.config.from_object(__name__)  # load config from this file , flaskr.py
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'conscience.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

passwords = {
    'marathas': 'caQUqXpe',
    'mauryans': '7NGgnVVL',
    'mughals': 'vx35pECH',
    'rajputs': 'pXqRcTyL',
    'veeras': 'aY95pBXR'
}

with open('labels1.txt') as f:
    content = f.readlines()
correctv1 = [int(x.strip()) for x in content]
with open('labels2.txt') as f:
    content = f.readlines()
correctv2 = [int(x.strip()) for x in content]
with open('labels3.txt') as f:
    content = f.readlines()
correctv3 = [int(x.strip()) for x in content]


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route('/', methods=['POST', 'GET'])
def result():
    cur = get_db().cursor()
    cur.execute('select * from entries')
    table = [[x["name"], x["acc11"], x["acc12"], x["acc21"], x["acc22"], x["acc31"], x["acc32"]] for x in cur.fetchall()]
    if request.method == 'POST':
        username = request.form['username']
        if username not in passwords.keys():
            return render_template("index.html", invaliduser=True, table=table)
        password = request.form['password']
        if password != passwords[username]:
            return render_template("index.html", invalidpassword=True, table=table)

        current = None
        index = -1
        i = 0
        for row in table:
            if row[0] == username:
                current = row
                index = i
            i += 1

        result = '<pre>'
        vector1 = []
        for line in request.files['file1'].stream:
            vector1.append(int(line))
        if len(vector1) != len(correctv1):
            return render_template("index.html", invalidfile1=True, table=table)
        acc1 = accuracy_score(correctv1, vector1)
        f11 = f1_score(correctv1, vector1, average='weighted')
        result += '\n\nQ1:\n\tAccuracy Score: ' + str(acc1) + '\n\tf1_score: ' + str(f11)

        vector21 = []
        for line in request.files['file21'].stream:
            vector21.append(int(line))
        if len(vector21) != len(correctv2):
            return render_template("index.html", invalidfile2=True, table=table)
        vector22 = []
        for line in request.files['file22'].stream:
            el = [float(x) for x in line.decode('utf-8').split(',')]
            if (len(el) != 3):
                return render_template("index.html", invalidfile2=True, table=table)
            vector22.append(el)
        if len(vector22) != len(correctv2):
            return render_template("index.html", invalidfile2=True, table=table)
        # print(f1_score(correctv2, vector21, average='weighted'))
        # print(log_loss(correctv2, vector22))
        f12 = f1_score(correctv2, vector21, average='weighted')
        log2 = log_loss(correctv2, vector22)
        result += '\n\nQ2:\n\tf1_score: ' + str(f12) + '\n\tlog_loss: ' + str(log2)

        vector31 = []
        for line in request.files['file31'].stream:
            vector31.append(int(line))
        if len(vector31) != len(correctv3):
            return render_template("index.html", invalidfile3=True, table=table)
        # f1_score
        vector32 = []
        x = 0
        for line in request.files['file32'].stream:
            if x < len(correctv3):
                vector32.append([float(x) for x in line.decode('utf-8').split(',')][correctv3[x]])
            x += 1
        if x != len(correctv3):
            return render_template("index.html", invalidfile3=True, table=table)

        # roc_auc
        f13 = f1_score(correctv3, vector31, average='weighted')
        roc3 = roc_auc_score(correctv3, vector32)
        result += '\n\nQ3:\n\tf1_score: ' + str(f13) + '\n\troc_auc: ' + str(roc3)
        result += '\n\n</pre>'
        print(result)

        if f11 > float(current[2]):
            table[index][1] = str(acc1)
            table[index][2] = str(f11)
            cur.execute('update entries set acc11 = ?, acc12 = ? where name = ?', (str(acc1), str(f11), username))
        if f12 > float(current[3]):
            table[index][3] = str(f12)
            table[index][4] = str(log2)
            cur.execute('update entries set acc21 = ?, acc22 = ? where name = ?', (str(f12), str(log2), username))
        if f13 > float(current[5]):
            table[index][5] = str(f13)
            table[index][6] = str(roc3)
            cur.execute('update entries set acc31 = ?, acc32 = ? where name = ?', (str(f13), str(roc3), username))


        return render_template("index.html", result=Markup(result), table=table)
    return render_template("index.html", table=table)

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.commit()
        g.sqlite_db.close()
