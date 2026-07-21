'''This is a prject start during () and ended (). it focuses on the lost proptery system at'''

# imports
from flask import Flask, render_template, request, flash, session, redirect
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# email stuff
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import hashlib
import auth


# Constants
DATABASE = 'lost_and_found.db'
ITEM_TYPE_LIST = [
    "BHS Beanie",
    "BHS Blazer",
    "BHS Cardigan",
    "BHS Jacket",
    "BHS Lavalava",
    "BHS Long-sleeved shirt",
    "BHS PE Shorts",
    "BHS PE Top",
    "BHS Scarf",
    "BHS Short-sleeved shirt",
    "BHS Shorts",
    "BHS Skirt",
    "BHS Sleveless vest",
    "BHS Socks",
    "BHS Tie",
    "BHS Tights",
    "BHS Tracksuit",
    "BHS Trousers",
    "BHS V-necked jersey",
    "Blazer",
    "Cap",
    "Cardigan",
    "Coat",
    "Dress",
    "Hair tie",
    "Hat",
    "Hoodie",
    "Jacket",
    "Jandals",
    "Jeans",
    "Jersey",
    "Long Skirt",
    "Long-sleeved Shirt",
    "Pants",
    "Scarf",
    "Shirt",
    "Shorts",
    "Skirt",
    "Socks",
    "T-Shirt",
    "Tank top",
    "Tie",
    "Tights"
]
COLOUR_LIST = [
    "BHS Uniform",
    "Red",
    "Orange",
    "Yellow",
    "Light Green",
    "Dark Green",
    "Light Blue",
    "Dark Blue",
    "Navy Blue",
    "Purple",
    "Pink",
    "Light Brown/Tan",
    "Dark Brown",
    "White",
    "Light Grey",
    "Dark Grey",
    "Black",
    "Cream",
    "Gold",
    "Silver"
]

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

    def get_id(self):
        return str(self.user_id)


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
    colours = db.relationship('Colour', secondary='lostitem_colour', backref='lost_items')


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

# testing routes
@login_required
@app.route('/test')
def test():
    results = User.query.all()
    print(current_user.school_code)
    for i in results:
        print(i.first_name)

    print('test')
    print(current_user.is_authenticated)
    print(session['clearance'])
    return render_template('test.html', title='test', example=results,)


@app.route('/add')
def add():
    add = User(first_name='Alex', last_name='Yao', password='heheheha', school_code='22177')
    db.session.add(add)
    db.session.commit()
    return 'added data successfully'


@app.route('/create')
def create():
    db.create_all()
    return 'donezo'


# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
# redirects users to login page if they need to login to access a page
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# routes
@app.context_processor
def inject_variables():
    '''This route injects these variable into every route'''
    return dict(show_footer=True,
                logged_in = current_user.is_authenticated)

# ensures that /, /index, and /home all lead to the same home page
@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    '''Flask route for the home page'''
    # prevent logged in users from accessing the page
    if current_user.is_authenticated:
        return redirect('/dashboard')
    
    return render_template('index.html',
                           title = 'Home',
                           )


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    '''
    Docstring for upload
    '''
    if session['clearance'] > 1:   # Clearance check
        # Users below clearance 1 cannot access this page
        return render_template('error.html',
                               title='Access Forbidon',
                               error_title='Forbiddon',
                               error_message='You do not have permission to access this page')
    
    if request.method == 'POST':
        finder_id = current_user.school_code
        item_type = request.form.get('item_type')
        item_colours = request.form.getlist('colours[]')
        time_found = request.form.get('time_found') or None
        size = request.form.get('size') or None
        nametag = request.form.get('nametag') or None
        status = 'LOST AND FOUND'
        notes = request.form.get('notes') or None

        # backend data check
        if item_type not in ITEM_TYPE_LIST:
            flash('Please provide a item type')
            return redirect('/upload')
        for colour in item_colours:
            if colour not in COLOUR_LIST:
                flash('Please provide valid colours')
                return redirect('/upload')
        if len(size) > 10 or len(nametag) > 20 or len(notes) > 67:
            flash('Please provide valid lengths for your inputs')
            return redirect('/upload')

        item = LostItem(finder_id=finder_id,
                       item_type=item_type,
                       time_found=time_found,
                       size=size,
                       nametag=nametag,
                       status=status,
                       notes=notes)
        
        for item_colour in item_colours:
            # checking if colour is valid
            colour = Colour.query.filter_by(name=item_colour).first()
            if colour:
                item.colours.append(colour)
        
        

        db.session.add(item)       
        db.session.commit()

        flash('Item uploaded successfully')
        
    return render_template('upload.html',
                           title='Upload',)


