'''
This is a project start during 18/04/2026 and ended xx/08/2026.
This project focuses on the lost proptery system at BHS.
The goal of this project is to digitise the current lost property system.
'''

# imports
import hashlib
import random
from datetime import datetime
from threading import Thread

# Flask stuff
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

import auth
from flask_session import Session

# Constants
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
LOCATION_LIST = [
    'N/A',
    'A block',
    'B block',
    'C block',
    'D block',
    'D Extension',
    'E block',
    'G block',
    'H block',
    'K block',
    'Learning Centre',
    'M block',
    'N block',
    'P block',
    'R block',
    'X block',
    'Aurora Centre',
    'Green Room',
    'Library',
    'Office/Administration block',
    'Quad',
    'Cross Gym',
    'Hunter Gym',
    'Hall',
    'Upper Court',
    'Pool',
    'Upper Fields',
    'Lower Fields',
]

# Functions
def validate_item_data(item_type,
                       item_colours,
                       time_found,
                       size,
                       nametag,
                       location,
                       notes):
    '''
    Function to validate item changes so they align with certain parameters
    Inputs: item_type, item_colours, size, nametag, notes
    Outputs: is_valid, error_message
    '''
    if item_type not in ITEM_TYPE_LIST:
        return False, 'Please provide a item type'
    
    for colour in item_colours:
        if colour not in COLOUR_LIST:
            return False, 'Please provide valid colours'

    if time_found is not None:
        try:
            # formatting the time format so it can be compared properly
            time_found_formatted = datetime.strptime(time_found, "%Y-%m-%dT%H:%M")
            print(time_found_formatted)
        except:
            return False, "Please provide a valid date and time."

        if time_found_formatted > datetime.now():
            return False, "The date and time cannot be in the future."

    if location not in LOCATION_LIST:
        return False, 'Please provide a valid location'
    
    if size is not None and len(size) > 10:
        return False, 'Please provide valid lengths for your inputs'
    
    if nametag is not None and len(nametag) > 20:
        return False, 'Please provide valid lengths for your inputs'
    
    if notes is not None and len(notes) > 67:
        return False, 'Please provide valid lengths for your inputs'
    
    return True, None


def send_confirmation_email(app, recipient, confirmation_code):
    '''Function for sending the confirmation email'''
    with app.app_context():
        message = Message(
            subject="[Lost and Found BHS] Confirmation Code",
            recipients=[recipient]
        )

        message.body = (
            f"Kia ora,\n\n"
            f"Here is your confirmation code: {confirmation_code}\n\n"
            f"If you did not request to create this account, you can ignore this email."
        )
        mail.send(message)


def send_match_email(app, recipient, item_type):
    '''Function for sending the match item email'''
    with app.app_context():
        message = Message(
            subject="[Lost and Found BHS] Your item has been found",
            recipients=[recipient]
        )

        message.body = (
            f"Kia ora,\n\n"
            f"Your {item_type} has been found\n\n"
            f"Please visit the student office to pick up your item"
        )
        mail.send(message)


def send_more_info_email(app, recipient, item_type):
    '''Function for sending the more info needed email'''
    with app.app_context():
        message = Message(
            subject="[Lost and Found BHS] Requesting more information",
            recipients=[recipient]
        )

        message.body = (
            f"Kia ora,\n\n"
            f"Your {item_type} needs more information in order to be returned to you\n\n"
            f"Please update your note on the item or visit the student office"
        )
        mail.send(message)


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

# Email set up
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = auth.sender_email
app.config['MAIL_PASSWORD'] = auth.sender_email_password
app.config['MAIL_DEFAULT_SENDER'] = auth.sender_email

mail = Mail(app)

# FlaskSQAlchemy tables
class User(db.Model, UserMixin):
    '''Database table containing the User information'''
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False) 
    school_code = db.Column(db.String(20), nullable=False, unique=True)
    clearance = db.Column(db.Integer, default=2)

    # Change the default 'id' column to be called 'user_id'
    def get_id(self):
        return str(self.user_id)


