import MySQLdb
from flask import *
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from csv import writer

# from model import *
app = Flask(__name__, template_folder="template", static_url_path='/static')

app.secret_key = 'abcdef ghijkl mnopqr stuvw xyz'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Value@2015'
app.config['MYSQL_DB'] = 'MovieSpy'

mysql = MySQL(app)

test = pd.read_csv('FINAL_MOVIE_TABLE.csv')



def create_sim():
    test = pd.read_csv('FINAL_MOVIE_TABLE.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(test['comb'])
    sim = cosine_similarity(count_matrix)
    return test, sim

def rcmd(m):
    m = m.lower()
    try:
        test.head()
    except:
        test, sim = create_sim()
    if m not in test['movie_title'].unique():
        print('Sorry! This movie is not in our database. Please check the spelling or try with some other
movies')
        return render_template('userportal.html')
    else:
# getting the index of the movie in the dataframe
        i = test.loc[test['movie_title'] == m].index[0]

# fetching the row containing similarity scores of the movie
# from similarity matrix and enumerate it
        lst = list(enumerate(sim[i]))



# sorting this list in decreasing order based on the similarity score
        lst = sorted(lst, key=lambda x: x[1], reverse=True)

# taking top 1- movie scores
# not taking the first index since it is the same movie
lst = lst[1:11]
# making an empty list that will containg all 10 movie recommendations
l = []
for i in range(len(lst)):
a = lst[i][0]
l.append(test['movie_title'][a])
return l

def searchHelper(year, name):
name = name.lower()
test1 = pd.read_csv('FINAL_MOVIE_TABLE.csv')
t = test1.loc[(test1['year'] == year)]

t1 = t.loc[(t['director_name'] == name)]

l = t1['movie_title'].tolist()
return l



def csvToSQL():
data = pd.read_csv('FINAL_MOVIE_TABLE.csv')
df = pd.DataFrame(data, columns=['year', 'director_name', 'actor_1_name', 'actor_2_name',
'actor_3_name', 'genres',
'movie_title', 'comb'])
curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
for row in df.itertuples():
curr.execute("INSERT INTO movie VALUES(%s, %s, %s, %s, %s, %s, %s, %d)", (
row.director_name, row.actor_1_name, row.actor_2_name, row.actor_3_name, row.genres,
row.movie_title,
row.comb,
int(row.year)))
curr.commit()

@app.route('/', methods={'GET', 'POST'})
def home():
return render_template('homepage.html')

@app.route('/userportal')
def userportal():
if 'loggedin' in session:


return render_template('userportal.html')
else:
return redirect(url_for('user'))

@app.route('/user', methods={'GET', 'POST'})
def user():
msg = ''
if request.method == 'POST' and 'user_id' in request.form and 'upwd' in request.form:
uid = request.form['user_id']
pwd = request.form['upwd']
# Now, check if account exists in database
curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
curr.execute("SELECT * FROM user where user_id = %s and upwd = %s", (uid, pwd,))
account = curr.fetchone()
if account:
session['loggedin'] = True
session['id'] = account['user_id']
session['password'] = account['upwd']
return redirect(url_for('userportal'))
else:
msg = 'Incorrect User_id/Password..!!!'
# flash(u'Incorrect User_id/Password..!!!', 'error')
return render_template('userLogIn.html', msg=msg)


@app.route('/user', methods={'GET', 'POST'})
@app.route('/user/register', methods={'GET', 'POST'})
def register():
msg = ''
if request.method == "POST" and 'user_id' in request.form and 'upwd' in request.form and 'ucnfrmpwd'
in request.form:
id = request.form['user_id']
pwd = request.form['upwd']
cpwd = request.form['ucnfrmpwd']
curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
curr.execute("SELECT * FROM user where user_id = %s and upwd = %s", (id, pwd,))
account = curr.fetchone()
if account:
msg = "Account Already Exist"
elif pwd != cpwd:
msg = "Password doesn't match..!!!"
else:
curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
curr.execute("INSERT INTO USER(user_id,upwd) VALUES (%s,%s) ", (id, pwd,))
mysql.connection.commit()
return redirect(url_for('user'))
return render_template('userRegister.html', msg=msg)


@app.route('/admin', methods={'GET', 'POST'})
def admin():
msg = ''
if request.method == 'POST' and 'admin_id' in request.form and 'apwd' in request.form:
id = request.form['admin_id']
pwd = request.form['apwd']
curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
curr.execute("SELECT * FROM admin WHERE admin_id = %s and apwd = %s", (id, pwd,))
account = curr.fetchone()
if account:
session['loggedin'] = True
session['id'] = account['admin_id']
session['password'] = account['apwd']
return redirect(url_for('userportal'))
else:
msg = 'Incorrect Admin Id/Password..!!!'
flash(msg, category="error")
return render_template('adminLogIn.html', msg=msg)

@app.route('/admin', methods={'GET', 'POST'})
@app.route('/admin/register', methods={'GET', 'POST'})
def adminRegister():



msg = ''
if request.method == "POST" and "admin_id" in request.form and "apwd" in request.form and
"acnfrmpwd" in request.form and "key" in request.form:
id = request.form['admin_id']
pwd = request.form['apwd']
cpwd = request.form['acnfrmpwd']
akey = request.form['key']
curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
curr.execute("SELECT * FROM admin WHERE admin_id = %s and apwd = %s", (id, pwd,))
account = curr.fetchone()
if account:
msg = "Account Already Exist..!!!"
elif pwd != cpwd:
msg = "Password doesn't match..!!!"
elif akey != "12345abc":
msg = "Incorrect Confirmation Key..!!!"
else:
curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
curr.execute("INSERT INTO admin(admin_id,apwd) VALUES (%s,%s) ", (id, pwd,))
mysql.connection.commit()
return redirect(url_for('admin'))
return render_template('adminRegister.html', msg=msg)

@app.route('/<person>')



def access(person):
if person == 'User':
return redirect(url_for('user'))
else:
return redirect(url_for('admin'))

@app.route('/addmovie', methods={'GET', 'POST'})
def addMovie():
if request.method == 'POST' and 'title' in request.form:
movie = request.form['title']
y = request.form['year']
gen = request.form['genre']
dirc = request.form['director']
act1 = request.form['actor_1']
act2 = request.form['actor_2']
act3 = request.form['actor_3']
year = int(y)
comb = act1 + " " + act2 + " " + act3 + " " + dirc + " " + gen + " "
test, sim = create_sim()
test.loc[len(test.index)] = [year, dirc, act1, act2, act3, gen, movie, comb]
test, sim = create_sim()
test.to_csv('FINAL_MOVIE_TABLE.csv',index=False)
return render_template('addmovie.html')

@app.route('/recommend', methods={'GET', 'POST'})
def recommend():
if request.method == 'POST':
if request.form['action'] == 'get' and 'movie_title' in request.form:
m = request.form['movie_title']
if len(m) != 0:
return redirect(url_for('predict', movie=m))
# else:
# flash message for incorrect movie input
elif request.form['action'] == 'add':
return redirect(url_for('addMovie'))
elif request.form['action'] == 'portal':
return redirect(url_for('userportal'))
return render_template('recommendation.html')

@app.route('/search', methods={'GET', 'POST'})
def search():
if request.method == 'POST':
if 'year' in request.form and 'director' in request.form:
year = request.form['year']
dir = request.form['director']
return redirect(url_for('searched_movies', y=year, d=dir))
return render_template('search.html')

@app.route('/search')
@app.route('/search/searched_movies/<y>/<d>')
def searched_movies(y, d):
r = list()
year = int(y)
r = searchHelper(year, d)
d = d.upper()
return render_template('searched_movies.html', year=year, name=d, lst=r)

@app.route('/recommend')
@app.route('/recommend/predict/<movie>')
def predict(movie):
r = list()
r = rcmd(movie)
movie = movie.upper()
return render_template('predict.html', movie=movie, r=r)

if __name__ == '__main__':
app.run(debug=True)