@app.route('/find', methods=['POST', 'GET'])
@login_required
def find():
    '''
    Docstring for find
    '''

    if request.method == 'POST':
        finder_id = current_user.school_code
        item_type = request.form.get('item_type')
        item_colours = request.form.getlist('colours[]')
        time_missing = request.form.get('time_found') or None
        size = request.form.get('size') or None
        nametag = request.form.get('nametag') or None
        status = 'LOOKING FOR'
        notes = request.form.get('notes') or None

        item = LostItem(finder_id=finder_id,
                       item_type=item_type,
                       time_found=time_missing,
                       size=size,
                       nametag=nametag,
                       status=status,
                       notes=notes)
        
        for item_colour in item_colours:
            colour = Colour.query.filter_by(name=item_colour).first()
            if colour:
                item.colours.append(colour)

        db.session.add(item)
        db.session.commit()

        flash('Request submitted successfully, a response may take a few days')

        return render_template('find.html',
                               title='Find')
    return render_template('find.html',
                           title='Find',)


@app.route('/about', methods=['POST', 'GET'])
def about():
    '''
    Docstring for about
    '''
    return render_template('about.html',
                           title='About',)


@app.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    return render_template('settings.html', title='Settings')


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    '''Route for the dashboard containing information for logged in users'''
    lost_items = LostItem.query.filter_by(finder_id=current_user.school_code, status='LOOKING FOR').all()
    lost_and_found_items = LostItem.query.filter_by(finder_id=current_user.school_code, status='LOST AND FOUND').all()
    print(current_user.is_authenticated)
    return render_template('dashboard.html',
                           title='Dashboard',
                           lost_items=lost_items,
                           lost_and_found_items=lost_and_found_items,
                           user_name = (f'{current_user.first_name} {current_user.last_name}'))


@app.route('/admin', methods=['POST', 'GET'])
@login_required
def admin():
    if session['clearance'] > 1:   # Clearance check
        # Users below clearance 1 cannot access this page
        return render_template('error.html',
                               title='Access Forbidon',
                               error_title='Forbiddon',
                               error_message='You do not have permission to access this page')
    
    lost_and_found_items = LostItem.query.filter_by(status='LOST AND FOUND').all()
    missing_items = LostItem.query.filter_by(status='LOOKING FOR').all()

    for item in lost_and_found_items:
        print(item.time_found)
    
    return render_template('admin.html', title='Admin',
                           lost_and_found_items=lost_and_found_items,
                           missing_items=missing_items)


@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item(item_id):
    if session['clearance'] > 1:   # Clearance check
    # If the user isnt an admin, they need to be the finder of the item
        if current_user.school_code != item.finder_id:
            return redirect('/404')

    item = LostItem.query.get_or_404(item_id)
    items = [item]
    # getting list of colours for preselecting colour options
    colour_names = [colour.name for colour in item.colours]

    if request.method == 'POST':
        item.item_type = request.form.get('item_type')
        item_colours = request.form.getlist('colours[]')
        item.time_found = request.form.get('time_found') or None
        item.size = request.form.get('size') or None
        item.nametag = request.form.get('nametag') or None
        item.status = request.form.get('item_status') or None
        item.notes = request.form.get('notes') or None

        item.colours.clear()
        for item_colour in item_colours:
            colour = Colour.query.filter_by(name=item_colour).first()
            if colour:
                item.colours.append(colour)

        db.session.commit()
        flash('Item updated successfully')
        return redirect(f'/item/{item_id}')

    return render_template('item.html', title='Edit Item', items=items, colour_names=colour_names)


@app.route('/item/<int:item_id>/delete', methods=['POST', 'GET'])
@login_required
def delete(item_id):
    item = LostItem.query.get_or_404(item_id)
    if session['clearance'] > 1:   # Clearance check
    # If the user isnt an admin, they need to be the finder of the item
        if current_user.school_code != item.finder_id:
            return redirect('/404')
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully')
    return redirect('/dashboard')


@app.route('/login', methods=['POST', 'GET'])
def login():
    '''Docstring for login'''
    # prevent logged in users from accessing the page
    if current_user.is_authenticated:
            return redirect('/dashboard')
    
    if request.method == 'POST':
        school_code = request.form.get('school_code')
        password = request.form.get('password')
        if school_code is None or password is None:
            flash('Please provide valid input')
            return redirect('/login')
        account = User.query.filter_by(school_code=school_code).first()
        if account is None:
            flash('School code is incorrect')
            return redirect('/login')
        if account.password == password:
            print('Successful login')
            login_user(account)
            flash('Successful login, welcome')
            session['clearance'] = account.clearance
            print(session['clearance'])
            return redirect('/dashboard')
        else:
            flash('Incorrect password, please try again')
            return redirect('/login')
    
    return render_template('login.html', title='Log in')