class LostItem(db.Model):
    '''Database table containing the lost item information'''
    __tablename__ = 'lost_item'
    item_id = db.Column(db.Integer, primary_key=True)
    finder_id = db.Column(db.String(6), db.ForeignKey('user.user_id'))
    item_type = db.Column(db.String(50))
    time_found = db.Column(db.String(50))
    size = db.Column(db.String(50))
    nametag = db.Column(db.String(50))
    location = db.Column(db.String(50))
    status = db.Column(db.String(50))
    notes = db.Column(db.String(50))
    colours = db.relationship('Colour', secondary='lostitem_colour', backref='lost_items')


class Colour(db.Model):
    '''Database table containing a list of colours'''
    __tablename__ = 'colour'
    colour_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


# the linking table that links LostItem and Colour
lostitem_colour = db.Table(
    'lostitem_colour', 
    db.Column('iid', db.Integer, db.ForeignKey('lost_item.item_id')),
    db.Column('cid', db.Integer, db.ForeignKey('colour.colour_id'))
)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
# redirects users to login page if they need to login to access a page
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    '''User loader for Flask Login'''
    return User.query.get(int(user_id))


@app.context_processor
def inject_variables():
    '''This route injects these variable into every route'''
    return dict(show_footer=True,
                logged_in = current_user.is_authenticated,
                min_time = "2026-01-01T00:00",
                current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
                )


@app.before_request
def before_request():
    '''
    This route runs a check before every request to check if the account
    is disabled or not. If it is, they cannot access anything
    '''
    if request.endpoint in ['logout', 'static']:
        # User can still log out but is still denied from each route
        return
    
    if current_user.is_authenticated is True and current_user.clearance == 4:
        return render_template("error.html",
                                    title="Forbidden",
                                    error_title="Your account has been disabled",
                                    error_message="Please contact an admin")


# Beginning of Routes/Pages
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
    Route for the upload page where a user can upload a lost item that
    they have found
    '''
    if request.method == 'POST':
        finder_id = current_user.school_code
        item_type = request.form.get('item_type')
        item_colours = request.form.getlist('colours[]')
        time_found = request.form.get('time_found') or None
        size = request.form.get('size') or None
        nametag = request.form.get('nametag') or None
        location = request.form.get('location') or None
        status = 'LOST AND FOUND'
        notes = request.form.get('notes') or None

        # backend data check for item data
        is_valid, error_message = validate_item_data(item_type, item_colours, time_found, size, nametag, location, notes)
        if not is_valid:
            flash(error_message)
            return redirect('/upload')

        item = LostItem(finder_id=finder_id,
                       item_type=item_type,
                       time_found=time_found,
                       size=size,
                       nametag=nametag,
                       location=location,
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
    This is the page where users can submit an item that they have lost and
    await a response from an admin who can see that their item has been found
    '''

    if request.method == 'POST':
        finder_id = current_user.school_code
        item_type = request.form.get('item_type')
        item_colours = request.form.getlist('colours[]')
        time_missing = request.form.get('time_found') or None
        size = request.form.get('size') or None
        nametag = request.form.get('nametag') or None
        location = request.form.get('location') or None
        status = 'LOOKING FOR'
        notes = request.form.get('notes') or None

        # backend data check for item data
        is_valid, error_message = validate_item_data(item_type, item_colours, time_missing, size, nametag, location, notes)
        if not is_valid:
            flash(error_message)
            return redirect('/find')

        item = LostItem(finder_id=finder_id,
                       item_type=item_type,
                       time_found=time_missing,
                       size=size,
                       nametag=nametag,
                       location=location,
                       status=status,
                       notes=notes)

        # Adding colours one at a time
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


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    '''Route for the dashboard containing information for logged in users'''
    lost_items = LostItem.query.filter_by(finder_id=current_user.school_code,
                                          status='LOOKING FOR').all()
    lost_and_found_items = LostItem.query.filter_by(finder_id=current_user.school_code,
                                                    status='LOST AND FOUND').all()
    return render_template('dashboard.html',
                           title='Dashboard',
                           lost_items=lost_items,
                           lost_and_found_items=lost_and_found_items,
                           user_name = (f'{current_user.first_name} {current_user.last_name}'))


