'''Docstring'''

# imports
from flask import Flask, render_template, request, flash, session, redirect
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


# Constants
DATABASE = 'lost_and_found.db'
# flask session stuff
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'secretkey'
Session(app)


# flask sqlalchemy testing stuff
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///lost_and_found.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# FlaskSQAlchemy tables
class User(db.Model, UserMixin):
    '''Database table containing the User information'''
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False) 
    school_code = db.Column(db.String(20), nullable=False, unique=True)
    clearance = db.Column(db.Integer, default=4)


class LostItem(db.Model):
    '''Database table containing the lost item information'''
    __tablename__ = 'lost_item'
    item_id = db.Column(db.Integer, primary_key=True)
    finder_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    item_type = db.Column(db.String(50))
    time_found = db.Column(db.String(50))
    size = db.Column(db.String(50))
    nametag = db.Column(db.String(50))
    status = db.Column(db.String(50))
    notes = db.Column(db.String(50))
    found_items = db.relationship('Colour', secondary='lostitem_colour', backref='finder')


class Colour(db.Model):
    '''Database table containing a list of colours'''
    __tablename__ = 'colour'
    colour_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


# table in the middle that links LostItem and Colour
lostitem_colour = db.Table(
    'lostitem_colour', 
    db.Column('iid', db.Integer, db.ForeignKey('lost_item.item_id')),
    db.Column('cid', db.Integer, db.ForeignKey('colour.colour_id'))
)


@app.route('/test')
def test():
    results = User.query.all()
    return render_template('test.html', title='test', example=results,)


@app.route('/add')
def add():
    add = User(first_name='Alex', last_name='Yao', password='heheheha', school_code='22177')
    db.session.add(add)
    db.session.commit()
    return 'added data'


@app.route('/create')
def create():
    db.create_all()
    return 'donezo'


# Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# routes
@app.context_processor
def inject_variables():
    '''This function injects these variable into every route'''
    return dict(show_footer=True)


# ensures that /, /index, and /home all lead to the same home page
@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    '''Flask route for the home page'''
    return render_template('index.html',
                           title = 'Home',
                           )


@app.route('/search', methods=['POST', 'GET'])
def search():
    '''
    Docstring for search
    '''
    return render_template('search.html',
                           title='Search',)


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    '''
    Docstring for upload
    '''
    return render_template('upload.html',
                           title='Upload',)


@app.route('/find', methods=['POST', 'GET'])
def find():
    '''
    Docstring for find
    '''
    return render_template('find.html',
                           title='Find',)


@app.route('/about', methods=['POST', 'GET'])
def about():
    '''
    Docstring for about
    '''
    return render_template('about.html',
                           title='About',)


@app.route('/login', methods=['POST', 'GET'])
def login():
    '''
    Docstring for login
    '''
    return render_template('login.html',
                           title='Login',)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    '''
    This is the route that leads to the signup page. This page allows the
    user to sign up using a username and password
    '''

    if request.method == 'POST':
        print('form done')
        first_name = request.form.get('username').rstrip()
        last_name = request.form.get('username').rstrip()
        school_code = request.form.get('school_code').rstrip()
        password = request.form.get('password').rstrip()
        print('password')
        # Checking there is no blank inputs
        if first_name is None or last_name is None or password is None:
            flash('Provide valid input')
            return render_template("signup.html",
                                   title="Sign Up")
        
        # Succesful account creation
        print('success')
        add = User(first_name=first_name, last_name=last_name, password=password, school_code=school_code)
        db.session.add(add)
        db.session.commit()
        
    print('route')    
    return render_template('signup.html',
                           title='Signup',)


# error handlers
@app.errorhandler(404)
def page_not_found(e):
    '''
    Custom 404 page not found page
    '''
    return render_template("404.html", title="Page Not Found"), 404


if __name__ == "__main__":
    app.run(debug=True)