@app.route('/signup', methods=['POST', 'GET'])
def signup(): 
    '''
    This is the route that leads to the signup page. This page allows the
    user to sign up using a name, school code, and password.
    Assuming that the input requirements are met the user will be
    redirected to a page to enter a confirmation number that has been emailed to them.
    Only then will the account be successfully created.
    '''
    # prevent logged in users from accessing the page
    if current_user.is_authenticated:
            return redirect('/dashboard')
    
    if request.method == 'POST':
        first_name = request.form.get('first_name').strip()
        last_name = request.form.get('last_name').strip()
        school_code = request.form.get('school_code').strip()
        password = request.form.get('password').strip()

        # Checking that inputs are all valid
        # Checking there is no blank inputs
        if first_name is None or last_name is None or school_code is None or password is None:
            flash('Provide valid input')
            return redirect('/signup')
        # Checking length of names
        if len(first_name) <= 1 or len(last_name) <= 1:
            flash('Please provide a valid name')
            return redirect('/signup')
        # Checking there are no numbers in the names
        for letter in first_name:
            if letter.isnumeric():
                flash('Please provide a valid name length')
                return redirect('/signup')
        for letter in last_name:
            if letter.isnumeric():
                flash('Please provide a valid name length')
                return redirect('/signup')
        # Checking school code is valid
        if school_code is None:
            flash('Please provide a valid school code')
            return redirect('/signup')
        elif len(school_code) < 2:
            flash('Please provide a valid school code')
            return redirect('/signup')    
        # Checking password
        if password is None:
            flash('Please provide a valid school code')
            return redirect('/signup')
        elif len(password) < 6 or len(password) > 20:
            flash('Please provide a valid password length')
            return redirect('/signup')
        elif password.isalpha():
            flash("Your password must have a number or special character")
            return render_template("signup.html", title="Sign up")
        
        # Checking that this account doesn't already exist
        existing_users = User.query.filter_by(school_code=school_code).first()
        print(existing_users)
        if existing_users is not None:
            flash('This account already exists')
            return redirect('/signup')

        # Initilising variables for the senders email
        sender_email = auth.sender_email
        sender_email_password = auth.sender_email_password

        # storing the variables in the session to be used in the confirm route
        session['first_name'] = first_name
        session['last_name'] = last_name
        session['school_code'] = school_code
        session['password'] = password
        # generating random 6 digit confirmation code
        correct_number = random.randint(100000, 999999)
        session['correct_number'] = correct_number

        # generating email with random confirmation code
        message = MIMEMultipart()  # setting up email format
        message['From'] = auth.sender_email
        message['To'] = f'{school_code}{auth.domain_name}'
        print(f'{school_code}{auth.domain_name}')
        message['Subject'] = 'Lost and Found BHS confirmation code'
        body = f'Kia ora,\nHere is your confirmation code: {correct_number}'
        message.attach(MIMEText(body, 'plain'))

        # setting up gmail server, will close as soon as email is sent
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # starting server
            server.login(sender_email, sender_email_password)
            server.send_message(message)
            print(f'Email sent successfully to {school_code}@burnside.school.nz')

        flash('Enter the confirmation number')
        return redirect('/confirm')
    return render_template('signup.html', title='Sign Up')


@app.route('/logout')
def logout():
    '''This route logs out the user and redirects them to the home page'''
    logout_user()
    session.clear()
    print('User succseffully logged out')
    return redirect('/index')


@app.route('/confirm', methods=['POST', 'GET'])
def confirm():
    '''Confirmation email'''
    
    # getting variables from the session
    print('confirm route')
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    school_code = session.get('school_code')
    password = session.get('password')
    correct_number = session.get('correct_number')

    # prevents users from accessing the route if they are not making an account
    if school_code is None or correct_number is None:
        return render_template('error.html', title='Not allowed',
                               error_title="Oops, you must be lost",
                               error_message="404 page not found")

    if request.method == 'POST':
        confirmation_number = request.form.get('confirmation_number').strip()
        if confirmation_number is None or confirmation_number == '':
            flash('Please enter a valid confirmation number')
            return redirect('/confirm')
        print(confirmation_number)

        if int(confirmation_number )== correct_number:
            # Successful account creation
            add = User(first_name=first_name, last_name=last_name, password=password, school_code=school_code)
            db.session.add(add)
            db.session.commit()
            print(f'Account created successfully for {school_code}')
            flash('Account created successfully')
            session.clear()  # clears the variables
            # Logging in user after successful account creation
            account = User.query.filter_by(school_code=school_code).first()
            login_user(account)
            session['clearance'] = account.clearance
            return redirect('/dashboard')
        else:
            flash('Wrong confirmation number')
            return redirect('/confirm')
        


    return render_template('confirm.html',
                           title='Confirm',)


# error handlers
@app.errorhandler(404)
def page_not_found(e):
    '''
    Custom 404 page not found page
    '''
    return render_template("error.html",
                           title="Page Not Found",
                           error_title="Oops, you must be lost",
                           error_message="404 page not found"), 404


if __name__ == "__main__":
    app.run(debug=True)