@app.route('/admin', methods=['POST', 'GET'])
@login_required
def admin():
    '''An admin panel for admins'''
    if current_user.clearance > 1:   # Clearance check, Admins only
        # Users below clearance 1 cannot access this page
        return render_template('error.html',
                               title='Access Forbidden',
                               error_title='Forbidden',
                               error_message='You do not have permission to access this page')

    lost_and_found_query = LostItem.query.filter_by(status='LOST AND FOUND')
    missing_items_query = LostItem.query.filter_by(status='LOOKING FOR')
    returned_items_query = LostItem.query.filter_by(status='RETURNED')
    recieved_items_query = LostItem.query.filter_by(status='RETURNED')

    if request.method == 'POST':
        finder_id = request.form.get('finder_id')
        item_type = request.form.get('item_type')
        colours = request.form.getlist('colours[]')
        location = request.form.get('location') or None

        # Applying the filters only if the filter has been applied
        if finder_id:  # Filtering by finder_id
            lost_and_found_query = lost_and_found_query.filter(
                LostItem.finder_id == finder_id
            )
            missing_items_query = missing_items_query.filter(
                LostItem.finder_id == finder_id
            )
            returned_items_query = returned_items_query.filter(
                LostItem.finder_id == finder_id
            )
            recieved_items_query = recieved_items_query.filter(
                LostItem.finder_id == finder_id
            )
        if item_type != 'None':  # Filtering by item type
            lost_and_found_query = lost_and_found_query.filter(
                LostItem.item_type == item_type
            )
            missing_items_query = missing_items_query.filter(
                LostItem.item_type == item_type
            )
            returned_items_query = returned_items_query.filter(
                LostItem.item_type == item_type
            )
            recieved_items_query = recieved_items_query.filter(
                LostItem.item_type == item_type
            )
        if colours:  # FIltering by colours
            lost_and_found_query = lost_and_found_query.filter(
                LostItem.colours.any(Colour.name.in_(colours))
            )
            missing_items_query = missing_items_query.filter(
                LostItem.colours.any(Colour.name.in_(colours))
            )
            returned_items_query = returned_items_query.filter(
                LostItem.colours.any(Colour.name.in_(colours))
            )
            recieved_items_query = recieved_items_query.filter(
                LostItem.colours.any(Colour.name.in_(colours))
            )
        if location != 'None':  # Filtering by location
            lost_and_found_query = lost_and_found_query.filter(
                LostItem.location == location
            )
            missing_items_query = missing_items_query.filter(
                LostItem.finder_id == finder_id
            )
            returned_items_query = returned_items_query.filter(
                LostItem.finder_id == finder_id
            )
            recieved_items_query = recieved_items_query.filter(
                LostItem.finder_id == finder_id
            )
            

    lost_and_found_items = lost_and_found_query.all()
    missing_items = missing_items_query.all()


    for item in lost_and_found_items + missing_items:
        item.colour_names = [colour.name for colour in item.colours]
    
    return render_template('admin.html', title='Admin',
                           lost_and_found_items=lost_and_found_items,
                           missing_items=missing_items)


@app.route('/item/<int:item_id>/match', methods=['POST', 'GET'])
@login_required
def match(item_id):
    '''
    Route that allows admins to press a button to match lost items with
    found items. This will send them to a page where they can check it against all of
    current lost and found items and then return them to the student
    '''
    if current_user.clearance > 1:   # Clearance check, Admins only
            # Users below clearance 1 cannot access this page
            return render_template('error.html',
                                   title='Access Forbidden',
                                   error_title='Forbidden',
                                   error_message='You do not have permission to access this page')
    
    current_item = LostItem.query.filter_by(item_id=item_id).first_or_404()
    if current_item.status != 'LOOKING FOR':
        abort(404)
    lost_and_found_items = LostItem.query.filter_by(status='LOST AND FOUND').all()
    return render_template('match.html',
                           title='Match',
                           current_item=current_item,
                           lost_and_found_items=lost_and_found_items,
                           item_id=item_id)


@app.route('/return_item/<int:looking_for_item_id>/<int:item_match_id>', methods=['POST', 'GET'])
@login_required
def return_item(looking_for_item_id, item_match_id):
    '''
    Route that allows admins to press a button to return lost items with
    found items. This will send a notification to the person with the lost item
    '''
    if current_user.clearance > 1:   # Clearance check, Admins only
            # Users below clearance 1 cannot access this page
            return render_template('error.html',
                                   title='Access Forbidden',
                                   error_title='Forbidden',
                                   error_message='You do not have permission to access this page')

    looking_for_item = LostItem.query.filter_by(item_id=looking_for_item_id).first_or_404()
    print(2)
    current_lost_item = LostItem.query.filter_by(item_id=item_match_id).first_or_404()
    print(current_lost_item.status)
    if current_lost_item.status != 'LOST AND FOUND':
        abort(404)
        print('3')

    if looking_for_item.status != 'LOOKING FOR':
        abort(404)
        print('4')
    looking_for_item.status = 'FOUND'
    current_lost_item.status = 'RETURNED'
    db.session.commit()

    # sending email
    recipient_school_code = looking_for_item.finder_id
    recipient_item_type = looking_for_item.item_type
    print(5)
    try:
        recipient = f"{recipient_school_code}{auth.domain_name}"
        # Sending the email in the background so redirect can occur immediatly
        Thread(
            target=send_match_email,
            args=(app, recipient, recipient_item_type),
            daemon=True
        ).start()
        print(f"Email sent successfully to {recipient}")
        flash(f'Email sent successfully to {recipient}')
    except Exception as e:
        # Captures the error pessage and prints it in terminal
        print(f"Failed to send email: {e}")
        flash("An error occured, please try again later.")
        return redirect('/admin')

    flash('Item successfully paired')
    return redirect('/admin')


@app.route('/request_info/<int:item_id>')
@login_required
def request_info(item_id):
    '''A route that allows admins to request more info about an item'''
    if current_user.clearance > 1:   # Clearance check, Admins only
            # Users below clearance 1 cannot access this page
            return render_template('error.html',
                                   title='Access Forbidden',
                                   error_title='Forbidden',
                                   error_message='You do not have permission to access this page')


    looking_for_item = LostItem.query.filter_by(item_id=item_id).first_or_404()

    if looking_for_item.status != 'LOOKING FOR':
        abort(404)
    # sending email
    school_code = looking_for_item.finder_id
    item_type = looking_for_item.item_type

    try:
        print('Sending email')
        recipient = f"{school_code}{auth.domain_name}"
        # Sending the email in the background so redirect can occur immediatly
        Thread(
            target=send_more_info_email,
            args=(app, recipient, item_type),
            daemon=True
        ).start()
        flash(f'Email sent succerssfully to {recipient}')
        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        # Captures the error pessage and prints it in terminal
        print(f"Failed to send email: {e}")
        flash("An error occured, please try again later.")
        return redirect('/dashboard')
        
    return redirect('/admin')


@app.route('/account_manager')
@login_required
def account_manager():
    '''
    Route that only admins can access and can manage all accounts.
    They will have the ability to promote and demote accounts
    '''
    if current_user.clearance > 1:   # Clearance check, Admins only
            # Users below clearance 1 cannot access this page
            return render_template('error.html',
                                   title='Access Forbidden',
                                   error_title='Forbiddon',
                                   error_message='You do not have permission to access this page')
    users = User.query.all()
    return render_template('account_manager.html',
                           title='Account Manager',
                           users=users)


@app.route('/promote/<int:user_id>')
@login_required
def promote(user_id):
    '''Route that can be used to promote someones clearance, admins only'''
    if current_user.clearance > 1:   # Clearance check, Admins only
            # Users below clearance 1 cannot access this page
            return render_template('error.html',
                                   title='Access Forbidden',
                                   error_title='Forbiddon',
                                   error_message='You do not have permission to access this page')

    account = User.query.filter_by(user_id=user_id).first_or_404()

    # Making sure admins can't be promote
    if account.clearance <= 1:
        flash('Admins cannot be promoted')
        return redirect('/account_manager')
    else:
        account.clearance -= 1
        db.session.commit()
        flash('User successfully promote')
        return redirect('/account_manager')


@app.route('/demote/<int:user_id>')
@login_required
def demote(user_id):
    '''Route that can be used to promote someones clearance, admins only'''
    if current_user.clearance > 1:   # Clearance check, Admins only
            # Users below clearance 1 cannot access this page
            return render_template('error.html',
                                   title='Access Forbidden',
                                   error_title='Forbiddon',
                                   error_message='You do not have permission to access this page')

    account = User.query.filter_by(user_id=user_id).first_or_404()

    # Making sure disabled accounts can't be demoted
    if account.clearance >= 4:
        flash('Admins cannot be promoted')
        return redirect('/account_manager')
    else:
        account.clearance += 1
        db.session.commit()
        flash('User successfully demoted')
        return redirect('/account_manager')


@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item(item_id):
    item = LostItem.query.get_or_404(item_id)

    if current_user.clearance > 1:   # Clearance check, Admin or Finder only
    # If the user isnt an admin, they need to be the finder of the item
        if current_user.school_code != str(item.finder_id):
            print('aborted')
            abort(404)

    items = [item]
    # getting list of colours for preselecting colour options
    colour_names = [colour.name for colour in item.colours]

    if request.method == 'POST':
        item.item_type = request.form.get('item_type')
        item_colours = request.form.getlist('colours[]')
        item.time_found = request.form.get('time_found') or None
        item.size = request.form.get('size') or None
        item.nametag = request.form.get('nametag') or None
        item.location = request.form.get('location') or None
        item.status = request.form.get('item_status') or None
        item.notes = request.form.get('notes') or None

        # backend data check for item data
        is_valid, error_message = validate_item_data(item.item_type,
                                                     item_colours,
                                                     item.time_found,
                                                     item.size,
                                                     item.nametag,
                                                     item.location,
                                                     item.notes)
        if not is_valid:
            flash(error_message)
            return redirect(f'/item/{item_id}')

        # Clearning original colours
        item.colours.clear()
        for item_colour in item_colours:
            colour = Colour.query.filter_by(name=item_colour).first()
            if colour:
                item.colours.append(colour)

        db.session.commit()
        flash('Item updated successfully')
        return redirect(f'/item/{item_id}')

    return render_template('item.html', title='Edit Item', items=items, colour_names=colour_names, item_id=item_id)


@app.route('/item/<int:item_id>/delete', methods=['POST', 'GET'])
@login_required
def delete(item_id):
    
    item = LostItem.query.get_or_404(item_id)
    print('test')
    print(item)
    if current_user.clearance > 1:   # Clearance check
    # If the user isnt an admin, they need to be the finder of the item
        if current_user.school_code != item.finder_id:
            abort(404)
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
        inputted_password = request.form.get('password')

        # Backend input checks
        if school_code is None or inputted_password is None:
            flash('Please provide valid input')
            return redirect('/login')
        account = User.query.filter_by(school_code=school_code).first()
        if account is None:
            flash('School code is incorrect')
            return redirect('/login')

        # Hashing the inputted password and comparing the hashes
        h = hashlib.new('SHA256')
        h.update(inputted_password.encode())
        hashed_inputted_password = h.hexdigest()
        if account.password == hashed_inputted_password:
            print('Successful login')
            login_user(account)
            flash('Successful login, welcome')
            session['clearance'] = account.clearance
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
        if len(first_name) < 1 or len(last_name) < 1:
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
        elif len(school_code) < 2 or len(school_code) > 5:
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

        # Store the variables in the session to be used in the confirm route
        session['first_name'] = first_name
        session['last_name'] = last_name
        session['school_code'] = school_code
        session['password'] = password

        # Generate random 6 digit confirmation code
        correct_number = random.randint(100000, 999999)
        session['correct_number'] = correct_number

        try:
            recipient = f"{school_code}{auth.domain_name}"
            # Sending the email in the background so redirect can occur immediatly
            Thread(
                target=send_confirmation_email,
                args=(app, recipient, correct_number),
                daemon=True
            ).start()
            print(f"Email sent successfully to {recipient}")
        except Exception as e:
            # Captures the error pessage and prints it in terminal
            print(f"Failed to send email: {e}")
            flash("An error occured, please try again later.")
            return redirect('/signup')

        flash('Enter the confirmation number')
        return redirect('/confirm')
    return render_template('signup.html', title='Sign Up')


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

        if int(confirmation_number) == correct_number:
            # Successful account creation
            # Hashing the password
            h = hashlib.new('SHA256')
            h.update(password.encode())
            hashed_password = h.hexdigest()

            # Adding the account into the database
            add = User(first_name=first_name,
                       last_name=last_name,
                       password=hashed_password,
                       school_code=school_code)
            db.session.add(add)
            db.session.commit()

            print(f'Account created successfully for {school_code}')
            session.clear()  # clears the variables
            # Logging in user after successful account creation
            account = User.query.filter_by(school_code=school_code).first()
            login_user(account)
            session['clearance'] = account.clearance
            # Clearing session variables
            session.pop('first_name', None)
            session.pop('last_name', None)
            session.pop('school_code', None)
            session.pop('password', None)
            session.pop('correct_number', None)
            flash('Account created successfully')
            return redirect('/dashboard')
        else:
            flash('Wrong confirmation number')
            return redirect('/confirm')
        


    return render_template('confirm.html',
                           title='Confirm',)


@app.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    '''Route for settings. Users can cahnge their password and delete their accounts here'''
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        current_hashed_password = current_user.password
        print(current_hashed_password)

        # Checking if the old passwords match
        # Hashing old password to compare the hashes to the current password
        h = hashlib.new("SHA256")
        h.update(old_password.encode())
        old_hashed_password = h.hexdigest()

        # checking that the hashed passwords match
        if old_hashed_password != current_hashed_password:
            flash('Incorrect password')
            return redirect('/settings')

        # Checking the new password is valid
        if new_password is None:
            flash('Please provide a valid school code')
            return redirect('/settings')
        elif len(new_password) < 6 or len(new_password) > 20:
            flash('Please provide a valid password length')
            return redirect('/settings')
        elif new_password.isalpha():
            flash("Your password must have a number or special character")
            return redirect('/settings')
        else:  # The password is valid
            # Hashing the new password
            h = hashlib.new("SHA256")
            h.update(new_password.encode())
            new_hashed_password = h.hexdigest()
            account = User.query.filter_by(school_code=current_user.school_code).first_or_404()
            account.password = new_hashed_password
            db.session.commit()
            print('Password Successfully Updated')
            flash('Password Successfully Updated')

        
    return render_template('settings.html', title='Settings')


@app.route('/delete_account', methods=['POST', 'GET'])
@login_required
def delete_account():
    if request.method == 'POST':
        inputted_password = request.form.get('password')
        checkbox = request.form.get('delete_account_checkbox')
        # Checking for invalid password input
        if inputted_password is None or inputted_password == '':
            flash('Please check the checkbox and input your password to proceed')
            return redirect('/delete_account')
        # Checking if check box is checked
        if checkbox != 'Checked':
            flash('Please check the checkbox and input your password to proceed')
            return redirect('/delete_account')
        
        # Checking if password is correct
        # Hashing inputted password
        h = hashlib.new("SHA256")
        h.update(inputted_password.encode())
        hashed_inputted_password = h.hexdigest()
        if hashed_inputted_password == current_user.password:
            print(f'Deleting the account of {current_user.school_code}')
            account = User.query.filter_by(school_code=current_user.school_code).first_or_404()
            # Delete all lost items and their colours associated with the user
            lost_items = LostItem.query.filter_by(finder_id=account.user_id).all()
            for item in lost_items:
                item.colours.clear()
                db.session.delete(item)

            logout_user()
            session.clear()
            db.session.delete(account)
            db.session.commit()

            flash("Your account has been deleted")
            return redirect('/home')
        else:  # incorrect password
            flash('Incorrect password')
            return redirect('/delete_account')


    return render_template('delete_account.html', title='Delete Account')


@app.route('/about', methods=['POST', 'GET'])
def about():
    '''
    Route for about page. Page contains general information about the site
    '''
    return render_template('about.html',
                           title='About',)


@app.route('/logout')
def logout():
    '''This route logs out the user and redirects them to the home page'''
    logout_user()
    session.clear()
    print('User successfully logged out')
    return redirect('/index')


# error handlers
@app.errorhandler(404)
def page_not_found(e):
    '''
    Custom 404 page not found page
    '''
    print(e)
    return render_template("error.html",
                           title="Page Not Found",
                           error_title="Oops, you must be lost",
                           error_message="404 page not found"), 404


if __name__ == "__main__":
    app.run(debug=True)
